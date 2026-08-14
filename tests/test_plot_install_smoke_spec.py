from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_renderer_accepts_install_smoke_spec(tmp_path):
    spec = {
        "layout": {"rows": 1, "cols": 1, "figsize": [6, 4]},
        "panels": [
            {
                "kind": "bar",
                "title": "Installation Smoke Test",
                "ylabel": "Value",
                "data": {
                    "categories": ["A", "B", "C"],
                    "series": [{"label": "Series", "values": [1.0, 1.5, 2.0]}],
                },
                "annotate": True,
                "legend": False,
            }
        ],
    }
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
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
