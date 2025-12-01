# tests/sanity_check.py
"""
Quick sanity test: run main with demo and real modes (real requires env var).
This is not an exhaustive test but helps validate runtime flow.
"""

import os
import subprocess
import sys

def run_demo():
    print("Running demo mode check...")
    p = subprocess.run([sys.executable, "main.py", "--mode", "demo"], capture_output=False)
    print("demo exit code:", p.returncode)

def run_real_missing_key():
    print("Running real mode check (expected to fail if WEATHER_API_KEY not set)...")
    rc = subprocess.run([sys.executable, "main.py", "--mode", "real"], capture_output=False)
    print("real exit code:", rc.returncode)

if __name__ == "__main__":
    run_demo()
    run_real_missing_key()
