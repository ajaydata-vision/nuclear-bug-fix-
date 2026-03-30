#!/usr/bin/env bash
# nuclear-bug-fix updater
# Invoked by: /nuclear-bug-fix update  OR  bash ~/.claude/skills/nuclear-bug-fix/scripts/update.sh

set -euo pipefail

REPO_OWNER="ajaydata-vision"
REPO_NAME="nuclear-bug-fix-"
SKILL_NAME="nuclear-bug-fix"
SKILLS_DIR="${HOME}/.claude/skills/${SKILL_NAME}"
SKILL_MD="${SKILLS_DIR}/SKILL.md"
DEFAULT_ARTIFACT="dist/${SKILL_NAME}.skill"
RELEASE_URL="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/dist/release.json"
COMPARE_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/compare"

read_skill_metadata_field() {
  local file="$1"
  local field="$2"
  grep -E "^\s+${field}:" "$file" 2>/dev/null \
    | head -1 | awk '{print $2}' | tr -d '"' | tr -d "'"
}

# ── 1. Read installed version from metadata block in SKILL.md ────────────────
# Check personal install first, then project install
installed_version=""
installed_source_commit=""
PROJECT_SKILL_MD=".claude/skills/${SKILL_NAME}/SKILL.md"
if [[ -f "$SKILL_MD" ]]; then
  installed_version=$(read_skill_metadata_field "$SKILL_MD" "version")
  installed_source_commit=$(read_skill_metadata_field "$SKILL_MD" "source_commit")
elif [[ -f "$PROJECT_SKILL_MD" ]]; then
  installed_version=$(read_skill_metadata_field "$PROJECT_SKILL_MD" "version")
  installed_source_commit=$(read_skill_metadata_field "$PROJECT_SKILL_MD" "source_commit")
fi

[[ -z "$installed_version" ]] && installed_version="unknown"
[[ -z "$installed_source_commit" ]] && installed_source_commit="unknown"

echo "nuclear-bug-fix updater"
echo "  Installed : ${installed_version}"

# ── 2. Fetch latest released version from GitHub ─────────────────────────────
echo "  Checking  : GitHub release manifest..."

release_response=$(curl -sf \
  -H "Accept: application/json" \
  "${RELEASE_URL}") || {
  echo ""
  echo "❌ Could not fetch dist/release.json from GitHub."
  echo "   Manual install:"
  echo "     curl -L https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/${DEFAULT_ARTIFACT} -o /tmp/${SKILL_NAME}.skill"
  echo "     claude skills add /tmp/${SKILL_NAME}.skill --force"
  exit 1
}

if ! command -v python3 &>/dev/null; then
  echo "❌ python3 is required to parse dist/release.json but was not found in PATH."
  echo "   Install python3 or use the manual install command:"
  echo "     curl -L https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/${DEFAULT_ARTIFACT} -o /tmp/${SKILL_NAME}.skill"
  echo "     claude skills add /tmp/${SKILL_NAME}.skill --force"
  exit 1
fi

latest_version=$(echo "$release_response" | python3 -c \
  "import sys,json; print(json.load(sys.stdin)['version'])" 2>/dev/null) || {
  echo "❌ Unexpected release manifest. Try again later."; exit 1
}
latest_source_commit=$(echo "$release_response" | python3 -c \
  "import sys,json; print(json.load(sys.stdin)['source_commit'])" 2>/dev/null) || {
  echo "❌ Release manifest missing source_commit. Try again later."; exit 1
}
latest_date=$(echo "$release_response" | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('source_date', ''))" 2>/dev/null \
  || echo "")
latest_msg=$(echo "$release_response" | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('source_subject', '')[:70])" 2>/dev/null \
  || echo "")
artifact_path=$(echo "$release_response" | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('artifact', '${DEFAULT_ARTIFACT}'))" 2>/dev/null \
  || echo "${DEFAULT_ARTIFACT}")
DIST_URL="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/${artifact_path}"

echo "  Latest    : ${latest_version}  ${latest_date:+(${latest_date})}"

