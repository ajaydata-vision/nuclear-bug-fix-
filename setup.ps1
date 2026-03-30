param(
    [switch]$Personal,
    [switch]$Project,
    [string]$InstallDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$SkillName = "nuclear-bug-fix"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Installer = Join-Path $RepoRoot "scripts\install.py"

if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot "SKILL.md"))) {
    throw "setup.ps1 must be run from the repo root containing SKILL.md"
}

$ResolvedRepoRoot = [System.IO.Path]::GetFullPath($RepoRoot)
$CurrentName = [System.IO.Path]::GetFileName($ResolvedRepoRoot)
$ParentName = [System.IO.Path]::GetFileName((Split-Path -Parent $ResolvedRepoRoot))
$InvocationDir = [System.IO.Path]::GetFullPath((Get-Location).Path)
$PersonalTarget = [System.IO.Path]::GetFullPath((Join-Path $HOME ".claude\skills\$SkillName"))
$CurrentIsInstalled = $CurrentName -eq $SkillName -and $ParentName -eq "skills"

if ($Personal -and $Project) {
    throw "Use either -Personal or -Project, not both"
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    $Python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $Python) {
    throw "python3 or python is required"
}

$RequestedTarget = $null
if ($InstallDir) {
    $RequestedTarget = [System.IO.Path]::GetFullPath($InstallDir)
} elseif ($Personal) {
    $RequestedTarget = $PersonalTarget
} elseif ($Project) {
    if ($CurrentIsInstalled -and $ResolvedRepoRoot -ne $PersonalTarget) {
        $RequestedTarget = $ResolvedRepoRoot
    } else {
        if (
            $InvocationDir -eq $ResolvedRepoRoot -or
            $InvocationDir.StartsWith($ResolvedRepoRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
        ) {
            throw "-Project from a personal install must be run from the target project root or with -InstallDir"
        }
        $RequestedTarget = [System.IO.Path]::GetFullPath((Join-Path $InvocationDir ".claude\skills\$SkillName"))
    }
} elseif ($CurrentIsInstalled) {
    $RequestedTarget = $ResolvedRepoRoot
} else {
    $RequestedTarget = $PersonalTarget
}

if ($RequestedTarget -eq $ResolvedRepoRoot) {
    Write-Host "$SkillName is already installed at $ResolvedRepoRoot"
    Write-Host "Restart Claude Code if it is already running."
    exit 0
}

$Arguments = @($Installer, "--repo-root", $ResolvedRepoRoot, "--install-dir", $RequestedTarget)

& $Python.Source @Arguments
exit $LASTEXITCODE
