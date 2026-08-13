param(
    [string]$SourceDir = (Split-Path -Parent $PSScriptRoot),
    [string]$CodexHome = "$HOME/.codex",
    [switch]$SkipDependencies
)

$ErrorActionPreference = "Stop"
$installScript = Join-Path $SourceDir "scripts/install_skill.ps1"
$requirements = Join-Path $SourceDir "requirements.txt"
$target = Join-Path (Join-Path $CodexHome "skills") "engineering-figure-gpt"
$check = Join-Path $target "scripts/check_setup.ps1"

if (-not $SkipDependencies) {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python not found in PATH." }
    & python -m pip install -r $requirements
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
}

& $installScript -SourceDir $SourceDir -CodexHome $CodexHome
if ($LASTEXITCODE -ne 0) { throw "Skill installation failed." }

if (-not (Test-Path $check)) { throw "Setup check missing after installation: $check" }
& $check -SkillDir $target -SecretsDir (Join-Path $CodexHome "secrets")
exit $LASTEXITCODE