# ── 3. Already current? ───────────────────────────────────────────────────────
if [[ "$installed_version" == "$latest_version" && "$installed_source_commit" == "$latest_source_commit" ]]; then
  echo ""
  echo "✅ Already up to date (${installed_version})."
  exit 0
fi

# ── 4. Update available ───────────────────────────────────────────────────────
echo ""
echo "🔄 Update: ${installed_version} → ${latest_version}"
[[ -n "$latest_msg" ]] && echo "   ${latest_msg}"
[[ "$installed_source_commit" != "unknown" ]] && \
[[ "$latest_source_commit" != "unknown" ]] && \
[[ "$installed_source_commit" != "$latest_source_commit" ]] && \
  echo "   Full diff: ${COMPARE_URL}/${installed_source_commit}...${latest_source_commit}"
echo ""

# ── 5. Download built .skill from dist/ ──────────────────────────────────────
TMP_DIR="${TMPDIR:-/tmp}"
TMP=$(mktemp "${TMP_DIR%/}/${SKILL_NAME}-${latest_version}-XXXXXX.skill")
trap 'rm -f "${TMP}"' EXIT   # guarantee cleanup on any exit (set -e, error, normal)
echo "   Downloading..."
curl -sf -L "${DIST_URL}" -o "${TMP}" || {
  echo ""
  echo "❌ Download failed."
  echo "   The dist/${SKILL_NAME}.skill may not be committed yet."
  echo "   Check: https://github.com/${REPO_OWNER}/${REPO_NAME}/tree/main/dist"
  rm -f "${TMP}"; exit 1
}

# Sanity check — .skill is a zip; verify it contains a valid SKILL.md and matches release.json
packaged_skill_md=$(python3 -c \
  "import sys, zipfile; print(zipfile.ZipFile(sys.argv[1]).read('${SKILL_NAME}/SKILL.md').decode('utf-8'), end='')" \
  "${TMP}" 2>/dev/null) || {
  echo "❌ Downloaded file invalid (missing ${SKILL_NAME}/SKILL.md). Aborting."
  rm -f "${TMP}"; exit 1
}

echo "$packaged_skill_md" | grep -q "name: ${SKILL_NAME}" || {
  echo "❌ Downloaded file invalid (not a valid skill archive or missing skill name). Aborting."
  rm -f "${TMP}"; exit 1
}

downloaded_version=$(echo "$packaged_skill_md" | awk '
  /^[[:space:]]+version:/ {
    gsub(/["'\''"]/, "", $2)
    print $2
    exit
  }
')
downloaded_source_commit=$(echo "$packaged_skill_md" | awk '
  /^[[:space:]]+source_commit:/ {
    gsub(/["'\''"]/, "", $2)
    print $2
    exit
  }
')

if [[ -z "$downloaded_version" || "$downloaded_version" != "$latest_version" ]]; then
  echo "❌ Downloaded archive version mismatch."
  echo "   release.json: ${latest_version}"
  echo "   archive:      ${downloaded_version:-missing}"
  rm -f "${TMP}"; exit 1
fi

if [[ -z "$downloaded_source_commit" || "$downloaded_source_commit" != "$latest_source_commit" ]]; then
  echo "❌ Downloaded archive source commit mismatch."
  echo "   release.json: ${latest_source_commit}"
  echo "   archive:      ${downloaded_source_commit:-missing}"
  rm -f "${TMP}"; exit 1
fi

# ── 6. Install ────────────────────────────────────────────────────────────────
echo "   Installing..."
if command -v claude &>/dev/null; then
  claude skills add "${TMP}" --force
  echo ""
  echo "✅ Updated: ${installed_version} → ${latest_version}"
  echo "   Restart Claude Code for the new version to take effect."
else
  mkdir -p "$(dirname "${SKILLS_DIR}")"
  cp "${TMP}" "${SKILLS_DIR}/../${SKILL_NAME}.skill"
  echo ""
  echo "⚠️  claude CLI not in PATH. Saved to:"
  echo "   ${SKILLS_DIR}/../${SKILL_NAME}.skill"
  echo "   Run: claude skills add ${SKILLS_DIR}/../${SKILL_NAME}.skill --force"
fi
rm -f "${TMP}"
