#!/usr/bin/env bash
# Publish (or replace) the Android preview APK on a FIXED GitHub Release tag.
# Download URL never changes — overwrite the asset in place on every build.
#
# Stable URLs (both receive every build):
#   https://github.com/iumer/Hadith/releases/download/android-preview/HeartThreads-preview.apk
#   https://github.com/iumer/Hadith/releases/download/android-preview-2026-10-22/HeartThreads-preview.apk
#
# Usage:
#   ./scripts/publish_android_apk.sh [/path/to/app-release.apk]
#
# Auth: GITHUB_TOKEN, GH_TOKEN, or token in `git remote get-url origin`.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="iumer/Hadith"
# Testers have both links, so every build replaces the APK on both releases.
TAG="${TAG:-android-preview}"
ASSET_NAME="HeartThreads-preview.apk"
APK="${1:-}"
STABLE_URL="https://github.com/${REPO}/releases/download/${TAG}/${ASSET_NAME}"

if [[ -z "$APK" ]]; then
  for candidate in \
    "/opt/cursor/artifacts/HeartThreads-preview.apk" \
    "$ROOT/app/android/app/build/outputs/apk/release/app-release.apk"
  do
    if [[ -f "$candidate" ]]; then
      APK="$candidate"
      break
    fi
  done
fi

if [[ -z "${APK}" || ! -f "$APK" ]]; then
  echo "APK not found. Pass path: $0 /path/to/app-release.apk" >&2
  exit 1
fi

# Prefer token from git remote (Cursor cloud). Env GITHUB_TOKEN is often wrong-scoped here.
TOKEN="$(git -C "$ROOT" remote get-url origin 2>/dev/null | sed -n 's|https://x-access-token:\([^@]*\)@github.com/.*|\1|p' || true)"
TOKEN="${TOKEN:-${GITHUB_TOKEN:-${GH_TOKEN:-}}}"
if [[ -z "$TOKEN" ]]; then
  echo "No GitHub token. Set GITHUB_TOKEN or use an authenticated origin remote." >&2
  exit 1
fi

API="https://api.github.com/repos/${REPO}"
HDR=(-H "Authorization: Bearer ${TOKEN}" -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28")

echo "Publishing $(basename "$APK") ($(du -h "$APK" | cut -f1)) → tag '${TAG}'"

REL_JSON="$(curl -sS "${HDR[@]}" "${API}/releases/tags/${TAG}" || true)"
REL_ID="$(printf '%s' "$REL_JSON" | python3 -c 'import sys,json
d=json.load(sys.stdin)
print(d["id"] if isinstance(d,dict) and "id" in d else "")' 2>/dev/null || true)"

if [[ -z "$REL_ID" ]]; then
  echo "Creating release ${TAG} …"
  BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD)"
  BODY="Stable Android preview APK. **Same download URL for every build** — new builds replace the file in place.

${STABLE_URL}

Publish with: \`./scripts/publish_android_apk.sh\`"
  REL_JSON="$(curl -sS -X POST "${HDR[@]}" "${API}/releases" \
    --data-binary @- <<EOF
{"tag_name":"${TAG}","name":"Heart Threads — Android preview (stable download)","body":$(python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' <<<"$BODY"),"draft":false,"prerelease":true,"target_commitish":"${BRANCH}"}
EOF
)"
  REL_ID="$(printf '%s' "$REL_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')"
fi

UPLOAD_URL="$(printf '%s' "$REL_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["upload_url"].split("{")[0])')"

ASSETS="$(curl -sS "${HDR[@]}" "${API}/releases/${REL_ID}/assets")"
while read -r ASSET_ID; do
  [[ -z "$ASSET_ID" ]] && continue
  echo "Removing previous asset id=${ASSET_ID}"
  curl -sS -X DELETE "${HDR[@]}" "${API}/releases/assets/${ASSET_ID}" >/dev/null
done < <(printf '%s' "$ASSETS" | python3 -c "import sys,json; print('\\n'.join(str(a['id']) for a in json.load(sys.stdin) if a.get('name')=='${ASSET_NAME}'))")

echo "Uploading ${ASSET_NAME} …"
RESP="$(curl -sS -X POST "${HDR[@]}" \
  -H "Content-Type: application/vnd.android.package-archive" \
  --data-binary @"${APK}" \
  "${UPLOAD_URL}?name=${ASSET_NAME}")"

URL="$(printf '%s' "$RESP" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("browser_download_url",""))')"
if [[ -z "$URL" ]]; then
  echo "Upload failed:" >&2
  echo "$RESP" >&2
  exit 1
fi

echo "OK — stable download URL (never changes; file is replaced in place):"
echo "${STABLE_URL}"

# Also refresh the older dated release that some testers were given.
if [[ "$TAG" == "android-preview" ]]; then
  TAG="android-preview-2026-10-22" "$0" "$APK"
fi
