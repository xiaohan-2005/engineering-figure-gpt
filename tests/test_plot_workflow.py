import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_multi_panel_plot_workflow(tmp_path):
    request = {
        "layout": {"nrows": 1, "ncols": 3, "figsize": [12, 4], "width_ratios": [1, 1, 0.25]},
        "panels": [
            {
                "kind": "bar",
                "title": "Comparison",
                "annotate": True,
                "legend": False,
                "data": {"categories": ["AUC", "F1"], "series": {"Ours": [0.92, 0.88], "Base": [0.85, 0.82]}},
                "colors": {"Ours": "blue_main", "Base": "red"}
            },
            {
                "kind": "heatmap",
                "title": "Matrix",
                "annotate": True,
                "data": {"matrix": [[1.0, 0.4], [0.4, 1.0]], "x_labels": ["A", "B"], "y_labels": ["A", "B"]}
            },
            {"kind": "legend", "source_panel": 0}
        ]
    }
    request_path = tmp_path / "request.json"
    spec_path = tmp_path / "spec.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")

    build = subprocess.run([sys.executable, str(ROOT / "scripts/build_plot_spec.py"), str(request_path), "--out", str(spec_path)], capture_output=True, text=True)
    assert build.returncode == 0, build.stderr
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    assert [p["type"] for p in spec["panels"]] == ["bar", "heatmap", "legend"]

    out_base = tmp_path / "figure"
    render = subprocess.run([sys.executable, str(ROOT / "scripts/plot_publication_figure.py"), str(spec_path), "--out-path", str(out_base), "--formats", "png", "svg"], capture_output=True, text=True)
    assert render.returncode == 0, render.stderr
    assert out_base.with_suffix(".png").is_file()
    assert out_base.with_suffix(".svg").is_file()


def test_trend_and_scatter_build(tmp_path):
    request = {
        "panels": [
            {"kind": "trend", "data": {"x": [1, 2, 3], "series": {"train": [0.3, 0.2, 0.1]}, "shadow": {"train": [0.02, 0.02, 0.01]}}},
            {"kind": "scatter", "data": {"series": [{"label": "Ours", "x": [10], "y": [0.92], "color": "blue_main"}]}}
        ]
    }
    req = tmp_path / "request.json"
    req.write_text(json.dumps(request), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/build_plot_spec.py"), str(req)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    spec = json.loads(proc.stdout)
    assert spec["panels"][0]["type"] == "trend"
    assert spec["panels"][1]["type"] == "scatter"
