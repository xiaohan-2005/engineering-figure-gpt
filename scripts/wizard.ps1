param(
    [string]$SkillDir = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"
$efg = Join-Path $SkillDir "scripts/efg.py"
$promptBuilder = Join-Path $SkillDir "scripts/build_engineering_figure_prompt.py"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python not found in PATH." }
if (-not (Test-Path $efg)) { throw "Missing CLI: $efg" }

function Ask-Choice($title, $options, $defaultIndex) {
    Write-Host ""
    Write-Host $title -ForegroundColor Cyan
    for ($i = 0; $i -lt $options.Count; $i++) {
        Write-Host ("[{0}] {1}" -f ($i + 1), $options[$i])
    }
    $raw = Read-Host ("Select 1-{0} (default {1})" -f $options.Count, ($defaultIndex + 1))
    if (-not $raw) { return $defaultIndex }
    $parsed = 0
    if (-not [int]::TryParse($raw, [ref]$parsed)) { return $defaultIndex }
    $value = $parsed - 1
    if ($value -lt 0 -or $value -ge $options.Count) { return $defaultIndex }
    return $value
}

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

function Add-EndpointOverride([System.Collections.ArrayList]$ArgsList) {
    $endpoint = Ask-Choice "Connection" @(
        "Reuse active Codex / CC Switch provider (recommended)",
        "Manually override with a trusted OpenAI-compatible relay"
    ) 0
    if ($endpoint -eq 1) {
        $baseUrl = Read-Host "Relay Base URL (for example https://relay.example/v1)"
        if (-not $baseUrl) { throw "Relay Base URL is required." }
        if (-not (Ask-YesNo "I trust this relay with the configured API key and any input images" $false)) {
            throw "Relay use cancelled because trust was not confirmed."
        }
        [void]$ArgsList.Add("--base-url")
        [void]$ArgsList.Add($baseUrl)
        [void]$ArgsList.Add("--allow-third-party")
    }
}

function Add-OptionalFinalModelRoute([System.Collections.ArrayList]$ArgsList) {
    if (Ask-YesNo "Use the configured final/high-resolution model route (--final)? This is separate from the visual quality profile" $false) {
        [void]$ArgsList.Add("--final")
    }
}

function Maybe-DryRun([System.Collections.ArrayList]$ArgsList) {
    $live = Ask-YesNo "Call the live image API now? This may use paid credits" $false
    if (-not $live) {
        Write-Host "Dry-run only; no image credits will be used." -ForegroundColor Yellow
        [void]$ArgsList.Add("--dry-run")
    }
}

Write-Host "Engineering Figure GPT Wizard" -ForegroundColor Cyan
Write-Host "1. Build conceptual-figure prompt only"
Write-Host "2. Generate a conceptual figure"
Write-Host "3. Edit an existing figure"
Write-Host "4. Verify raster size / format / aspect"
Write-Host "5. Check active image provider compatibility"
Write-Host "6. Build + render exact plot"
Write-Host "7. Run offline runtime check"
$choice = Read-Host "Choose 1-7"

if ($choice -eq "1") {
    Write-Host "" -ForegroundColor Yellow
    Write-Host "Available templates:" -ForegroundColor Yellow
    & python $promptBuilder --list-templates
    $template = Read-Host "Template"
    $lang = Read-Host "Language (zh/en; Enter for auto)"
    $profile = @("draft", "paper", "final")[(Ask-Choice "Image quality profile" @("draft", "paper - default paper-ready constraints", "final - strongest final-export constraints") 1)]
    $background = Read-Host "Technical/modeling background"
    $argsList = [System.Collections.ArrayList]@($efg, "prompt", $background, "--figure-template", $template, "--quality-profile", $profile)
    Add-IfValue $argsList "--lang" $lang
    & python @argsList
    exit $LASTEXITCODE
}

if ($choice -eq "2") {
    Write-Host "" -ForegroundColor Yellow
    Write-Host "Available templates:" -ForegroundColor Yellow
    & python $promptBuilder --list-templates
    $template = Read-Host "Template (optional; Enter if the text is already the figure request)"
    $lang = Read-Host "Language (zh/en; Enter for auto)"
    $profile = @("draft", "paper", "final")[(Ask-Choice "Image quality profile" @("draft - fast structural iteration", "paper - recommended", "final - strongest prompt/render constraints") 1)]
    $background = Read-Host "Scientific/modeling background or final image request"
    $style = Read-Host "Optional style note"
    $savePrompt = Read-Host "Save resolved prompt path (default output/final-prompt.txt)"
    if (-not $savePrompt) { $savePrompt = "output/final-prompt.txt" }

    $argsList = [System.Collections.ArrayList]@($efg, "image", $background, "--quality-profile", $profile, "--save-prompt", $savePrompt)
    Add-IfValue $argsList "--figure-template" $template
    Add-IfValue $argsList "--lang" $lang
    Add-IfValue $argsList "--style-note" $style
    Add-OptionalFinalModelRoute $argsList
    Add-EndpointOverride $argsList
    Maybe-DryRun $argsList
    & python @argsList
    exit $LASTEXITCODE
}

if ($choice -eq "3") {
    $inputImage = Read-Host "Primary figure image path"
    if (-not $inputImage) { throw "Input image path is required." }
    $mode = @("correct", "revise", "restyle", "redraw")[(Ask-Choice "Edit mode" @(
        "correct - smallest possible fix",
        "revise - local content/structure change",
        "restyle - visual style only",
        "redraw - clean reconstruction"
    ) 0)]
    $instruction = Read-Host "Exact edit instruction"
    if (-not $instruction) { throw "Edit instruction is required." }
    $profile = @("draft", "paper", "final")[(Ask-Choice "Image quality profile" @("draft", "paper - recommended", "final - strongest prompt/render constraints") 1)]
    $preserve = Read-Host "Optional must-preserve item (Enter to skip)"
    $allowChange = Read-Host "Optional explicitly allowed change (Enter to skip)"
    $reference = Read-Host "Optional additional reference image (Enter to skip)"
    $mask = Read-Host "Optional spatial edit mask (same size/format as primary image, with alpha; Enter to skip)"
    $savePrompt = Read-Host "Save edit prompt path (default output/edit-prompt.txt)"
    if (-not $savePrompt) { $savePrompt = "output/edit-prompt.txt" }

    $argsList = [System.Collections.ArrayList]@($efg, "edit", $inputImage, $instruction, "--mode", $mode, "--quality-profile", $profile, "--save-prompt", $savePrompt)
    Add-IfValue $argsList "--preserve" $preserve
    Add-IfValue $argsList "--allow-change" $allowChange
    Add-IfValue $argsList "--reference-image" $reference
    Add-IfValue $argsList "--mask" $mask
    Add-OptionalFinalModelRoute $argsList
    Add-EndpointOverride $argsList
    Maybe-DryRun $argsList
    & python @argsList
    exit $LASTEXITCODE
}

if ($choice -eq "4") {
    $image = Read-Host "Raster image path"
    if (-not $image) { throw "Image path is required." }
    $expected = Read-Host "Exact expected size WIDTHxHEIGHT (Enter to skip)"
    $minWidth = Read-Host "Minimum width px (Enter to skip)"
    $minHeight = Read-Host "Minimum height px (Enter to skip)"
    $format = Read-Host "Required format png/jpeg/webp (Enter to skip)"
    $argsList = [System.Collections.ArrayList]@($efg, "verify-image", $image)
    Add-IfValue $argsList "--expected-size" $expected
    Add-IfValue $argsList "--min-width" $minWidth
    Add-IfValue $argsList "--min-height" $minHeight
    Add-IfValue $argsList "--require-format" $format
    & python @argsList
    exit $LASTEXITCODE
}

if ($choice -eq "5") {
    $argsList = [System.Collections.ArrayList]@($efg, "provider-check")
    Add-EndpointOverride $argsList
    $model = Read-Host "Image model override (Enter for configured/default model)"
    Add-IfValue $argsList "--model" $model
    Write-Host "Provider check probes route/model exposure without generating an image." -ForegroundColor Yellow
    & python @argsList
    exit $LASTEXITCODE
}

if ($choice -eq "6") {
    $request = Read-Host "Concise plot request JSON path"
    $spec = Read-Host "Normalized spec output path (default output/spec.json)"
    if (-not $spec) { $spec = "output/spec.json" }
    $out = Read-Host "Figure output base path (default output/figure)"
    if (-not $out) { $out = "output/figure" }
    & python $efg plot $request --spec-out $spec --out-path $out --formats png pdf svg
    exit $LASTEXITCODE
}

if ($choice -eq "7") {
    & python $efg check
    exit $LASTEXITCODE
}

throw "Unknown choice: $choice"
