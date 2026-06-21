import subprocess
import sys


def test_cli_run_smoke(tmp_path):
    output_dir = tmp_path / "cli_output"
    command = [
        sys.executable,
        "-m",
        "geosciloop.cli",
        "run",
        "configs/uhi_synthetic_demo.yaml",
        "--offline",
        "--output-dir",
        str(output_dir),
    ]

    completed = subprocess.run(command, check=False, capture_output=True, text=True)

    assert completed.returncode == 0, completed.stderr
    assert "GeoSciLoop run complete" in completed.stdout
    assert (output_dir / "research_ledger.json").exists()
    assert (output_dir / "report.md").exists()
