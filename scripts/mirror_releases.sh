#!/bin/sh
# Mirror the newest APK release of each private app repo into a release of
# ashleyiscookin/fdroid (public), then trigger the publish workflow.
# Needs gh logged in with read access to the source repos. Idempotent.
set -e
DEST=ashleyiscookin/fdroid
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
new=0
# name  source-repo  asset-glob  include-prereleases
while read -r name src pat pre; do
  [ -z "$name" ] && continue
  if [ "$pre" = yes ]; then
    tag=$(gh release list -R "$src" -L 1 --json tagName --jq '.[0].tagName')
  else
    tag=$(gh release list -R "$src" -L 20 --exclude-pre-releases --json tagName --jq '.[0].tagName')
  fi
  [ -z "$tag" ] && { echo "$src: no release"; continue; }
  rm -rf "$W/$name"; gh release download "$tag" -R "$src" -p "$pat" -D "$W/$name"
  f=$(ls "$W/$name"/*.apk | head -1)
  sum=$(sha256sum "$f" | cut -c1-12)
  rtag="$name-$tag-$sum"   # sum in tag: rolling tags like "latest" still produce new mirrors
  if gh release view "$rtag" -R "$DEST" >/dev/null 2>&1; then echo "$rtag: up to date"; continue; fi
  gh release create "$rtag" "$f" -R "$DEST" --title "$name $tag" --notes "Mirror of $src release $tag" >/dev/null
  echo "$rtag: mirrored"; new=1
done <<LIST
parla ashleyiscookin/parla parla-*.apk no
kleinanzeigen-alarm ashleyiscookin/kleinanzeigen-alarm kleinanzeigen-alarm-*.apk no
raope ashleyiscookin/jiggolo raope.apk yes
LIST
[ "$new" = 1 ] && gh workflow run publish.yml -R "$DEST" && echo "publish triggered"
exit 0
