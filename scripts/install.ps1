param(
    [switch]$Project,
    [string]$InstallDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoOwner = "ajaydata-vision"
$RepoName = "nuclear-bug-fix-"
$SkillName = "nuclear-bug-fix"
$SourceArchiveUrl = "https://github.com/$RepoOwner/$RepoName/archive/refs/heads/main.zip"
$AllowedTopLevels = @("SKILL.md", "README.md", "setup", "setup.ps1", "scripts", "references", "benchmarks")

if ($InstallDir) {
    $TargetDir = $InstallDir
} elseif ($Project) {
    $TargetDir = Join-Path (Get-Location) ".claude\skills\$SkillName"
} else {
    $TargetDir = Join-Path $HOME ".claude\skills\$SkillName"
}

$ResolvedTargetDir = [System.IO.Path]::GetFullPath($TargetDir)
if ([System.IO.Path]::GetFileName($ResolvedTargetDir) -ne $SkillName) {
    throw "Install dir must end with ${SkillName}: $ResolvedTargetDir"
}

$SkillsDir = Split-Path -Parent $ResolvedTargetDir
if ([System.IO.Path]::GetFileName($SkillsDir) -ne "skills") {
    throw "Install dir must live inside a skills directory: $ResolvedTargetDir"
}

$TempRoot = [System.IO.Path]::GetTempPath()
$Guid = [guid]::NewGuid().ToString("N")
$ArchivePath = Join-Path $TempRoot "$SkillName-install-$Guid.skill"
$ExtractRoot = Join-Path $TempRoot "$SkillName-extract-$Guid"

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
        if (-not (Test-Path -LiteralPath $SourcePath)) {
            continue
        }

        $DestinationPath = Join-Path $ResolvedTargetDir $TopLevel
        Copy-Item -LiteralPath $SourcePath -Destination $DestinationPath -Recurse -Force
    }

    if (-not (Test-Path -LiteralPath (Join-Path $ResolvedTargetDir "SKILL.md"))) {
        throw "Install failed: SKILL.md was not copied"
    }

    Write-Host "Installed $SkillName to $ResolvedTargetDir"
    Write-Host "Restart Claude Code if it is already running."
}
finally {
    if (Test-Path -LiteralPath $ArchivePath) {
        Remove-Item -LiteralPath $ArchivePath -Force
    }
    if (Test-Path -LiteralPath $ExtractRoot) {
        Remove-Item -LiteralPath $ExtractRoot -Recurse -Force
    }
}
