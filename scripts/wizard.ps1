param(
    [string]$SkillDir = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"
$efg = Join-Path $SkillDir "scripts/efg.py"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python not found in PATH." }
if (-not (Test-Path $efg)) { throw "Missing CLI: $efg" }

Write-Host "Engineering Figure GPT Wizard" -ForegroundColor Cyan
Write-Host "1. Build conceptual-figure prompt"
Write-Host "2. Test or run GPT image fallback"
Write-Host "3. Build and render exact plot"
Write-Host "4. Run offline setup check"
$choice = Read-Host "Choose 1-4"

if ($choice -eq "1") {
    Write-Host "Templates: system-architecture, algorithm-workflow, graphical-abstract, mathematical-model-framework, data-analysis-pipeline, optimization-workflow, evaluation-framework, electronic-schematic" -ForegroundColor Yellow
    $template = Read-Host "Template"
    $lang = Read-Host "Language (zh/en)"
    $background = Read-Host "Technical/modeling background"
    & python $efg prompt --figure-template $template --lang $lang $background
    exit $LASTEXITCODE
}

if ($choice -eq "2") {
    $prompt = Read-Host "Image prompt"
    $live = Read-Host "Call the live OpenAI image API? This may use paid credits. Type YES to continue"
    if ($live -eq "YES") {
        & python $efg image $prompt
    } else {
        Write-Host "Running dry-run only; no image API credits will be used." -ForegroundColor Yellow
        & python $efg image $prompt --dry-run
    }
    exit $LASTEXITCODE
}

if ($choice -eq "3") {
    $request = Read-Host "Concise plot request JSON path"
    $spec = Read-Host "Spec output path (default output/spec.json)"
    if (-not $spec) { $spec = "output/spec.json" }
    $out = Read-Host "Figure output base path (default output/figure)"
    if (-not $out) { $out = "output/figure" }
    & python $efg build-plot $request --out $spec
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & python $efg plot $spec --out-path $out --formats png pdf svg
    exit $LASTEXITCODE
}

if ($choice -eq "4") {
    & python $efg check
    exit $LASTEXITCODE
}

throw "Unknown choice: $choice"
