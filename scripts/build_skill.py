#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "nuclear-bug-fix"
ARCHIVE_PREFIX = f"{SKILL_NAME}/"
ALLOWED_ROOTS = (
    "SKILL.md",
    "README.md",
    "scripts/",
    "references/",
    "benchmarks/",
)
FORBIDDEN_PREFIXES = (
    ".git/",
    ".github/",
    "dist/",
    "evals/",
)
VERSION_PATTERN = re.compile(r"(^\s{1,4}version:\s*)\S+", re.MULTILINE)


def git_tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z"],
        capture_output=True,
        check=True,
    )
    return [Path(item) for item in result.stdout.decode("utf-8").split("\0") if item]


def is_env_path(rel_path: str) -> bool:
    parts = Path(rel_path).parts
    return any(part == ".env" or part.startswith(".env.") for part in parts)


def is_allowed_path(rel_path: str) -> bool:
    if rel_path == "SKILL.md" or rel_path == "README.md":
        return True
    return any(rel_path.startswith(root) for root in ALLOWED_ROOTS[2:])


def is_forbidden_path(rel_path: str) -> bool:
    if any(rel_path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        return True
    if rel_path == ".gitignore":
        return True
    return is_env_path(rel_path)


def should_package(rel_path: str) -> bool:
    return is_allowed_path(rel_path) and not is_forbidden_path(rel_path)


def patch_version(skill_text: str, version: str) -> str:
    updated, count = VERSION_PATTERN.subn(lambda match: f"{match.group(1)}{version}", skill_text, count=1)
    if count != 1:
        raise ValueError("Could not locate metadata.version in SKILL.md")
    return updated


def build_archive(output_path: Path, version: str | None) -> None:
    tracked_files = []
    for rel_path in sorted(path.as_posix() for path in git_tracked_files()):
        if should_package(rel_path):
            tracked_files.append(rel_path)

    if "SKILL.md" not in tracked_files:
        raise ValueError("SKILL.md is missing from the package manifest")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for rel_path in tracked_files:
            source_path = REPO_ROOT / rel_path
            arcname = f"{ARCHIVE_PREFIX}{rel_path}"
            if rel_path == "SKILL.md" and version is not None:
                data = patch_version(source_path.read_text(encoding="utf-8"), version).encode("utf-8")
                info = zipfile.ZipInfo(arcname)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
                continue
            archive.write(source_path, arcname)

    print(f"Built {output_path} ({output_path.stat().st_size:,} bytes, {len(tracked_files)} files)")


def validate_archive(archive_path: Path, expected_version: str | None, max_size_bytes: int | None) -> None:
    if not archive_path.exists():
        raise ValueError(f"Archive does not exist: {archive_path}")

    if max_size_bytes is not None and archive_path.stat().st_size > max_size_bytes:
        raise ValueError(
            f"Archive is too large: {archive_path.stat().st_size:,} bytes > {max_size_bytes:,} bytes"
        )

    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if f"{ARCHIVE_PREFIX}SKILL.md" not in names:
            raise ValueError("Archive is missing nuclear-bug-fix/SKILL.md")

        bad_paths: list[str] = []
        for name in names:
            if not name.startswith(ARCHIVE_PREFIX):
                bad_paths.append(name)
                continue
            rel_path = name[len(ARCHIVE_PREFIX) :]
            if not rel_path:
                continue
            if not should_package(rel_path):
                bad_paths.append(name)

        if bad_paths:
            preview = "\n".join(bad_paths[:20])
            raise ValueError(f"Archive contains forbidden paths:\n{preview}")

        skill_text = archive.read(f"{ARCHIVE_PREFIX}SKILL.md").decode("utf-8")
        if "name: nuclear-bug-fix" not in skill_text:
            raise ValueError("Packaged SKILL.md is missing the skill name")

        if expected_version is not None:
            match = re.search(r"^\s{1,4}version:\s*(\S+)", skill_text, re.MULTILINE)
            if not match:
                raise ValueError("Packaged SKILL.md is missing metadata.version")
            actual_version = match.group(1)
            if actual_version != expected_version:
                raise ValueError(
                    f"Packaged SKILL.md version mismatch: expected {expected_version}, found {actual_version}"
                )

    print(f"Validated {archive_path} ({archive_path.stat().st_size:,} bytes)")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and validate the nuclear-bug-fix skill archive")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build the .skill archive from tracked files")
    build_parser.add_argument("--output", required=True, type=Path, help="Archive output path")
    build_parser.add_argument("--version", help="Version string to stamp into the packaged SKILL.md")

    validate_parser = subparsers.add_parser("validate", help="Validate a built .skill archive")
    validate_parser.add_argument("--archive", required=True, type=Path, help="Archive path")
    validate_parser.add_argument("--expected-version", help="Expected metadata.version inside the archive")
    validate_parser.add_argument(
        "--max-size-bytes",
        type=int,
        help="Fail if the archive exceeds this size",
    )

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.command == "build":
            build_archive(args.output, args.version)
        elif args.command == "validate":
            validate_archive(args.archive, args.expected_version, args.max_size_bytes)
        else:
            raise ValueError(f"Unsupported command: {args.command}")
    except (subprocess.CalledProcessError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
