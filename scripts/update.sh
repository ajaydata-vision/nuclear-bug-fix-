#!/usr/bin/env bash
# nuclear-bug-fix updater
# Invoked by: /nuclear-bug-fix update  OR  bash ~/.claude/skills/nuclear-bug-fix/scripts/update.sh

set -euo pipefail

REPO_OWNER="ajaydata-vision"
REPO_NAME="nuclear-bug-fix-"
SKILL_NAME="nuclear-bug-fix"
SKILLS_DIR="${HOME}/.claude/skills/${SKILL_NAME}"
SKILL_MD="${SKILLS_DIR}/SKILL.md"
DIST_URL="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/dist/${SKILL_NAME}.skill"
COMMITS_API="https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/commits/main"
COMPARE_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/compare"

# ── 1. Read installed version from metadata block in SKILL.md ────────────────
installed_version=""
if [[ -f "$SKILL_MD" ]]; then
  installed_version=$(grep -E "^\s+version:" "$SKILL_MD" 2>/dev/null \
    | head -1 | awk '{print $2}' | tr -d '"' | tr -d "'")
fi

[[ -z "$installed_version" ]] && installed_version="unknown"

echo "nuclear-bug-fix updater"
echo "  Installed : ${installed_version}"

# ── 2. Fetch latest commit from GitHub ───────────────────────────────────────
echo "  Checking  : GitHub (main branch)..."

api_response=$(curl -sf \
  -H "Accept: application/vnd.github.v3+json" \
  "${COMMITS_API}" 2>&1) || {
  echo ""
  echo "❌ Could not reach GitHub. Check your network connection."
  echo "   Manual install:"
  echo "     curl -L ${DIST_URL} -o /tmp/${SKILL_NAME}.skill"
  echo "     claude skills add /tmp/${SKILL_NAME}.skill --force"
  exit 1
}

latest_full=$(echo "$api_response" | python3 -c \
  "import sys,json; print(json.load(sys.stdin)['sha'])" 2>/dev/null) || {
  echo "❌ Unexpected GitHub API response. Try again later."; exit 1
}
latest_short="${latest_full:0:7}"
latest_date=$(echo "$api_response" | python3 -c \
  "import sys,json; print(json.load(sys.stdin)['commit']['committer']['date'][:10])" 2>/dev/null \
  || echo "")
latest_msg=$(echo "$api_response" | python3 -c \
  "import sys,json; print(json.load(sys.stdin)['commit']['message'].splitlines()[0][:70])" 2>/dev/null \
  || echo "")

echo "  Latest    : ${latest_short}  ${latest_date:+(${latest_date})}"

# ── 3. Already current? ───────────────────────────────────────────────────────
if [[ "$installed_version" == "$latest_short" ]]; then
  echo ""
  echo "✅ Already up to date (${installed_version})."
  exit 0
fi

# ── 4. Update available ───────────────────────────────────────────────────────
echo ""
echo "🔄 Update: ${installed_version} → ${latest_short}"
[[ -n "$latest_msg" ]] && echo "   ${latest_msg}"
[[ "$installed_version" != "unknown" ]] && \
  echo "   Full diff: ${COMPARE_URL}/${installed_version}...${latest_short}"
echo ""

# ── 5. Download built .skill from dist/ ──────────────────────────────────────
TMP="/tmp/${SKILL_NAME}-${latest_short}.skill"
echo "   Downloading..."
curl -sf -L "${DIST_URL}" -o "${TMP}" || {
  echo ""
  echo "❌ Download failed."
  echo "   The dist/${SKILL_NAME}.skill may not be committed yet."
  echo "   Check: https://github.com/${REPO_OWNER}/${REPO_NAME}/tree/main/dist"
  rm -f "${TMP}"; exit 1
}

# Sanity check
grep -q "name: nuclear-bug-fix" "${TMP}" 2>/dev/null || {
  echo "❌ Downloaded file invalid (missing skill name). Aborting."; rm -f "${TMP}"; exit 1
}

# ── 6. Install ────────────────────────────────────────────────────────────────
echo "   Installing..."
if command -v claude &>/dev/null; then
  claude skills add "${TMP}" --force
  echo ""
  echo "✅ Updated: ${installed_version} → ${latest_short}"
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
