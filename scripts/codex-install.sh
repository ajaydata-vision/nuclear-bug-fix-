#!/usr/bin/env bash
# nuclear-bug-fix — Codex CLI installer
# Installs into $CODEX_HOME/skills/nuclear-bug-fix/ (defaults to ~/.codex/skills/)
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/ajaydata-vision/nuclear-bug-fix-/main/scripts/codex-install.sh | bash
#   bash codex-install.sh [--install-dir PATH]

set -euo pipefail

REPO_OWNER="ajaydata-vision"
REPO_NAME="nuclear-bug-fix-"
SKILL_NAME="nuclear-bug-fix"
SOURCE_ARCHIVE_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/archive/refs/heads/main.zip"

# Respect $CODEX_HOME if set, otherwise default to ~/.codex
CODEX_HOME="${CODEX_HOME:-${HOME}/.codex}"
install_dir=""

usage() {
  cat <<'EOF'
Usage: codex-install.sh [--install-dir PATH]

Installs nuclear-bug-fix into Codex CLI's skill directory.

  --install-dir PATH   Override the install directory (must end with nuclear-bug-fix
                       inside a directory named skills/)

Default: $CODEX_HOME/skills/nuclear-bug-fix  (CODEX_HOME defaults to ~/.codex)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-dir)
      if [[ $# -lt 2 ]]; then
        echo "error: --install-dir requires a path" >&2
        exit 1
      fi
      install_dir="$2"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

if ! command -v curl >/dev/null 2>&1; then
  echo "error: curl is required" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required" >&2
  exit 1
fi

to_python_path() {
  local path="$1"
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$path"
  else
    printf '%s\n' "$path"
  fi
}

if [[ -n "$install_dir" ]]; then
  target_dir="$install_dir"
else
  target_dir="${CODEX_HOME}/skills/${SKILL_NAME}"
fi

tmp_file="$(mktemp "${TMPDIR:-/tmp}/${SKILL_NAME}-codex-install-XXXXXX.zip")"
trap 'rm -f "$tmp_file"' EXIT

echo "Downloading ${SOURCE_ARCHIVE_URL}"
curl -fsSL "${SOURCE_ARCHIVE_URL}" -o "${tmp_file}"

python3 - "$(to_python_path "${tmp_file}")" "$(to_python_path "${target_dir}")" <<'PY'
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

SKILL_NAME = "nuclear-bug-fix"
# Files and directories to install from the repo.
# openai.yaml is intentionally excluded — SKILL.md alone is sufficient for Codex CLI.
# CLAUDE.md and docs/ are contributor-only and must never be installed into a user's environment.
ALLOWED_TOP_LEVELS = ("SKILL.md", "README.md", "setup", "setup.ps1", "scripts", "references", "benchmarks")
FORBIDDEN_TOP_LEVELS = ("CLAUDE.md", "docs", ".claude", ".github")

archive_path = Path(sys.argv[1])
target_dir = Path(sys.argv[2]).expanduser().resolve()

if target_dir.name != SKILL_NAME:
    raise SystemExit(f"Install dir must end with {SKILL_NAME}: {target_dir}")
if target_dir.parent.name != "skills":
    raise SystemExit(f"Install dir must live inside a directory named 'skills': {target_dir}")

target_dir.parent.mkdir(parents=True, exist_ok=True)
if target_dir.exists():
    if not target_dir.is_dir():
        raise SystemExit(f"Target exists but is not a directory: {target_dir}")
    shutil.rmtree(target_dir)
target_dir.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory() as temp_dir:
    temp_root = Path(temp_dir)
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(temp_root)

    repo_roots = [p for p in temp_root.iterdir() if p.is_dir() and (p / "SKILL.md").exists()]
    if len(repo_roots) != 1:
        raise SystemExit("Could not locate SKILL.md in the downloaded repository snapshot")

    repo_root = repo_roots[0]

    # Defense-in-depth: refuse if a forbidden entry is also in the allow-list.
    for forbidden in FORBIDDEN_TOP_LEVELS:
        if forbidden in ALLOWED_TOP_LEVELS:
            raise SystemExit(
                f"Install aborted: '{forbidden}' appears in both ALLOWED_TOP_LEVELS and "
                f"FORBIDDEN_TOP_LEVELS. Remove it from ALLOWED_TOP_LEVELS in "
                f"scripts/codex-install.sh."
            )

    for name in ALLOWED_TOP_LEVELS:
        source = repo_root / name
        if not source.exists():
            continue
        destination = target_dir / name
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

if not (target_dir / "SKILL.md").exists():
    raise SystemExit("Install failed: SKILL.md was not extracted")

print(f"Installed {SKILL_NAME} to {target_dir}")
print("Restart Codex for the skill to take effect.")
print(f"To update later: bash {target_dir}/scripts/update.sh")
PY
