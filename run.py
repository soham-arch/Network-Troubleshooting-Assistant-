"""Entrypoint runner for the Network Troubleshooting Assistant.

Usage:
  python run.py        -> Starts Streamlit UI (default)
  python run.py api    -> Starts FastAPI REST server on port 8000
"""

import subprocess
import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() == "api":
        cmd = [sys.executable, "-m", "uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    else:
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
