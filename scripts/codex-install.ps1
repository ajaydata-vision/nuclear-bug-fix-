# nuclear-bug-fix — Codex CLI installer (Windows PowerShell)
# Installs into $env:CODEX_HOME\skills\nuclear-bug-fix\ (defaults to $HOME\.codex\skills\)
# Usage:
#   irm https://raw.githubusercontent.com/ajaydata-vision/nuclear-bug-fix-/main/scripts/codex-install.ps1 | iex
#   .\codex-install.ps1 [-InstallDir PATH]

param(
    [string]$InstallDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoOwner = "ajaydata-vision"
$RepoName  = "nuclear-bug-fix-"
$SkillName = "nuclear-bug-fix"
$SourceArchiveUrl = "https://github.com/$RepoOwner/$RepoName/archive/refs/heads/main.zip"

# Respect $env:CODEX_HOME if set, otherwise default to $HOME\.codex
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }

# Files and directories to install from the repo.
# openai.yaml intentionally excluded — SKILL.md alone is sufficient for Codex CLI.
# CLAUDE.md and docs/ are contributor-only and must never be installed into a user's environment.
$AllowedTopLevels = @("SKILL.md", "README.md", "setup", "setup.ps1", "scripts", "references", "benchmarks")

if ($InstallDir) {
    $TargetDir = $InstallDir
} else {
    $TargetDir = Join-Path $CodexHome "skills\$SkillName"
}

$ResolvedTargetDir = [System.IO.Path]::GetFullPath($TargetDir)

if ([System.IO.Path]::GetFileName($ResolvedTargetDir) -ne $SkillName) {
    throw "Install dir must end with ${SkillName}: $ResolvedTargetDir"
}
$SkillsDir = Split-Path -Parent $ResolvedTargetDir
if ([System.IO.Path]::GetFileName($SkillsDir) -ne "skills") {
    throw "Install dir must live inside a directory named 'skills': $ResolvedTargetDir"
}

$TempRoot  = [System.IO.Path]::GetTempPath()
$Guid      = [guid]::NewGuid().ToString("N")
$ArchivePath  = Join-Path $TempRoot "$SkillName-codex-install-$Guid.zip"
$ExtractRoot  = Join-Path $TempRoot "$SkillName-codex-extract-$Guid"

try {
    Write-Host "Downloading $SourceArchiveUrl"
    Invoke-WebRequest -Uri $SourceArchiveUrl -OutFile $ArchivePath

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($ArchivePath, $ExtractRoot)

    $RepoRoot = Get-ChildItem -LiteralPath $ExtractRoot -Directory |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") } |
        Select-Object -First 1

    if (-not $RepoRoot) {
        throw "Archive is missing SKILL.md"
    }

    New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null
    if (Test-Path -LiteralPath $ResolvedTargetDir) {
        Remove-Item -LiteralPath $ResolvedTargetDir -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $ResolvedTargetDir | Out-Null

    foreach ($TopLevel in $AllowedTopLevels) {
        $SourcePath = Join-Path $RepoRoot.FullName $TopLevel
        if (-not (Test-Path -LiteralPath $SourcePath)) { continue }
        $DestPath = Join-Path $ResolvedTargetDir $TopLevel
        if (Test-Path -LiteralPath $SourcePath -PathType Container) {
            Copy-Item -LiteralPath $SourcePath -Destination $DestPath -Recurse -Force
        } else {
            Copy-Item -LiteralPath $SourcePath -Destination $DestPath -Force
        }
    }

    $SkillMdPath = Join-Path $ResolvedTargetDir "SKILL.md"
    if (-not (Test-Path -LiteralPath $SkillMdPath)) {
        throw "Install failed: SKILL.md was not extracted"
    }

    Write-Host "Installed $SkillName to $ResolvedTargetDir"
    Write-Host "Restart Codex for the skill to take effect."
    Write-Host "To update later: run scripts\update.ps1 inside your Codex skill directory."

} finally {
    if (Test-Path -LiteralPath $ArchivePath)  { Remove-Item -LiteralPath $ArchivePath  -Force }
    if (Test-Path -LiteralPath $ExtractRoot)  { Remove-Item -LiteralPath $ExtractRoot  -Recurse -Force }
}
