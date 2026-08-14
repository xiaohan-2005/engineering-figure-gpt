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

# Real local plot E2E smoke test: create a temporary normalized plot spec,
# render an actual PNG through the installed runtime, verify non-zero bytes,
# then clean up. This performs no network request and has no API cost.
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("engineering-figure-gpt-smoke-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
try {
    $specPath = Join-Path $tempDir "plot-spec.json"
    $outBase = Join-Path $tempDir "plot-smoke"
    @'
{
  "layout": {"rows": 1, "cols": 1, "figsize": [6, 4]},
  "panels": [
    {
      "kind": "bar",
      "title": "Installation Smoke Test",
      "ylabel": "Value",
      "data": {
        "categories": ["A", "B", "C"],
        "series": [
          {"label": "Series", "values": [1.0, 1.5, 2.0]}
        ]
      },
      "annotate": true,
      "legend": false
    }
  ]
}
'@ | Set-Content -Encoding UTF8 $specPath

    Push-Location $target
    & python scripts/plot_publication_figure.py $specPath --out-path $outBase --formats png
    $plotExit = $LASTEXITCODE
    Pop-Location
    if ($plotExit -ne 0) { throw "Plot E2E smoke test failed with exit code $plotExit." }

    $png = "$outBase.png"
    if (-not (Test-Path $png)) { throw "Plot E2E smoke test did not create $png" }
    if ((Get-Item $png).Length -le 0) { throw "Plot E2E smoke test created an empty PNG." }
    Write-Host "[PASS] Plot E2E smoke test rendered a non-empty PNG" -ForegroundColor Green
}
finally {
    if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir }
}

# Live image generation is opt-in because it performs a paid network request.
if ($TestLiveImage) {
    Push-Location $target
    & python scripts/generate_image.py "Minimal publication-style scientific workflow diagram with three labeled modules on a white background." --quality low --size 1024x1024 --out-dir (Join-Path $tempDir "live-image")
    $imageExit = $LASTEXITCODE
    Pop-Location
    if ($imageExit -ne 0) { throw "Live GPT image test failed with exit code $imageExit." }
    Write-Host "[PASS] Optional live GPT image test completed" -ForegroundColor Green
}

Write-Host "Engineering Figure GPT install-and-test completed successfully." -ForegroundColor Green
exit 0
