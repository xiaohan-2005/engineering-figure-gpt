import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_example_plot_renders(tmp_path):
    script = ROOT / "scripts" / "plot_publication_figure.py"
    spec = ROOT / "examples" / "benchmark-plot-request.json"
    out = tmp_path / "benchmark"
    subprocess.run(
        [sys.executable, str(script), str(spec), "--out-path", str(out), "--formats", "png"],
        cwd=ROOT,
        check=True,
    )
    assert out.with_suffix(".png").is_file()
