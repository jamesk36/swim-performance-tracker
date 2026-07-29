#!/usr/bin/env python3
"""
seed_sectional_placeholder.py — Generate PLACEHOLDER Sectional/Zone cut times.

Jack (age 15-16, LSC: AR / Central Zone) doesn't yet have an official Sectional
or Zone time-standards document loaded into this project — the real ones live
on GoMotion behind Sectional/Zone-specific PDFs (e.g. "Region VIII" Speedo
Sectionals, which covers Arkansas, Missouri Valley, Oklahoma, Midwestern, and
Ozark LSCs) that weren't available to fetch automatically.

This script fabricates *rough* stand-in numbers from the existing USA-S AAAA
motivational standard (standards.json, 15-16 Male) so the "Sectionals/Zones"
UI tab has something to render:
    Sectional placeholder = AAAA cut × 0.985  (≈ AAAA, slightly faster)
    Zone placeholder      = AAAA cut × 1.030  (≈ AAA/AA range)

These multipliers are NOT derived from any real meet's standards — they only
exist to make the layout look plausible. Replace sectional_standards.json
with real data as soon as you have the official PDF:
    1. Set meta.verified = true
    2. Fill in real per-event cuts for "Sectional" and/or "Zone"
    3. Re-run generate_data.py

Run:
    python3 seed_sectional_placeholder.py
"""
import json
from pathlib import Path

BASE = Path(__file__).parent
AGE_GROUP = "15-16"
GENDER = "Male"
SECTIONAL_FACTOR = 0.985
ZONE_FACTOR = 1.030

def parse_time(t):
    t = str(t).strip()
    if ":" in t:
        m, s = t.split(":")
        return float(m) * 60 + float(s)
    return float(t)

def format_time(seconds):
    seconds = round(seconds, 2)
    if seconds >= 60:
        m = int(seconds // 60)
        s = seconds - m * 60
        return f"{m}:{s:05.2f}"
    return f"{seconds:.2f}"

def build():
    standards = json.loads((BASE / "standards.json").read_text())
    era = standards.get("2024-2028", {})
    ag_data = era.get(AGE_GROUP, {}).get(GENDER, {})

    sectional = {}
    zone = {}
    for course in ("SCY", "LCM"):
        sectional[course] = {}
        zone[course] = {}
        for event, cuts in ag_data.get(course, {}).items():
            aaaa = cuts.get("AAAA")
            if not aaaa:
                continue
            aaaa_s = parse_time(aaaa)
            sectional[course][event] = format_time(aaaa_s * SECTIONAL_FACTOR)
            zone[course][event] = format_time(aaaa_s * ZONE_FACTOR)

    out = {
        "meta": {
            "verified": False,
            "note": (
                "PLACEHOLDER — NOT an official time standard. Generated from "
                f"{AGE_GROUP} {GENDER} AAAA cuts (x{SECTIONAL_FACTOR} / x{ZONE_FACTOR}) "
                "only so the UI has something to display. Replace with the real "
                "Region VIII / Central Zone Sectional and/or Zone qualifying "
                "times, then set verified=true. See PROCESS_GUIDE.md."
            ),
            "ageGroup": AGE_GROUP,
            "gender": GENDER,
            "season": "2025-2026",
        },
        "Sectional": {AGE_GROUP: {GENDER: sectional}},
        "Zone": {AGE_GROUP: {GENDER: zone}},
    }

    out_path = BASE / "sectional_standards.json"
    out_path.write_text(json.dumps(out, indent=2))
    n = sum(len(v) for v in sectional.values())
    print(f"Wrote {out_path.name}: {n} placeholder event/course cuts (UNVERIFIED)")

if __name__ == "__main__":
    build()
