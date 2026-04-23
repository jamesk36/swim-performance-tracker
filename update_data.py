#!/usr/bin/env python3
"""
update_data.py — Full pipeline: swim_history.html → swim_data.json

Usage:
    1. Save your GoMotion HTML export as 'swim_history.html' in this folder
    2. Run: python update_data.py
    3. Then commit and push:
           git add swim_data.json
           git commit -m "Update swim data"
           git push
    4. On the server: ssh root@5.78.198.96 "cd /var/www/swim && git pull"
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent

STEPS = [
    ("scraper.py",          "swim_history.html",    "raw_swim_data.csv"),
    ("cleaner.py",          "raw_swim_data.csv",    "clean_swim_data.xlsx"),
    ("grader.py",           "clean_swim_data.xlsx", "graded_swim_data.xlsx"),
    ("create_dashboard.py", "graded_swim_data.xlsx","Swim_Dashboard.xlsx"),
    ("generate_data.py",    "Swim_Dashboard.xlsx",  "swim_data.json"),
]

def check_input(filename):
    path = ROOT / filename
    if not path.exists():
        print(f"\n❌  Missing input: {filename}")
        if filename == "swim_history.html":
            print("   → Download your swim history from GoMotion and save it here as 'swim_history.html'")
        sys.exit(1)

def run_step(script, input_file, output_file):
    print(f"\n▶  {script}  ({input_file} → {output_file})")
    check_input(input_file)
    result = subprocess.run(
        [sys.executable, str(ROOT / script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    # Print script output
    for line in (result.stdout + result.stderr).splitlines():
        print(f"   {line}")
    if result.returncode != 0:
        print(f"\n❌  {script} failed (exit {result.returncode})")
        sys.exit(result.returncode)
    out = ROOT / output_file
    if not out.exists():
        print(f"\n❌  {script} ran but {output_file} was not created")
        sys.exit(1)
    print(f"   ✓  {output_file} written ({out.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    print("=" * 60)
    print("  Swim Data Pipeline")
    print("=" * 60)

    for script, inp, out in STEPS:
        run_step(script, inp, out)

    print("\n" + "=" * 60)
    print("  ✅  swim_data.json is ready!")
    print("=" * 60)
    print("""
Next steps to go live:

  git add swim_data.json
  git commit -m "Update swim data"
  git push
  ssh root@5.78.198.96 "cd /var/www/swim && git pull"

The site updates instantly after the git pull.
""")
