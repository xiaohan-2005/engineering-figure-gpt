import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_check_command_is_offline():
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/efg.py"), "check"], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "gpt-image-2" in proc.stdout


def test_image_dry_run_uses_gpt_image_2():
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/generate_image.py"), "test figure", "--dry-run"], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert '"model": "gpt-image-2"' in proc.stdout


def test_custom_image_base_url_is_rejected():
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/generate_image.py"), "test", "--dry-run", "--base-url", "https://example.invalid/v1"], capture_output=True, text=True)
    assert proc.returncode != 0
