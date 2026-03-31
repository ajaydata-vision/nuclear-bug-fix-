#!/usr/bin/env python3
from __future__ import annotations

import argparse
import functools
import http.server
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "nuclear-bug-fix"
VERSION_PATTERN = re.compile(r'^\s{1,4}version:\s*["\']?([^"\r\n\']+)["\']?\s*$', re.MULTILINE)
SOURCE_COMMIT_PATTERN = re.compile(
    r'^\s{1,4}source_commit:\s*["\']?([^"\r\n\']+)["\']?\s*$',
    re.MULTILINE,
)


class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd is not None else None,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def load_release_manifest() -> dict[str, str]:
    manifest_path = REPO_ROOT / "dist" / "release.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def head_commit() -> str:
    return run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"]).stdout.strip()


def create_accessible_temp_root() -> Path:
    parent = Path(tempfile.gettempdir()) / ".nbf-updater"
    parent.mkdir(parents=True, exist_ok=True)

    for _ in range(10):
        candidate = parent / f"upd-{uuid.uuid4().hex[:12]}"
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            continue

    raise RuntimeError("Could not allocate updater temp root")


def latest_release_commit(*, exclude_commits: set[str] | None = None) -> str:
    result = run(
        ["git", "-C", str(REPO_ROOT), "log", "--grep", "^Release ", "--format=%H"],
        check=False,
    )
    excluded = exclude_commits or set()
    for commit in (line.strip() for line in result.stdout.splitlines()):
        if commit and commit not in excluded:
            return commit
    raise ValueError("No prior Release commit found for updater smoke test")


def release_commit_for_version(version: str) -> str:
    pattern = f"^Release {re.escape(version)}$"
    result = run(
        ["git", "-C", str(REPO_ROOT), "log", "--extended-regexp", "--grep", pattern, "-n", "1", "--format=%H"],
        check=False,
    )
    commit = result.stdout.strip()
    if not commit:
        raise ValueError(f"No Release commit found for version {version}")
    return commit


def materialize_commit_snapshot(commit: str, dest: Path) -> Path:
    archive = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "archive", "--format=tar", commit],
        capture_output=True,
        check=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        try:
            tar.extractall(dest, filter="data")
        except TypeError:
            tar.extractall(dest)
    return dest


def install_snapshot(snapshot_dir: Path, installed_dir: Path) -> None:
    install_py = snapshot_dir / "scripts" / "install.py"
    run(
        [
            sys.executable,
            str(install_py),
            "--repo-root",
            str(snapshot_dir),
            "--install-dir",
            str(installed_dir),
        ]
    )


