param(
    [string]$SourceDir = (Split-Path -Parent $PSScriptRoot),
    [string]$CodexHome = "$HOME/.codex"
)

$ErrorActionPreference = "Stop"
$skillsDir = Join-Path $CodexHome "skills"
$target = Join-Path $skillsDir "engineering-figure-gpt"
$syncScript = Join-Path $SourceDir "scripts/sync_codex_skill.py"

New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python not found in PATH." }
if (-not (Test-Path $syncScript)) { throw "Missing sync script: $syncScript" }

& python $syncScript --target $target
if ($LASTEXITCODE -ne 0) { throw "Runtime sync failed." }

Write-Host "Installed Engineering Figure GPT to $target" -ForegroundColor Green
Write-Host "Repository-only docs, examples, tests and CI files were intentionally not copied into the Codex runtime." -ForegroundColor Yellow
