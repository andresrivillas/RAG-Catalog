import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src" / "promotional_gifts" / "interfaces" / "web" / "streamlit_app.py"

env = os.environ.copy()
env["PYTHONPATH"] = f"{ROOT / 'src'}:{ROOT}:{env.get('PYTHONPATH', '')}"

if __name__ == "__main__":
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(APP),
            "--server.headless",
            "true",
        ],
        env=env,
    )
