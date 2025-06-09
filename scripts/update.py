# scripts/update.py

import subprocess
import sys

def main():
    cmd = [
        "OctoBot", "tentacles",
        "--single-tentacle-install",
        "src/extra_volatility_evaluator",
        "Evaluator/TA"
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)