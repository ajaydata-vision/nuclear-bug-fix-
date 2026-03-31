#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "nuclear-bug-fix"
ARCHIVE_PREFIX = f"{SKILL_NAME}/"
ALLOWED_ROOTS = (
    "scripts/",
    "references/",
    "benchmarks/",
)
ALLOWED_EXACT_FILES = (
    "SKILL.md",
    "README.md",
    "setup",
    "setup.ps1",
)
FORBIDDEN_PREFIXES = (
    ".git/",
    ".github/",
    "dist/",
    "evals/",
)
VERSION_PATTERN = re.compile(r"(^\s{1,4}version:\s*).+$", re.MULTILINE)
SOURCE_COMMIT_PATTERN = re.compile(r"(^\s{1,4}source_commit:\s*).+$", re.MULTILINE)
DEFAULT_RELEASE_ARTIFACT = f"dist/{SKILL_NAME}.skill"
LEGACY_ASCII_REPLACEMENTS = (
    ("☢️ ", ""),
    ("☢", ""),
    ("️", ""),
    ("—", "-"),
    ("–", "-"),
    ("→", "->"),
    ("≠", "!="),
    ("□", "[ ]"),
    ("★", "*"),
)


def git_repo_files() -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True,
        check=True,
    )
    return [Path(item) for item in result.stdout.decode("utf-8").split("\0") if item]


def is_env_path(rel_path: str) -> bool:
    parts = Path(rel_path).parts
    return any(part == ".env" or part.startswith(".env.") for part in parts)


def is_generated_path(rel_path: str) -> bool:
    path = Path(rel_path)
    if any(part == "__pycache__" for part in path.parts):
        return True
    return path.suffix in {".pyc", ".pyo"}


def is_allowed_path(rel_path: str) -> bool:
    if rel_path in ALLOWED_EXACT_FILES:
        return True
    return any(rel_path.startswith(root) for root in ALLOWED_ROOTS)


