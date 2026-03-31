param(
    [string]$InstallDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoOwner = "ajaydata-vision"
$RepoName = "nuclear-bug-fix-"
$SkillName = "nuclear-bug-fix"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SelfSkillDir = Split-Path -Parent $ScriptDir
$PersonalSkillDir = Join-Path $HOME ".claude\skills\$SkillName"
$ProjectSkillDir = Join-Path (Get-Location) ".claude\skills\$SkillName"
$DefaultArtifact = "dist/$SkillName.skill"
$ReleaseUrl = if ($env:NBF_RELEASE_URL) { $env:NBF_RELEASE_URL } else { "https://raw.githubusercontent.com/$RepoOwner/$RepoName/main/dist/release.json" }
$CompareUrl = if ($env:NBF_COMPARE_URL) { $env:NBF_COMPARE_URL } else { "https://github.com/$RepoOwner/$RepoName/compare" }
$InstallShUrl = if ($env:NBF_INSTALL_SH_URL) { $env:NBF_INSTALL_SH_URL } else { "https://raw.githubusercontent.com/$RepoOwner/$RepoName/main/scripts/install.sh" }
$InstallPs1Url = if ($env:NBF_INSTALL_PS1_URL) { $env:NBF_INSTALL_PS1_URL } else { "https://raw.githubusercontent.com/$RepoOwner/$RepoName/main/scripts/install.ps1" }

# Keep behavior in sync with scripts/update.sh.

function Write-ManualReinstall {
    Write-Host "   Reinstall:"
    Write-Host "     macOS/Linux personal: curl -fsSL $InstallShUrl | bash"
    Write-Host "     macOS/Linux project:  curl -fsSL $InstallShUrl | bash -s -- --project"
    Write-Host "     Windows PS personal:  irm $InstallPs1Url | iex"
    Write-Host "     Windows PS project:   & ([scriptblock]::Create((irm $InstallPs1Url))) -Project"
}

function Read-SkillMetadataField {
    param(
        [string]$Path,
        [string]$Field
    )

    if (-not $Path -or -not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    $Pattern = '(?m)^\s+{0}:\s*[''"]?([^''"\r\n]+)[''"]?\s*$' -f [regex]::Escape($Field)
    $Match = [regex]::Match((Get-Content -LiteralPath $Path -Raw), $Pattern)
    if ($Match.Success) {
        return $Match.Groups[1].Value
    }

    return $null
}

function Find-Python {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $Python) {
        $Python = Get-Command python3 -ErrorAction SilentlyContinue
    }
    return $Python
}

$TargetDir = $null
$TargetSkillMd = $null

if ($InstallDir) {
    $TargetDir = [System.IO.Path]::GetFullPath($InstallDir)
    $TargetSkillMd = Join-Path $TargetDir "SKILL.md"
} else {
    $SelfName = [System.IO.Path]::GetFileName($SelfSkillDir)
    $SelfParentName = [System.IO.Path]::GetFileName((Split-Path -Parent $SelfSkillDir))
    $SelfIsInstalled = (
        (Test-Path -LiteralPath (Join-Path $SelfSkillDir "SKILL.md")) -and
        $SelfName -eq $SkillName -and
        $SelfParentName -eq "skills"
    )

    if ($SelfIsInstalled) {
        $TargetDir = $SelfSkillDir
        $TargetSkillMd = Join-Path $SelfSkillDir "SKILL.md"
    } elseif (Test-Path -LiteralPath (Join-Path $PersonalSkillDir "SKILL.md")) {
        $TargetDir = $PersonalSkillDir
        $TargetSkillMd = Join-Path $PersonalSkillDir "SKILL.md"
    } elseif (Test-Path -LiteralPath (Join-Path $ProjectSkillDir "SKILL.md")) {
        $TargetDir = $ProjectSkillDir
        $TargetSkillMd = Join-Path $ProjectSkillDir "SKILL.md"
    }
}

$InstalledVersion = Read-SkillMetadataField -Path $TargetSkillMd -Field "version"
$InstalledSourceCommit = Read-SkillMetadataField -Path $TargetSkillMd -Field "source_commit"

if (-not $InstalledVersion) {
    $InstalledVersion = "unknown"
}
if (-not $InstalledSourceCommit) {
    $InstalledSourceCommit = "unknown"
}

Write-Host "nuclear-bug-fix updater"
Write-Host "  Installed : $InstalledVersion"
if ($TargetDir) {
    Write-Host "  Location  : $TargetDir"
}

Write-Host "  Checking  : GitHub release manifest..."
try {
    $Release = Invoke-RestMethod -Headers @{ Accept = "application/json" } -Uri $ReleaseUrl
} catch {
    Write-Host ""
    Write-Host "❌ Could not fetch dist/release.json from GitHub."
    Write-ManualReinstall
    exit 1
}

$LatestVersion = [string]$Release.version
$LatestSourceCommit = [string]$Release.source_commit
$LatestDate = [string]$Release.source_date
$LatestMsg = [string]$Release.source_subject
$ArtifactPath = [string]$Release.artifact

if (-not $LatestVersion) {
    Write-Host "❌ Unexpected release manifest. Try again later."
    exit 1
}
if (-not $LatestSourceCommit) {
    Write-Host "❌ Release manifest missing source_commit. Try again later."
    exit 1
}
if (-not $ArtifactPath) {
    $ArtifactPath = $DefaultArtifact
}

$DistUrl = if ($env:NBF_DIST_URL) { $env:NBF_DIST_URL } else { "https://raw.githubusercontent.com/$RepoOwner/$RepoName/main/$ArtifactPath" }
Write-Host "  Latest    : $LatestVersion" -NoNewline
if ($LatestDate) {
    Write-Host " ($LatestDate)"
} else {
    Write-Host ""
}

if ($InstalledVersion -eq $LatestVersion -and $InstalledSourceCommit -eq $LatestSourceCommit) {
    Write-Host ""
    Write-Host "✅ Already up to date ($InstalledVersion)."
    exit 0
}

Write-Host ""
Write-Host "🔄 Update: $InstalledVersion → $LatestVersion"
if ($LatestMsg) {
    Write-Host "   $LatestMsg"
}
if ($InstalledSourceCommit -ne "unknown" -and $LatestSourceCommit -ne "unknown" -and $InstalledSourceCommit -ne $LatestSourceCommit) {
    Write-Host "   Full diff: $CompareUrl/$InstalledSourceCommit...$LatestSourceCommit"
}
Write-Host ""

$TempRoot = [System.IO.Path]::GetTempPath()
$TempArchive = Join-Path $TempRoot "$SkillName-$LatestVersion-$([guid]::NewGuid().ToString('N')).skill"
$PackagedSkillMd = $null

try {
    Write-Host "   Downloading..."
    try {
        Invoke-WebRequest -Uri $DistUrl -OutFile $TempArchive
    } catch {
        Write-Host ""
        Write-Host "❌ Download failed."
        Write-Host "   The dist/$SkillName.skill may not be committed yet."
        Write-Host "   Check: https://github.com/$RepoOwner/$RepoName/tree/main/dist"
        exit 1
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    try {
        $Archive = [System.IO.Compression.ZipFile]::OpenRead($TempArchive)
    } catch {
        Write-Host "❌ Downloaded file invalid (could not open the .skill archive). Aborting."
        exit 1
    }

    try {
        $SkillEntry = $Archive.GetEntry("$SkillName/SKILL.md")
        if (-not $SkillEntry) {
            Write-Host "❌ Downloaded file invalid (missing $SkillName/SKILL.md). Aborting."
            exit 1
        }

        $Reader = New-Object System.IO.StreamReader($SkillEntry.Open())
        try {
            $PackagedSkillMd = $Reader.ReadToEnd()
        } finally {
            $Reader.Dispose()
        }
    } finally {
        $Archive.Dispose()
    }

    $SkillNamePattern = [regex]::Escape($SkillName)
    if (-not [regex]::IsMatch($PackagedSkillMd, "(?m)^name:\s*$SkillNamePattern\s*$")) {
        Write-Host "❌ Downloaded file invalid (not a valid skill archive or missing skill name). Aborting."
        exit 1
    }

    $VersionPattern = '(?m)^\s+version:\s*[''"]?([^''"\r\n]+)[''"]?\s*$'
    $SourceCommitPattern = '(?m)^\s+source_commit:\s*[''"]?([^''"\r\n]+)[''"]?\s*$'
    $DownloadedVersionMatch = [regex]::Match($PackagedSkillMd, $VersionPattern)
    $DownloadedSourceCommitMatch = [regex]::Match($PackagedSkillMd, $SourceCommitPattern)
    $DownloadedVersion = if ($DownloadedVersionMatch.Success) { $DownloadedVersionMatch.Groups[1].Value } else { "" }
    $DownloadedSourceCommit = if ($DownloadedSourceCommitMatch.Success) { $DownloadedSourceCommitMatch.Groups[1].Value } else { "" }

    if (-not $DownloadedVersion -or $DownloadedVersion -ne $LatestVersion) {
        $ArchiveVersion = if ($DownloadedVersion) { $DownloadedVersion } else { "missing" }
        Write-Host "❌ Downloaded archive version mismatch."
        Write-Host "   release.json: $LatestVersion"
        Write-Host "   archive:      $ArchiveVersion"
        exit 1
    }

    if (-not $DownloadedSourceCommit -or $DownloadedSourceCommit -ne $LatestSourceCommit) {
        $ArchiveSourceCommit = if ($DownloadedSourceCommit) { $DownloadedSourceCommit } else { "missing" }
        Write-Host "❌ Downloaded archive source commit mismatch."
        Write-Host "   release.json: $LatestSourceCommit"
        Write-Host "   archive:      $ArchiveSourceCommit"
        exit 1
    }

    if (-not $TargetDir) {
        $TargetDir = $PersonalSkillDir
    }

    Write-Host "   Installing into $TargetDir..."
    $Installer = Join-Path $ScriptDir "install.py"
    if (-not (Test-Path -LiteralPath $Installer)) {
        Write-Host "❌ Missing installer helper: $Installer"
        Write-ManualReinstall
        exit 1
    }

    $Python = Find-Python
    if (-not $Python) {
        Write-Host "❌ python3 or python is required to install the downloaded update."
        Write-ManualReinstall
        exit 1
    }

    $Arguments = @($Installer, "--from-archive", $TempArchive, "--install-dir", $TargetDir)
    & $Python.Source @Arguments | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install the downloaded update."
        Write-ManualReinstall
        exit 1
    }

    Write-Host ""
    Write-Host "✅ Updated: $InstalledVersion → $LatestVersion"
    Write-Host "   Restart Claude Code for the new version to take effect."
}
finally {
    if (Test-Path -LiteralPath $TempArchive) {
        Remove-Item -LiteralPath $TempArchive -Force
    }
}
