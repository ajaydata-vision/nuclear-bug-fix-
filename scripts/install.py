#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import sys
import uuid
import zipfile
from pathlib import Path, PurePosixPath


SKILL_NAME = "nuclear-bug-fix"
ARCHIVE_PREFIX = f"{SKILL_NAME}/"
ALLOWED_TOP_LEVEL_FILES = (
    "SKILL.md",
    "README.md",
    "setup",
    "setup.ps1",
)
ALLOWED_TOP_LEVEL_DIRS = (
    "scripts",
    "references",
    "benchmarks",
)
ALLOWED_TOP_LEVELS = ALLOWED_TOP_LEVEL_FILES + ALLOWED_TOP_LEVEL_DIRS
VERSION_PATTERN = re.compile(r"^\s{1,4}version:\s*(\S+)", re.MULTILINE)


STAGING_PREFIX = ".nbf-stg-"
BACKUP_PREFIX = ".nbf-bak-"
TEMP_NAME_BYTES = 12


def temp_name(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:TEMP_NAME_BYTES]}"


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install nuclear-bug-fix into Claude Code's skills directory"
    )
    parser.add_argument(
        "--scope",
        choices=("personal", "project"),
        default="personal",
        help="Install into ~/.claude/skills (personal) or .claude/skills (project)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root used when --scope project is selected",
    )
    parser.add_argument(
        "--install-dir",
        type=Path,
        help="Explicit target skill directory; must end with skills/nuclear-bug-fix",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=default_repo_root(),
        help="Repo root containing SKILL.md when installing from a local checkout",
    )
    parser.add_argument(
        "--from-archive",
        type=Path,
        help="Install from a packaged .skill archive instead of the local repo checkout",
    )
    return parser.parse_args()


def resolve_target_dir(args: argparse.Namespace) -> Path:
    if args.install_dir is not None:
        target_dir = args.install_dir.expanduser()
    elif args.scope == "project":
        target_dir = args.project_root.expanduser() / ".claude" / "skills" / SKILL_NAME
    else:
        target_dir = Path.home() / ".claude" / "skills" / SKILL_NAME

    resolved = target_dir.resolve()
    if resolved.name != SKILL_NAME:
        raise ValueError(f"Install dir must end with {SKILL_NAME}: {resolved}")
    if resolved.parent.name != "skills":
        raise ValueError(f"Install dir must live inside a skills directory: {resolved}")
    return resolved


def extract_version(skill_md: Path) -> str:
    match = VERSION_PATTERN.search(skill_md.read_text(encoding="utf-8"))
    return match.group(1) if match else "unknown"


def ensure_target_parent(target_dir: Path) -> None:
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    if target_dir.exists():
        if not target_dir.is_dir():
            raise ValueError(f"Target exists but is not a directory: {target_dir}")


def create_staging_dir(target_dir: Path) -> Path:
    ensure_target_parent(target_dir)
    staging_dir = target_dir.parent / temp_name(STAGING_PREFIX)
    staging_dir.mkdir(parents=True, exist_ok=False)
    return staging_dir


def cleanup_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def validate_install_root(install_root: Path, context: str) -> Path:
    skill_md = install_root / "SKILL.md"
    if not skill_md.exists():
        raise ValueError(f"{context} is missing SKILL.md")
    return skill_md


def replace_install_dir(staging_dir: Path, target_dir: Path) -> None:
    ensure_target_parent(target_dir)
    backup_dir: Path | None = None
    backed_up_existing = False
    moved_staging = False

    try:
        if target_dir.exists():
            backup_dir = target_dir.parent / temp_name(BACKUP_PREFIX)
            shutil.move(str(target_dir), str(backup_dir))
            backed_up_existing = True

        shutil.move(str(staging_dir), str(target_dir))
        moved_staging = True
    except Exception:
        if moved_staging:
            cleanup_dir(target_dir)
        if backed_up_existing and backup_dir is not None and backup_dir.exists():
            shutil.move(str(backup_dir), str(target_dir))
        raise
    finally:
        cleanup_dir(staging_dir)
        if backup_dir is not None and backup_dir.exists():
            cleanup_dir(backup_dir)


