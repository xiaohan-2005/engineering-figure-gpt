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

# Full local Plot Mode E2E test:
# concise request -> normalized plot spec -> renderer -> non-empty PNG.
# This performs no network request and has no API cost.
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("engineering-figure-gpt-smoke-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
try {
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
    & python scripts/build_plot_spec.py $requestPath --out $specPath
    $buildExit = $LASTEXITCODE
    if ($buildExit -eq 0) {
        & python scripts/plot_publication_figure.py $specPath --out-path $outBase --formats png
        $plotExit = $LASTEXITCODE
    } else {
        $plotExit = 1
    }
    Pop-Location

    if ($buildExit -ne 0) { throw "Plot request normalization failed with exit code $buildExit." }
    if ($plotExit -ne 0) { throw "Plot renderer failed with exit code $plotExit." }

    $png = "$outBase.png"
    if (-not (Test-Path $png)) { throw "Plot E2E smoke test did not create $png" }
    if ((Get-Item $png).Length -le 0) { throw "Plot E2E smoke test created an empty PNG." }
    Write-Host "[PASS] Plot request -> spec -> renderer E2E produced a non-empty PNG" -ForegroundColor Green
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
        & python scripts/generate_image.py "Minimal publication-style scientific workflow diagram with three labeled modules on a white background." --quality low --size 1024x1024 --out-dir $liveTemp
        $imageExit = $LASTEXITCODE
        Pop-Location
        if ($imageExit -ne 0) { throw "Live GPT image test failed with exit code $imageExit." }
        $generated = Get-ChildItem $liveTemp -File | Where-Object { $_.Length -gt 0 }
        if (-not $generated) { throw "Live GPT image test returned no non-empty output file." }
        Write-Host "[PASS] Optional live GPT image test produced a non-empty output" -ForegroundColor Green
    }
    finally {
        if (Test-Path $liveTemp) { Remove-Item -Recurse -Force $liveTemp }
    }
}

Write-Host "Engineering Figure GPT install-and-test completed successfully." -ForegroundColor Green
exit 0
