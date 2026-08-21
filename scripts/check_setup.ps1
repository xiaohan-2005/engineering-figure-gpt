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
    "scripts/image_model_policy.py",
    "scripts/codex_provider_config.py",
    "scripts/build_engineering_figure_prompt.py",
    "scripts/build_image_edit_prompt.py",
    "scripts/verify_image_output.py",
    "scripts/build_plot_spec.py",
    "scripts/plot_publication_figure.py",
    "assets/prompt-templates/engineering-figure-templates.json",
    "assets/prompt-templates/mathematical-modeling-templates.json",
    "assets/prompt-templates/image-quality-contracts.json",
    "references/image-quality-contract.md",
    "references/edit-mode.md",
    "references/visual-qa.md"
)
foreach ($rel in $required) {
    if (Test-Path (Join-Path $SkillDir $rel)) { Status "PASS" "Found $rel" }
    else { Status "FAIL" "Missing $rel"; $failed = $true }
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    $pillowVersion = python -c "import PIL; print(PIL.__version__)" 2>$null
    if ($LASTEXITCODE -eq 0 -and $pillowVersion) { Status "PASS" "Pillow available for verify-image: $pillowVersion" }
    else { Status "FAIL" "Pillow missing; install requirements.txt so verify-image can inspect raster outputs"; $failed = $true }
}

$systemImagen = "$HOME/.codex/skills/.system/imagen/SKILL.md"
if (Test-Path $systemImagen) {
    Status "PASS" "Codex built-in imagen skill detected"
} else {
    Status "WARN" "Built-in imagen skill not detected; portable GPT Image CLI fallback can still be used"
    $warned = $true
}

$codexConfig = "$HOME/.codex/config.toml"
$codexAuth = "$HOME/.codex/auth.json"
if (Test-Path $codexConfig) { Status "PASS" "Codex live config detected: $codexConfig" }
else { Status "WARN" "Codex config.toml not found"; $warned = $true }
if (Test-Path $codexAuth) { Status "PASS" "Codex auth file detected: $codexAuth" }
else { Status "WARN" "Codex auth.json not found"; $warned = $true }

$providerReady = $false
$keyReady = $false
if (Get-Command python -ErrorAction SilentlyContinue -and (Test-Path (Join-Path $SkillDir "scripts/codex_provider_config.py"))) {
    Push-Location $SkillDir
    $providerJson = python scripts/codex_provider_config.py 2>$null
    $providerExit = $LASTEXITCODE
    Pop-Location
    if ($providerExit -eq 0 -and $providerJson) {
        try {
            $provider = ($providerJson -join "`n") | ConvertFrom-Json
            if ($provider.configured) {
                $providerReady = $true
                Status "PASS" "Active Codex provider: $($provider.provider_name)"
                if ($provider.base_url) { Write-Host "       Base URL: $($provider.base_url)" -ForegroundColor Cyan }
                if ($provider.wire_api) { Write-Host "       Wire API: $($provider.wire_api)" -ForegroundColor Cyan }
                if ($provider.has_api_key) {
                    Status "PASS" "Reusable Codex/CC Switch API credential detected (secret not displayed)"
                    $keyReady = $true
                } else {
                    Status "WARN" "Active Codex provider found, but no reusable API key was detected in config.toml/auth.json"
                    $warned = $true
                }
                Write-Host "       Image compatibility is separate from Codex text compatibility." -ForegroundColor DarkGray
                Write-Host "       Optional check: python scripts/efg.py provider-check" -ForegroundColor Cyan
            }
        } catch {
            Status "WARN" "Could not parse sanitized Codex provider diagnostics"
            $warned = $true
        }
    }
}

if (-not $providerReady) {
    if ($env:OPENAI_BASE_URL) {
        Status "WARN" "No active Codex provider was resolved; falling back to OPENAI_BASE_URL=$env:OPENAI_BASE_URL"
        $warned = $true
    } else {
        Status "PASS" "No custom Codex provider resolved; portable fallback defaults to official OpenAI"
    }

    if ($env:OPENAI_API_KEY) {
        Status "PASS" "OPENAI_API_KEY is set for fallback"
        $keyReady = $true
    } else {
        $keyFile = if ($env:OPENAI_API_KEY_FILE) { $env:OPENAI_API_KEY_FILE } else { Join-Path $SecretsDir "openai_api_key.txt" }
        if (Test-Path $keyFile) {
            $value = (Get-Content -Raw -Path $keyFile).Trim()
            if ($value -and -not $value.StartsWith("REPLACE_")) {
                Status "PASS" "Fallback API key file found"
                $keyReady = $true
            }
        }
    }
}

$routineModel = if ($env:OPENAI_IMAGE_MODEL) { $env:OPENAI_IMAGE_MODEL } else { "gpt-image-2" }
Status "PASS" "Routine image model: $routineModel"
if ($env:OPENAI_IMAGE_HIGHRES_MODEL) {
    Status "PASS" "Final/high-resolution image model configured: $env:OPENAI_IMAGE_HIGHRES_MODEL"
} else {
    Status "WARN" "OPENAI_IMAGE_HIGHRES_MODEL is not configured"
    Write-Host "       Routine image generation can still work; --final/--highres remains fail-closed." -ForegroundColor Yellow
    $warned = $true
}

if (-not $keyReady) {
    Status "WARN" "No reusable image API credential detected; Plot Mode, prompt building, edit dry-runs, and raster verification still work"
    $warned = $true
}

if (Get-Command python -ErrorAction SilentlyContinue -and (Test-Path (Join-Path $SkillDir "scripts/efg.py"))) {
    Push-Location $SkillDir
    python scripts/efg.py check
    if ($LASTEXITCODE -eq 0) { Status "PASS" "Offline CLI smoke check passed" }
    else { Status "FAIL" "Offline CLI smoke check failed"; $failed = $true }
    Pop-Location
}

Write-Host ""
Write-Host "Key image workflows:" -ForegroundColor Cyan
Write-Host "  python scripts/efg.py image ... --quality-profile paper"
Write-Host "  python scripts/efg.py edit figure.png \"fix one label only\" --mode correct --dry-run"
Write-Host "  python scripts/efg.py verify-image output/figure.png --expected-size 1536x1024 --require-format png"

Write-Host ""
if ($failed) {
    Write-Host "Readiness: BLOCKED" -ForegroundColor Red
    exit 1
}
if ($warned) {
    Write-Host "Readiness: READY WITH WARNINGS" -ForegroundColor Yellow
    exit 0
}
Write-Host "Readiness: READY" -ForegroundColor Green
exit 0