def is_forbidden_path(rel_path: str) -> bool:
    if any(rel_path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        return True
    if rel_path == ".gitignore":
        return True
    return is_env_path(rel_path) or is_generated_path(rel_path)


def should_package(rel_path: str) -> bool:
    return is_allowed_path(rel_path) and not is_forbidden_path(rel_path)


def patch_version(skill_text: str, version: str) -> str:
    updated, count = VERSION_PATTERN.subn(lambda match: f'{match.group(1)}"{version}"', skill_text, count=1)
    if count != 1:
        raise ValueError("Could not locate metadata.version in SKILL.md")
    return updated


def patch_source_commit(skill_text: str, source_commit: str | None) -> str:
    if source_commit is None:
        return skill_text

    updated, count = SOURCE_COMMIT_PATTERN.subn(
        lambda match: f'{match.group(1)}"{source_commit}"',
        skill_text,
        count=1,
    )
    if count == 1:
        return updated

    version_match = VERSION_PATTERN.search(skill_text)
    if version_match is None:
        raise ValueError("Could not locate metadata.version in SKILL.md")

    insert_at = version_match.end()
    return f'{skill_text[:insert_at]}\n  source_commit: "{source_commit}"{skill_text[insert_at:]}'


def patch_skill_metadata(skill_text: str, version: str, source_commit: str | None) -> str:
    return patch_source_commit(patch_version(skill_text, version), source_commit)


def sanitize_packaged_skill_text(skill_text: str) -> str:
    sanitized = skill_text
    for old, new in LEGACY_ASCII_REPLACEMENTS:
        sanitized = sanitized.replace(old, new)

    remaining = sorted({char for char in sanitized if ord(char) > 127})
    if remaining:
        codepoints = ", ".join(f"U+{ord(char):04X}" for char in remaining)
        raise ValueError(f"Packaged SKILL.md still contains non-ASCII characters: {codepoints}")

    return sanitized


def extract_skill_metadata(skill_text: str) -> dict[str, str]:
    version_match = re.search(r'^\s{1,4}version:\s*["\']?([^"\r\n\']+)["\']?\s*$', skill_text, re.MULTILINE)
    if not version_match:
        raise ValueError("Packaged SKILL.md is missing metadata.version")

    source_commit_match = re.search(
        r'^\s{1,4}source_commit:\s*["\']?([^"\r\n\']+)["\']?\s*$',
        skill_text,
        re.MULTILINE,
    )
    metadata = {"version": version_match.group(1)}
    if source_commit_match:
        metadata["source_commit"] = source_commit_match.group(1)
    return metadata


def stamp_skill_file(skill_md_path: Path, version: str, source_commit: str | None) -> None:
    skill_md_path.write_text(
        patch_skill_metadata(skill_md_path.read_text(encoding="utf-8"), version, source_commit),
        encoding="utf-8",
    )
    if source_commit is not None:
        print(f"Stamped {skill_md_path} with version {version} and source_commit {source_commit}")
    else:
        print(f"Stamped {skill_md_path} with version {version}")


def resolve_git_metadata(source_commit: str) -> dict[str, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "show", "-s", "--format=%H%n%h%n%cs%n%s", source_commit],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
    except subprocess.CalledProcessError:
        return {
            "source_commit": source_commit,
            "source_commit_short": source_commit,
            "source_date": "",
            "source_subject": "",
        }

    lines = result.stdout.splitlines()
    if len(lines) < 4:
        raise ValueError(f"Could not resolve git metadata for source commit {source_commit}")

    return {
        "source_commit": lines[0],
        "source_commit_short": lines[1],
        "source_date": lines[2],
        "source_subject": lines[3],
    }


def repo_relative_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def write_release_manifest(output_path: Path, version: str, artifact: str, source_commit: str) -> None:
    metadata = resolve_git_metadata(source_commit)
    manifest = {
        "skill": SKILL_NAME,
        "version": version,
        "source_commit": metadata["source_commit"],
        "source_commit_short": metadata["source_commit_short"],
        "source_date": metadata["source_date"],
        "source_subject": metadata["source_subject"],
        "artifact": artifact,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path} (version {manifest['version']})")


def load_release_manifest(manifest_path: Path) -> dict[str, str]:
    if not manifest_path.exists():
        raise ValueError(f"Release manifest does not exist: {manifest_path}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid release manifest JSON: {manifest_path}") from exc

    required_keys = ("skill", "version", "source_commit", "artifact")
    missing = [key for key in required_keys if key not in manifest]
    if missing:
        raise ValueError(f"Release manifest missing required keys: {', '.join(missing)}")

    if manifest["skill"] != SKILL_NAME:
        raise ValueError(
            f"Release manifest skill mismatch: expected {SKILL_NAME}, found {manifest['skill']}"
        )

    return {key: str(value) for key, value in manifest.items()}


def build_archive(output_path: Path, version: str | None, source_commit: str | None) -> None:
    tracked_files = []
    for rel_path in sorted(path.as_posix() for path in git_repo_files()):
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
            if rel_path == "SKILL.md":
                skill_text = source_path.read_text(encoding="utf-8")
                if version is not None:
                    skill_text = patch_skill_metadata(skill_text, version, source_commit)
                data = sanitize_packaged_skill_text(skill_text).encode("utf-8")
                info = zipfile.ZipInfo(arcname)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
                continue
            archive.write(source_path, arcname)

    print(f"Built {output_path} ({output_path.stat().st_size:,} bytes, {len(tracked_files)} files)")


def validate_archive(
    archive_path: Path,
    expected_version: str | None,
    max_size_bytes: int | None,
    manifest_path: Path | None,
) -> None:
    if not archive_path.exists():
        raise ValueError(f"Archive does not exist: {archive_path}")

    if manifest_path is not None:
        manifest = load_release_manifest(manifest_path)
        manifest_version = manifest["version"]
        manifest_source_commit = manifest["source_commit"]
        if expected_version is None:
            expected_version = manifest_version
        elif expected_version != manifest_version:
            raise ValueError(
                f"Release manifest version mismatch: expected {expected_version}, found {manifest_version}"
            )

        archive_rel_path = repo_relative_path(archive_path)
        if manifest["artifact"] != archive_rel_path:
            raise ValueError(
                f"Release manifest artifact mismatch: expected {archive_rel_path}, found {manifest['artifact']}"
            )

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

        metadata = extract_skill_metadata(skill_text)
        if expected_version is not None:
            actual_version = metadata["version"]
            if actual_version != expected_version:
                raise ValueError(
                    f"Packaged SKILL.md version mismatch: expected {expected_version}, found {actual_version}"
                )

        if manifest_path is not None:
            actual_source_commit = metadata.get("source_commit")
            if actual_source_commit != manifest_source_commit:
                raise ValueError(
                    "Packaged SKILL.md source_commit mismatch: "
                    f"expected {manifest_source_commit}, found {actual_source_commit or 'missing'}"
                )

    print(f"Validated {archive_path} ({archive_path.stat().st_size:,} bytes)")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and validate the nuclear-bug-fix skill archive")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stamp_parser = subparsers.add_parser("stamp-version", help="Stamp release metadata into SKILL.md")
    stamp_parser.add_argument("--skill-md", required=True, type=Path, help="Path to SKILL.md")
    stamp_parser.add_argument("--version", required=True, help="Version string to stamp into SKILL.md")
    stamp_parser.add_argument("--source-commit", help="Exact source commit to stamp into SKILL.md")

    build_parser = subparsers.add_parser(
        "build",
        help="Build the .skill archive from repo files (tracked plus non-ignored additions)",
    )
    build_parser.add_argument("--output", required=True, type=Path, help="Archive output path")
    build_parser.add_argument("--version", help="Version string to stamp into the packaged SKILL.md")
    build_parser.add_argument("--source-commit", help="Source commit to stamp into the packaged SKILL.md")

    manifest_parser = subparsers.add_parser(
        "write-release-manifest",
        help="Write the release manifest used by CI and the updater",
    )
    manifest_parser.add_argument("--output", required=True, type=Path, help="Manifest output path")
    manifest_parser.add_argument("--version", required=True, help="Released source version")
    manifest_parser.add_argument("--source-commit", required=True, help="Released source commit")
    manifest_parser.add_argument(
        "--artifact",
        default=DEFAULT_RELEASE_ARTIFACT,
        help="Repo-relative path to the built .skill artifact",
    )

    validate_parser = subparsers.add_parser("validate", help="Validate a built .skill archive")
    validate_parser.add_argument("--archive", required=True, type=Path, help="Archive path")
    validate_parser.add_argument("--expected-version", help="Expected metadata.version inside the archive")
    validate_parser.add_argument(
        "--manifest",
        type=Path,
        help="Release manifest path to treat as the version source of truth",
    )
    validate_parser.add_argument(
        "--max-size-bytes",
        type=int,
        help="Fail if the archive exceeds this size",
    )

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.command == "stamp-version":
            stamp_skill_file(args.skill_md, args.version, args.source_commit)
        elif args.command == "build":
            build_archive(args.output, args.version, args.source_commit)
        elif args.command == "write-release-manifest":
            write_release_manifest(args.output, args.version, args.artifact, args.source_commit)
        elif args.command == "validate":
            validate_archive(args.archive, args.expected_version, args.max_size_bytes, args.manifest)
        else:
            raise ValueError(f"Unsupported command: {args.command}")
    except (subprocess.CalledProcessError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
