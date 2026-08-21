param(
    [string]$SourceDir = (Split-Path -Parent $PSScriptRoot),
    [string]$CodexHome = "$HOME/.codex",
    [switch]$SkipDependencies,
    [switch]$TestLiveImage
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
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Local offline E2E tests. These perform no network request and use no image credits.
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("engineering-figure-gpt-smoke-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
try {
    # Plot request -> normalized plot spec -> renderer -> non-empty PNG.
    $requestPath = Join-Path $tempDir "plot-request.json"
    $specPath = Join-Path $tempDir "plot-spec.json"
    $outBase = Join-Path $tempDir "plot-smoke"
    @'
{
  "layout": {"nrows": 1, "ncols": 1, "figsize": [6, 4]},
  "panels": [
    {
      "kind": "bar",
      "title": "Installation Smoke Test",
      "ylabel": "Value",
      "data": {
        "categories": ["A", "B", "C"],
        "series": {
          "Series": [1.0, 1.5, 2.0]
        }
      },
      "annotate": true,
      "legend": false
    }
  ]
}
'@ | Set-Content -Encoding UTF8 $requestPath

    Push-Location $target
    & python scripts/efg.py plot $requestPath --spec-out $specPath --out-path $outBase --formats png
    $plotExit = $LASTEXITCODE
    Pop-Location

    if ($plotExit -ne 0) { throw "Plot E2E smoke test failed with exit code $plotExit." }
    $png = "$outBase.png"
    if (-not (Test-Path $png)) { throw "Plot E2E smoke test did not create $png" }
    if ((Get-Item $png).Length -le 0) { throw "Plot E2E smoke test created an empty PNG." }
    Write-Host "[PASS] Plot request -> spec -> renderer E2E produced a non-empty PNG" -ForegroundColor Green

    # Edit contract -> GPT edit dry-run. This validates preservation-first prompt construction without API cost.
    $editPrompt = Join-Path $tempDir "edit-prompt.txt"
    Push-Location $target
    & python scripts/efg.py edit $png "Fix one label only; change nothing else" --mode correct --save-prompt $editPrompt --dry-run
    $editExit = $LASTEXITCODE
    Pop-Location
    if ($editExit -ne 0) { throw "Edit dry-run smoke test failed with exit code $editExit." }
    if (-not (Test-Path $editPrompt)) { throw "Edit dry-run did not preserve the resolved edit prompt." }
    $editText = Get-Content -Raw -Path $editPrompt
    if ($editText -notmatch "smallest possible correction") { throw "Edit prompt is missing preservation-first correction rules." }
    if ($editText -notmatch "Publication Image Quality Contract") { throw "Edit prompt is missing the image quality contract." }
    Write-Host "[PASS] Edit mode built a preservation-first quality-constrained prompt" -ForegroundColor Green

    # Raster verifier -> exact dimensions/format.
    $qualityPng = Join-Path $tempDir "quality-contract-smoke.png"
    & python -c "from PIL import Image; Image.new('RGB',(1536,1024),'white').save(r'$qualityPng')"
    if ($LASTEXITCODE -ne 0) { throw "Could not create local raster verification fixture." }
    Push-Location $target
    & python scripts/efg.py verify-image $qualityPng --expected-size 1536x1024 --require-format png --min-megapixels 1.5
    $verifyExit = $LASTEXITCODE
    Pop-Location
    if ($verifyExit -ne 0) { throw "Raster verification smoke test failed with exit code $verifyExit." }
    Write-Host "[PASS] Raster verifier enforced exact size/format constraints" -ForegroundColor Green
}
finally {
    if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir }
}

# Live image generation is opt-in because it performs a paid network request.
if ($TestLiveImage) {
    $liveTemp = Join-Path ([System.IO.Path]::GetTempPath()) ("engineering-figure-gpt-live-" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force -Path $liveTemp | Out-Null
    try {
        Push-Location $target
        & python scripts/efg.py image "Minimal publication-style scientific workflow diagram with three large readable labeled modules on a white background." --quality-profile paper --quality low --size 1024x1024 --output-format png --out-dir $liveTemp --prefix live-smoke
        $imageExit = $LASTEXITCODE
        Pop-Location
        if ($imageExit -ne 0) { throw "Live GPT image test failed with exit code $imageExit." }
        $generated = Get-ChildItem $liveTemp -Filter "live-smoke-*.png" -File | Where-Object { $_.Length -gt 0 }
        if (-not $generated) { throw "Live GPT image test returned no non-empty PNG output file." }

        foreach ($file in $generated) {
            Push-Location $target
            & python scripts/efg.py verify-image $file.FullName --expected-size 1024x1024 --require-format png
            $verifyLiveExit = $LASTEXITCODE
            Pop-Location
            if ($verifyLiveExit -ne 0) {
                throw "Live provider returned an artifact that failed the requested 1024x1024 PNG contract: $($file.FullName)"
            }
        }
        Write-Host "[PASS] Optional live GPT image test produced and verified the requested raster output" -ForegroundColor Green
    }
    finally {
        if (Test-Path $liveTemp) { Remove-Item -Recurse -Force $liveTemp }
    }
}

Write-Host "Engineering Figure GPT install-and-test completed successfully." -ForegroundColor Green
exit 0
