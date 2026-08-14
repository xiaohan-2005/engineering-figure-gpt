from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_plot_request_to_renderer_smoke_chain(tmp_path):
    request = {
        "layout": {"nrows": 1, "ncols": 1, "figsize": [6, 4]},
        "panels": [
            {
                "kind": "bar",
                "title": "Installation Smoke Test",
                "ylabel": "Value",
                "data": {
                    "categories": ["A", "B", "C"],
                    "series": {"Series": [1.0, 1.5, 2.0]},
                },
                "annotate": True,
                "legend": False,
            }
        ],
    }
    request_path = tmp_path / "request.json"
    spec_path = tmp_path / "spec.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_plot_spec.py"),
            str(request_path),
            "--out",
            str(spec_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    normalized = json.loads(spec_path.read_text(encoding="utf-8"))
    assert normalized["panels"][0]["type"] == "bar"
    assert normalized["panels"][0]["series"] == [[1.0, 1.5, 2.0]]
    assert normalized["panels"][0]["labels"] == ["Series"]

    out_base = tmp_path / "smoke"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "plot_publication_figure.py"),
            str(spec_path),
            "--out-path",
            str(out_base),
            "--formats",
            "png",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    output = tmp_path / "smoke.png"
    assert output.is_file()
    assert output.stat().st_size > 0
