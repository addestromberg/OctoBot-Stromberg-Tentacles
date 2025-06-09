# scripts/pack.py

import subprocess
import sys

def main():
    cmd = [
        "OctoBot", "tentacles",
        "--pack",
        "../pack/any_platform.zip",
        "--directory",
        "src/",
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)