#!/usr/bin/env python3
"""Download the APKs listed in apps.yml from GitHub Releases into repo/.

Token: GITHUB_TOKEN for this repo's own releases (mirrors), SOURCE_TOKEN for
other repos (needed when they are private), falling back to GITHUB_TOKEN.
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

import yaml

API = "https://api.github.com"
OWN_REPO = os.environ.get("GITHUB_REPOSITORY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
SOURCE_TOKEN = os.environ.get("SOURCE_TOKEN")


def token_for(repo):
    if repo == OWN_REPO:
        return GITHUB_TOKEN
    return SOURCE_TOKEN or GITHUB_TOKEN


def request(url, token, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, headers={"Accept": accept, "X-GitHub-Api-Version": "2022-11-28"})
    if token:
        req.add_unredirected_header("Authorization", f"Bearer {token}")
    return urllib.request.urlopen(req, timeout=120)


def main():
    root = Path(__file__).resolve().parent.parent
    apps = (yaml.safe_load((root / "apps.yml").read_text()) or {}).get("apps") or []
    out = root / "repo"
    out.mkdir(exist_ok=True)
    failed = False

    for app in apps:
        repo = app["repo"]
        pattern = re.compile(app.get("asset", r"\.apk$"))
        keep = int(app.get("keep", 1))
        token = token_for(repo)
        try:
            with request(f"{API}/repos/{repo}/releases?per_page=30", token) as r:
                releases = json.load(r)
        except Exception as e:
            print(f"::error::{repo}: cannot list releases: {e}")
            failed = True
            continue

        releases = [
            rel for rel in releases
            if not rel["draft"] and (app.get("prerelease") or not rel["prerelease"])
        ]
        taken = 0
        for rel in releases:
            assets = [a for a in rel["assets"] if pattern.search(a["name"])]
            if not assets:
                continue
            for a in assets:
                safe = re.sub(r"[^A-Za-z0-9._-]", "_", f"{repo}_{rel['tag_name']}_{a['name']}")
                dest = out / safe
                print(f"{repo} {rel['tag_name']}: {a['name']}")
                with request(a["url"], token, accept="application/octet-stream") as r:
                    dest.write_bytes(r.read())
            taken += 1
            if taken >= keep:
                break
        if taken == 0:
            print(f"::warning::{repo}: no release with an asset matching {pattern.pattern}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
