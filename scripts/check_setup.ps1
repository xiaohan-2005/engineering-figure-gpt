param(
    [string]$SkillDir = "$HOME/.codex/skills/engineering-figure-gpt",
    [string]$SecretsDir = "$HOME/.codex/secrets"
)

$ErrorActionPreference = "Continue"
$failed = $false
$warned = $false

function Status([string]$kind, [string]$message) {
    if ($kind -eq "PASS") { Write-Host "[PASS] $message" -ForegroundColor Green }
    elseif ($kind -eq "WARN") { Write-Host "[WARN] $message" -ForegroundColor Yellow }
    else { Write-Host "[FAIL] $message" -ForegroundColor Red }
}

Write-Host "Engineering Figure GPT setup check" -ForegroundColor Cyan
Write-Host "SkillDir   : $SkillDir"
Write-Host "SecretsDir : $SecretsDir"
Write-Host ""

if (Get-Command python -ErrorAction SilentlyContinue) {
    Status "PASS" "Python detected: $(python --version 2>&1)"
} else {
    Status "FAIL" "Python not found in PATH"
    $failed = $true
}

if (Test-Path $SkillDir) { Status "PASS" "Skill directory exists" } else { Status "FAIL" "Skill directory missing"; $failed = $true }

$required = @(
    "SKILL.md",
    "agents/openai.yaml",
    "scripts/efg.py",
    "scripts/generate_image.py",
    "scripts/build_plot_spec.py",
    "scripts/plot_publication_figure.py",
    "assets/prompt-templates/engineering-figure-templates.json"
)
foreach ($rel in $required) {
    if (Test-Path (Join-Path $SkillDir $rel)) { Status "PASS" "Found $rel" }
    else { Status "FAIL" "Missing $rel"; $failed = $true }
}

$systemImagen = "$HOME/.codex/skills/.system/imagen/SKILL.md"
if (Test-Path $systemImagen) {
    Status "PASS" "Codex built-in imagen skill detected; use this as the preferred image path"
} else {
    Status "WARN" "Built-in imagen skill not detected; portable OpenAI CLI fallback can still be used"
    $warned = $true
}

$keyReady = $false
if ($env:OPENAI_API_KEY) {
    Status "PASS" "OPENAI_API_KEY is set for CLI fallback"
    $keyReady = $true
} else {
    $keyFile = if ($env:OPENAI_API_KEY_FILE) { $env:OPENAI_API_KEY_FILE } else { Join-Path $SecretsDir "openai_api_key.txt" }
    if (Test-Path $keyFile) {
        $value = (Get-Content -Raw -Path $keyFile).Trim()
        if ($value -and -not $value.StartsWith("REPLACE_")) {
            Status "PASS" "OpenAI key file found for CLI fallback"
            $keyReady = $true
        } else {
            Status "WARN" "OpenAI key file is empty or still contains a placeholder"
            $warned = $true
        }
    } else {
        Status "WARN" "No OpenAI API key configured; this is okay when Codex built-in image generation is available"
        $warned = $true
    }
}

if (Get-Command python -ErrorAction SilentlyContinue -and (Test-Path (Join-Path $SkillDir "scripts/efg.py"))) {
    Push-Location $SkillDir
    python scripts/efg.py check
    if ($LASTEXITCODE -eq 0) { Status "PASS" "Offline CLI smoke check passed" }
    else { Status "FAIL" "Offline CLI smoke check failed"; $failed = $true }
    Pop-Location
}

Write-Host ""
if ($failed) {
    Write-Host "Readiness: BLOCKED" -ForegroundColor Red
    exit 1
}
if ($warned) {
    Write-Host "Readiness: READY WITH WARNINGS" -ForegroundColor Yellow
    if (-not $keyReady) { Write-Host "Image CLI fallback will need an API key; Codex built-in image generation may not." }
    exit 0
}
Write-Host "Readiness: READY" -ForegroundColor Green
exit 0
