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

function EnvFlagEnabled([string]$value) {
    if (-not $value) { return $false }
    return @("1", "true", "yes", "on") -contains $value.Trim().ToLowerInvariant()
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
    "scripts/build_engineering_figure_prompt.py",
    "scripts/build_plot_spec.py",
    "scripts/plot_publication_figure.py",
    "assets/prompt-templates/engineering-figure-templates.json",
    "assets/prompt-templates/mathematical-modeling-templates.json"
)
foreach ($rel in $required) {
    if (Test-Path (Join-Path $SkillDir $rel)) { Status "PASS" "Found $rel" }
    else { Status "FAIL" "Missing $rel"; $failed = $true }
}

$systemImagen = "$HOME/.codex/skills/.system/imagen/SKILL.md"
if (Test-Path $systemImagen) {
    Status "PASS" "Codex built-in imagen skill detected; use this as the preferred in-agent image path"
} else {
    Status "WARN" "Built-in imagen skill not detected; portable GPT Image CLI fallback can still be used"
    $warned = $true
}

$baseUrl = if ($env:OPENAI_BASE_URL) { $env:OPENAI_BASE_URL.TrimEnd('/') } else { "https://api.openai.com/v1" }
$isOfficial = $baseUrl -eq "https://api.openai.com/v1"
$thirdPartyAllowed = EnvFlagEnabled $env:OPENAI_ALLOW_THIRD_PARTY

if ($isOfficial) {
    Status "PASS" "Image API base URL uses official OpenAI: $baseUrl"
} elseif ($thirdPartyAllowed) {
    Status "WARN" "Trusted custom relay enabled: $baseUrl"
    Write-Host "       The relay can receive the configured API key and images used for edits." -ForegroundColor Yellow
    Write-Host "       Optional compatibility probe: python scripts/efg.py provider-check" -ForegroundColor Cyan
    $warned = $true
} else {
    Status "WARN" "Custom OPENAI_BASE_URL detected but OPENAI_ALLOW_THIRD_PARTY is not enabled: $baseUrl"
    Write-Host "       Set OPENAI_ALLOW_THIRD_PARTY=1 only if you trust this relay." -ForegroundColor Yellow
    $warned = $true
}

$routineModel = if ($env:OPENAI_IMAGE_MODEL) { $env:OPENAI_IMAGE_MODEL } else { "gpt-image-2" }
Status "PASS" "Routine image model: $routineModel"
if ($env:OPENAI_IMAGE_HIGHRES_MODEL) {
    Status "PASS" "Final/high-resolution model configured: $env:OPENAI_IMAGE_HIGHRES_MODEL"
} else {
    Status "WARN" "OPENAI_IMAGE_HIGHRES_MODEL is not configured"
    Write-Host "       Routine image generation is available; --final/--highres requests will fail closed until a final-quality model is configured or explicitly passed." -ForegroundColor Yellow
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
            Status "PASS" "API key file found for CLI fallback"
            $keyReady = $true
        } else {
            Status "WARN" "API key file is empty or still contains a placeholder"
            $warned = $true
        }
    } else {
        Status "WARN" "No API key configured; this is okay when Codex built-in image generation is available"
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
    if ((-not $isOfficial) -and (-not $thirdPartyAllowed)) { Write-Host "Custom relay is configured but will be refused until explicitly trusted." }
    exit 0
}
Write-Host "Readiness: READY" -ForegroundColor Green
exit 0
