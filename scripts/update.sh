#!/usr/bin/env bash
# nuclear-bug-fix updater
# Invoked by: /nuclear-bug-fix update  OR  bash ~/.claude/skills/nuclear-bug-fix/scripts/update.sh

set -euo pipefail

REPO_OWNER="ajaydata-vision"
REPO_NAME="nuclear-bug-fix-"
SKILL_NAME="nuclear-bug-fix"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SELF_SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PERSONAL_SKILL_DIR="${HOME}/.claude/skills/${SKILL_NAME}"
PROJECT_SKILL_DIR=".claude/skills/${SKILL_NAME}"
DEFAULT_ARTIFACT="dist/${SKILL_NAME}.skill"
RELEASE_URL="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/dist/release.json"
COMPARE_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/compare"
INSTALL_SH_URL="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/scripts/install.sh"
INSTALL_PS1_URL="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/scripts/install.ps1"

print_manual_reinstall() {
  echo "   Reinstall:"
  echo "     macOS/Linux personal: curl -fsSL ${INSTALL_SH_URL} | bash"
  echo "     macOS/Linux project:  curl -fsSL ${INSTALL_SH_URL} | bash -s -- --project"
  echo "     Windows PowerShell:   irm ${INSTALL_PS1_URL} | iex"
}

read_skill_metadata_field() {
  local file="$1"
  local field="$2"
  grep -E "^\s+${field}:" "$file" 2>/dev/null \
    | head -1 | awk '{print $2}' | tr -d '"' | tr -d "'"
}

# ── 1. Locate installed skill directory and read version metadata ─────────────
installed_version=""
installed_source_commit=""
TARGET_DIR=""
TARGET_SKILL_MD=""

if [[ -f "${SELF_SKILL_DIR}/SKILL.md" ]] \
  && [[ "$(basename "${SELF_SKILL_DIR}")" == "${SKILL_NAME}" ]] \
  && [[ "$(basename "$(dirname "${SELF_SKILL_DIR}")")" == "skills" ]]; then
  TARGET_DIR="${SELF_SKILL_DIR}"
  TARGET_SKILL_MD="${SELF_SKILL_DIR}/SKILL.md"
elif [[ -f "${PERSONAL_SKILL_DIR}/SKILL.md" ]]; then
  TARGET_DIR="${PERSONAL_SKILL_DIR}"
  TARGET_SKILL_MD="${PERSONAL_SKILL_DIR}/SKILL.md"
elif [[ -f "${PROJECT_SKILL_DIR}/SKILL.md" ]]; then
  TARGET_DIR="${PROJECT_SKILL_DIR}"
  TARGET_SKILL_MD="${PROJECT_SKILL_DIR}/SKILL.md"
fi

if [[ -n "${TARGET_SKILL_MD}" ]]; then
  installed_version=$(read_skill_metadata_field "${TARGET_SKILL_MD}" "version")
  installed_source_commit=$(read_skill_metadata_field "${TARGET_SKILL_MD}" "source_commit")
fi

[[ -z "$installed_version" ]] && installed_version="unknown"
[[ -z "$installed_source_commit" ]] && installed_source_commit="unknown"

echo "nuclear-bug-fix updater"
echo "  Installed : ${installed_version}"
[[ -n "${TARGET_DIR}" ]] && echo "  Location  : ${TARGET_DIR}"

# ── 2. Fetch latest released version from GitHub ─────────────────────────────
echo "  Checking  : GitHub release manifest..."

release_response=$(curl -sf \
  -H "Accept: application/json" \
  "${RELEASE_URL}") || {
  echo ""
  echo "❌ Could not fetch dist/release.json from GitHub."
  print_manual_reinstall
  exit 1
}

if ! command -v python3 &>/dev/null; then
  echo "❌ python3 is required to parse dist/release.json but was not found in PATH."
  echo "   Install python3 or reinstall with:"
  print_manual_reinstall
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

# ── 6. Install into the existing skill directory ──────────────────────────────
if [[ -z "${TARGET_DIR}" ]]; then
  TARGET_DIR="${PERSONAL_SKILL_DIR}"
fi

echo "   Installing into ${TARGET_DIR}..."

if [[ ! -f "${SCRIPT_DIR}/install.py" ]]; then
  echo "❌ Missing installer helper: ${SCRIPT_DIR}/install.py"
  print_manual_reinstall
  rm -f "${TMP}"; exit 1
fi

python3 "${SCRIPT_DIR}/install.py" --from-archive "${TMP}" --install-dir "${TARGET_DIR}" >/dev/null || {
  echo "❌ Failed to install the downloaded update."
  print_manual_reinstall
  rm -f "${TMP}"; exit 1
}

echo ""
echo "✅ Updated: ${installed_version} → ${latest_version}"
echo "   Restart Claude Code for the new version to take effect."
rm -f "${TMP}"
