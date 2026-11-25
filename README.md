# ash's F-Droid repo

F-Droid repository for my apps, built with [fdroidserver](https://f-droid.org/docs/Setup_an_F-Droid_App_Repo/)
and published to GitHub Pages. APKs come from each app's GitHub Releases.

**Repo URL:** https://ashleyiscookin.github.io/fdroid/repo

Add it in Neo Store (or any F-Droid client) by opening
https://ashleyiscookin.github.io/fdroid/repo on your phone and tapping the link or scanning the QR code there.

## How it works

- `apps.yml` lists the source repos. Add an entry and push; the workflow does the rest.
- `.github/workflows/publish.yml` runs on push, daily, and on demand (Actions → Publish F-Droid repo → Run workflow).
  It downloads the APKs, builds and signs the index with `fdroid update`, and deploys to Pages.
- Nothing generated is committed. The signing key lives only in Actions secrets.

## Secrets

| Secret | What |
| --- | --- |
| `FDROID_KEYSTORE` | base64 of the PKCS12 repo signing keystore (alias `fdroid`) |
| `FDROID_KEYSTORE_PASS` | its password |
| `SOURCE_TOKEN` | optional, fine-grained PAT with read-only *Contents* on private source repos |

Keep an offline backup of the keystore. If it's lost, every user has to remove and re-add the repo.
