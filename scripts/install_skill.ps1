param(
    [string]$SourceDir = (Split-Path -Parent $PSScriptRoot),
    [string]$CodexHome = "$HOME/.codex"
)

$ErrorActionPreference = "Stop"
$skillsDir = Join-Path $CodexHome "skills"
$secretsDir = Join-Path $CodexHome "secrets"
$target = Join-Path $skillsDir "engineering-figure-gpt"
$syncScript = Join-Path $SourceDir "scripts/sync_codex_skill.py"
$keyExample = Join-Path $SourceDir "secrets/openai_api_key.txt.example"
$keyTarget = Join-Path $secretsDir "openai_api_key.txt"

New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
New-Item -ItemType Directory -Force -Path $secretsDir | Out-Null
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python not found in PATH." }
if (-not (Test-Path $syncScript)) { throw "Missing sync script: $syncScript" }

& python $syncScript --target $target
if ($LASTEXITCODE -ne 0) { throw "Runtime sync failed." }

if (-not (Test-Path $keyTarget) -and (Test-Path $keyExample)) {
    Copy-Item -Path $keyExample -Destination $keyTarget
    Write-Host "Created optional OpenAI key placeholder at $keyTarget" -ForegroundColor Yellow
} else {
    Write-Host "Kept existing OpenAI key file/configuration." -ForegroundColor Green
}

Write-Host "Installed Engineering Figure GPT to $target" -ForegroundColor Green
Write-Host "Repository-only docs, examples, tests and CI files were intentionally not copied into the Codex runtime." -ForegroundColor Yellow
Write-Host "The API key is only needed for the portable image CLI fallback; Codex built-in image generation may not require it." -ForegroundColor Cyan
