# scripts/start.py
import subprocess
import sys

def main():
    result = subprocess.run(["OctoBot"])
    sys.exit(result.returncode)