def resolve_staged_destination(staging_dir: Path, rel_path: Path, source_name: str) -> Path:
    destination = (staging_dir / rel_path).resolve()
    try:
        destination.relative_to(staging_dir.resolve())
    except ValueError as exc:
        raise ValueError(f"Unsafe archive path: {source_name}") from exc
    return destination


def parse_archive_member_path(filename: str) -> Path | None:
    if not filename.startswith(ARCHIVE_PREFIX):
        return None

    rel_name = filename[len(ARCHIVE_PREFIX) :]
    if not rel_name:
        return None

    normalized_name = rel_name.replace("\\", "/")
    rel_path = PurePosixPath(normalized_name)
    parts = rel_path.parts
    if rel_path.is_absolute() or rel_path.anchor or not parts:
        raise ValueError(f"Unsafe archive path: {filename}")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"Unsafe archive path: {filename}")
    if any(":" in part for part in parts):
        raise ValueError(f"Unsafe archive path: {filename}")

    top_level = parts[0]
    if top_level in ALLOWED_TOP_LEVEL_FILES and len(parts) != 1:
        raise ValueError(f"Unexpected archive path: {filename}")
    if top_level not in ALLOWED_TOP_LEVELS:
        raise ValueError(f"Unexpected archive path: {filename}")

    return Path(*parts)


def iter_local_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for entry in ALLOWED_TOP_LEVELS:
        path = repo_root / entry
        if not path.exists():
            continue
        if path.is_file():
            files.append(path.relative_to(repo_root))
            continue
        for child in sorted(path.rglob("*")):
            if not child.is_file():
                continue
            if "__pycache__" in child.parts:
                continue
            if child.suffix in {".pyc", ".pyo"}:
                continue
            files.append(child.relative_to(repo_root))
    return files


def install_from_repo(repo_root: Path, target_dir: Path) -> str:
    skill_md = repo_root / "SKILL.md"
    if not skill_md.exists():
        raise ValueError(f"Local repo install requires SKILL.md: {repo_root}")

    staging_dir = create_staging_dir(target_dir)

    try:
        copied = 0
        for rel_path in iter_local_files(repo_root):
            source = repo_root / rel_path
            destination = staging_dir / rel_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied += 1

        if copied == 0:
            raise ValueError(f"No installable files were found in {repo_root}")

        validate_install_root(staging_dir, "Staged skill")
        replace_install_dir(staging_dir, target_dir)
    except Exception:
        cleanup_dir(staging_dir)
        raise

    installed_skill_md = validate_install_root(target_dir, "Installed skill")
    return extract_version(installed_skill_md)


def install_from_archive(archive_path: Path, target_dir: Path) -> str:
    if not archive_path.exists():
        raise ValueError(f"Archive does not exist: {archive_path}")

    staging_dir = create_staging_dir(target_dir)

    try:
        with zipfile.ZipFile(archive_path) as archive:
            if f"{ARCHIVE_PREFIX}SKILL.md" not in archive.namelist():
                raise ValueError(f"Archive is missing {ARCHIVE_PREFIX}SKILL.md")

            for info in archive.infolist():
                rel_path = parse_archive_member_path(info.filename)
                if rel_path is None:
                    continue

                destination = resolve_staged_destination(staging_dir, rel_path, info.filename)
                if info.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue

                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, destination.open("wb") as output:
                    shutil.copyfileobj(source, output)

        validate_install_root(staging_dir, "Staged archive install")
        replace_install_dir(staging_dir, target_dir)
    except Exception:
        cleanup_dir(staging_dir)
        raise

    installed_skill_md = validate_install_root(target_dir, "Installed skill")
    return extract_version(installed_skill_md)


def main() -> int:
    args = parse_args()
    target_dir = resolve_target_dir(args)

    try:
        if args.from_archive is not None:
            version = install_from_archive(args.from_archive.expanduser().resolve(), target_dir)
        else:
            version = install_from_repo(args.repo_root.expanduser().resolve(), target_dir)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"Install failed: {exc}", file=sys.stderr)
        return 1

    print(f"Installed {SKILL_NAME} {version} to {target_dir}")
    print("Restart Claude Code if it is already running.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
