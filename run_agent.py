import os
import subprocess
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=== CT Industry Intel Agent ===")
print(f"Python: {sys.executable}")
print(f"Working dir: {os.getcwd()}")

cmd = [
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "web_app.py",
    "--server.port",
    "8501",
    "--server.address",
    "localhost",
]

print("Starting web app: http://localhost:8501")
raise SystemExit(subprocess.call(cmd))