def read_skill_metadata(skill_md: Path) -> tuple[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    version_match = VERSION_PATTERN.search(text)
    source_commit_match = SOURCE_COMMIT_PATTERN.search(text)
    version = version_match.group(1) if version_match else "unknown"
    source_commit = source_commit_match.group(1) if source_commit_match else "unknown"
    return version, source_commit


def detect_git_bash() -> str:
    if os.name != "nt":
        bash = shutil.which("bash")
        if not bash:
            raise ValueError("bash not found in PATH")
        return bash

    candidates: list[Path] = []
    git = shutil.which("git")
    if git:
        git_root = Path(git).resolve().parents[1]
        candidates.extend([git_root / "bin" / "bash.exe", git_root / "usr" / "bin" / "bash.exe"])

    maybe_bash = shutil.which("bash")
    if maybe_bash and "system32" not in maybe_bash.lower():
        candidates.append(Path(maybe_bash))

    candidates.extend(
        [
            Path(r"C:\Program Files\Git\bin\bash.exe"),
            Path(r"C:\Program Files\Git\usr\bin\bash.exe"),
        ]
    )

    seen: set[str] = set()
    for candidate in candidates:
        resolved = str(candidate)
        if resolved in seen:
            continue
        seen.add(resolved)
        if candidate.exists():
            return resolved

    raise ValueError("Git Bash not found")


def detect_powershell() -> str:
    pwsh = shutil.which("pwsh")
    if pwsh:
        return pwsh
    powershell = shutil.which("powershell")
    if powershell:
        return powershell
    raise ValueError("PowerShell not found")


def start_http_server(root: Path) -> tuple[http.server.ThreadingHTTPServer, threading.Thread, str]:
    handler = functools.partial(QuietHTTPRequestHandler, directory=str(root))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    return server, thread, base_url


def home_dir_for_install(installed_dir: Path) -> Path:
    return installed_dir.parents[2]


def print_console(text: str) -> None:
    data = f"{text}\n".encode(sys.stdout.encoding or "utf-8", errors="backslashreplace")
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()


def patch_installed_updater_urls(installed_dir: Path) -> None:
    bash_updater = installed_dir / "scripts" / "update.sh"
    if bash_updater.exists():
        bash_text = bash_updater.read_text(encoding="utf-8")
        bash_text = bash_text.replace(
            'RELEASE_URL="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/dist/release.json"',
            'RELEASE_URL="${NBF_RELEASE_URL:-https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/dist/release.json}"',
        )
        bash_text = bash_text.replace(
            'DIST_URL="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/${artifact_path}"',
            'DIST_URL="${NBF_DIST_URL:-https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/${artifact_path}}"',
        )
        bash_updater.write_text(bash_text, encoding="utf-8")

    powershell_updater = installed_dir / "scripts" / "update.ps1"
    if powershell_updater.exists():
        powershell_text = powershell_updater.read_text(encoding="utf-8")
        powershell_text = powershell_text.replace(
            '$ReleaseUrl = "https://raw.githubusercontent.com/$RepoOwner/$RepoName/main/dist/release.json"',
            '$ReleaseUrl = if ($env:NBF_RELEASE_URL) { $env:NBF_RELEASE_URL } else { "https://raw.githubusercontent.com/$RepoOwner/$RepoName/main/dist/release.json" }',
        )
        powershell_text = powershell_text.replace(
            '$DistUrl = "https://raw.githubusercontent.com/$RepoOwner/$RepoName/main/$ArtifactPath"',
            '$DistUrl = if ($env:NBF_DIST_URL) { $env:NBF_DIST_URL } else { "https://raw.githubusercontent.com/$RepoOwner/$RepoName/main/$ArtifactPath" }',
        )
        powershell_updater.write_text(powershell_text, encoding="utf-8")


def run_bash_updater(installed_dir: Path, release_url: str, dist_url: str, python_io_encoding: str | None) -> str:
    home_dir = home_dir_for_install(installed_dir)
    env = os.environ.copy()
    env["HOME"] = str(home_dir)
    env["NBF_RELEASE_URL"] = release_url
    env["NBF_DIST_URL"] = dist_url
    if python_io_encoding:
        env["PYTHONIOENCODING"] = python_io_encoding

    result = run(
        [detect_git_bash(), str(installed_dir / "scripts" / "update.sh")],
        cwd=home_dir,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Bash updater failed\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result.stdout


def run_powershell_updater(installed_dir: Path, release_url: str, dist_url: str) -> str:
    home_dir = home_dir_for_install(installed_dir)
    env = os.environ.copy()
    env["HOME"] = str(home_dir)
    env["USERPROFILE"] = str(home_dir)
    env["NBF_RELEASE_URL"] = release_url
    env["NBF_DIST_URL"] = dist_url

    result = run(
        [
            detect_powershell(),
            "-File",
            str(installed_dir / "scripts" / "update.ps1"),
            "-InstallDir",
            str(installed_dir),
        ],
        cwd=home_dir,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "PowerShell updater failed\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the updater against the previous released install")
    installed_group = parser.add_mutually_exclusive_group()
    installed_group.add_argument("--installed-commit", help="Commit to materialize as the pre-update installed skill")
    installed_group.add_argument(
        "--installed-release-version",
        help="Release version to materialize as the pre-update installed skill (for example: 1.3)",
    )
    parser.add_argument("--updater", choices=("bash", "powershell"), required=True)
    parser.add_argument(
        "--python-io-encoding",
        help="Optional PYTHONIOENCODING override for the Bash updater (used to simulate Windows code pages)",
    )
    args = parser.parse_args()

    manifest = load_release_manifest()
    expected_version = manifest["version"]
    expected_source_commit = manifest["source_commit"]
    if args.installed_commit:
        installed_commit = args.installed_commit
    elif args.installed_release_version:
        installed_commit = release_commit_for_version(args.installed_release_version)
    else:
        installed_commit = latest_release_commit(exclude_commits={head_commit()})

    temp_root = create_accessible_temp_root()
    try:
        snapshot_dir = temp_root / "snapshot"
        fake_home = temp_root / "User Home"
        installed_dir = fake_home / ".claude" / "skills" / SKILL_NAME
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        materialize_commit_snapshot(installed_commit, snapshot_dir)
        install_snapshot(snapshot_dir, installed_dir)
        installed_version, installed_source_commit = read_skill_metadata(installed_dir / "SKILL.md")

        server, thread, base_url = start_http_server(REPO_ROOT)
        try:
            release_url = f"{base_url}/dist/release.json"
            dist_url = f"{base_url}/dist/nuclear-bug-fix.skill"
            patch_installed_updater_urls(installed_dir)

            if args.updater == "bash":
                output = run_bash_updater(installed_dir, release_url, dist_url, args.python_io_encoding)
            else:
                output = run_powershell_updater(installed_dir, release_url, dist_url)

            updated_version, updated_source_commit = read_skill_metadata(installed_dir / "SKILL.md")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    if updated_version != expected_version:
        raise RuntimeError(
            f"{args.updater} updater installed version {updated_version}, expected {expected_version}"
        )
    if updated_source_commit != expected_source_commit:
        raise RuntimeError(
            f"{args.updater} updater installed source_commit {updated_source_commit}, "
            f"expected {expected_source_commit}"
        )

    print(
        f"PASS: {args.updater} updater moved {installed_version} ({installed_source_commit[:7]}) "
        f"-> {updated_version} ({updated_source_commit[:7]})"
    )
    if output.strip():
        print_console(output.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
