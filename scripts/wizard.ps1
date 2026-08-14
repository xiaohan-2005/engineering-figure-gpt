param(
    [string]$SkillDir = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"
$efg = Join-Path $SkillDir "scripts/efg.py"
$promptBuilder = Join-Path $SkillDir "scripts/build_engineering_figure_prompt.py"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python not found in PATH." }
if (-not (Test-Path $efg)) { throw "Missing CLI: $efg" }

function Ask-YesNo([string]$Message, [bool]$Default = $false) {
    $suffix = if ($Default) { " [Y/n]" } else { " [y/N]" }
    $value = (Read-Host ($Message + $suffix)).Trim().ToLowerInvariant()
    if (-not $value) { return $Default }
    return $value -in @("y", "yes", "1", "true")
}

function Add-IfValue([System.Collections.ArrayList]$ArgsList, [string]$Flag, [string]$Value) {
    if ($Value) {
        [void]$ArgsList.Add($Flag)
        [void]$ArgsList.Add($Value)
    }
}

Write-Host "Engineering Figure GPT Wizard" -ForegroundColor Cyan
Write-Host "1. Build conceptual-figure prompt only"
Write-Host "2. Generate/edit conceptual figure (one command)"
Write-Host "3. Check official/relay image provider compatibility"
Write-Host "4. Build + render exact plot (one command)"
Write-Host "5. Run offline runtime check"
$choice = Read-Host "Choose 1-5"

if ($choice -eq "1") {
    Write-Host "" -ForegroundColor Yellow
    Write-Host "Available templates:" -ForegroundColor Yellow
    & python $promptBuilder --list-templates
    $template = Read-Host "Template"
    $lang = Read-Host "Language (zh/en; Enter for auto)"
    $background = Read-Host "Technical/modeling background"
    $argsList = [System.Collections.ArrayList]@($efg, "prompt", $background, "--figure-template", $template)
    Add-IfValue $argsList "--lang" $lang
    & python @argsList
    exit $LASTEXITCODE
}

if ($choice -eq "2") {
    Write-Host "" -ForegroundColor Yellow
    Write-Host "Leave Template empty when the text you enter is already the final image prompt." -ForegroundColor Yellow
    & python $promptBuilder --list-templates
    $template = Read-Host "Template (optional)"
    $lang = Read-Host "Language (zh/en; Enter for auto)"
    $background = Read-Host "Scientific background / final prompt"
    $style = Read-Host "Optional style note"
    $savePrompt = Read-Host "Save resolved prompt path (default output/final-prompt.txt)"
    if (-not $savePrompt) { $savePrompt = "output/final-prompt.txt" }

    $provider = Read-Host "Endpoint: [1] official OpenAI  [2] trusted OpenAI-compatible relay (default 1)"
    $baseUrl = ""
    $allowRelay = $false
    if ($provider -eq "2") {
        $baseUrl = Read-Host "Relay Base URL (for example https://relay.example/v1)"
        if (-not $baseUrl) { throw "Relay Base URL is required." }
        $allowRelay = Ask-YesNo "I trust this relay with the configured API key and any input images" $false
        if (-not $allowRelay) { throw "Relay use cancelled because trust was not confirmed." }
    }

    $finalQuality = Ask-YesNo "Request final/high-resolution model routing" $false
    $live = Ask-YesNo "Call the live image API now? This may use paid credits" $false

    $argsList = [System.Collections.ArrayList]@($efg, "image", $background)
    Add-IfValue $argsList "--figure-template" $template
    Add-IfValue $argsList "--lang" $lang
    Add-IfValue $argsList "--style-note" $style
    Add-IfValue $argsList "--save-prompt" $savePrompt
    Add-IfValue $argsList "--base-url" $baseUrl
    if ($allowRelay) { [void]$argsList.Add("--allow-third-party") }
    if ($finalQuality) { [void]$argsList.Add("--final") }
    if (-not $live) {
        Write-Host "Dry-run only; no image credits will be used." -ForegroundColor Yellow
        [void]$argsList.Add("--dry-run")
    }
    & python @argsList
    exit $LASTEXITCODE
}

if ($choice -eq "3") {
    $provider = Read-Host "Endpoint: [1] official OpenAI  [2] trusted relay (default 1)"
    $argsList = [System.Collections.ArrayList]@($efg, "provider-check")
    if ($provider -eq "2") {
        $baseUrl = Read-Host "Relay Base URL"
        if (-not $baseUrl) { throw "Relay Base URL is required." }
        if (-not (Ask-YesNo "I trust this relay with the configured API key" $false)) {
            throw "Relay provider check cancelled."
        }
        [void]$argsList.Add("--base-url")
        [void]$argsList.Add($baseUrl)
        [void]$argsList.Add("--allow-third-party")
    }
    $model = Read-Host "Model override (Enter for configured/default model)"
    Add-IfValue $argsList "--model" $model
    Write-Host "Provider check probes compatibility without generating an image." -ForegroundColor Yellow
    & python @argsList
    exit $LASTEXITCODE
}

if ($choice -eq "4") {
    $request = Read-Host "Concise plot request JSON path"
    $spec = Read-Host "Normalized spec output path (default output/spec.json)"
    if (-not $spec) { $spec = "output/spec.json" }
    $out = Read-Host "Figure output base path (default output/figure)"
    if (-not $out) { $out = "output/figure" }
    & python $efg plot $request --spec-out $spec --out-path $out --formats png pdf svg
    exit $LASTEXITCODE
}

if ($choice -eq "5") {
    & python $efg check
    exit $LASTEXITCODE
}

throw "Unknown choice: $choice"
