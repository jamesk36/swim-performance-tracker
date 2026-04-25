#!/usr/bin/env python3
"""
swimapi.py — Lightweight Flask API for swim photo import.
Runs on port 5001 alongside the static site.
"""
import base64
import json
import os
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv(Path(__file__).parent / ".env")

app  = Flask(__name__)
BASE = Path(__file__).parent
LIVE = BASE / "live_swims.json"

# ── Standards lookup ──────────────────────────────────────────────────────────
ATHLETE_DOB    = datetime(2010, 11, 17)
ATHLETE_GENDER = "Male"
TIER_ORDER     = ["AAAA", "AAA", "AA", "A", "BB", "B"]
UI_TO_STD = {
    "50 FR":"50 Free","100 FR":"100 Free","200 FR":"200 Free",
    "500 FR":"500 Free","1000 FR":"1000 Free","1650 FR":"1650 Free",
    "800 FR":"800 Free","1500 FR":"1500 Free",
    "50 BK":"50 Back","100 BK":"100 Back","200 BK":"200 Back",
    "50 BR":"50 Breast","100 BR":"100 Breast","200 BR":"200 Breast",
    "50 FL":"50 Fly","100 FL":"100 Fly","200 FL":"200 Fly",
    "100 IM":"100 IM","200 IM":"200 IM","400 IM":"400 IM",
}

def _load_standards():
    p = BASE / "standards.json"
    return json.loads(p.read_text()) if p.exists() else {}

STANDARDS = _load_standards()

def _age_at(swim_date):
    d = swim_date if isinstance(swim_date, date) else date.fromisoformat(swim_date)
    dob = ATHLETE_DOB.date()
    return d.year - dob.year - ((d.month, d.day) < (dob.month, dob.day))

def _age_group(age):
    if age <= 10: return "10&U"
    if age <= 12: return "11-12"
    if age <= 14: return "13-14"
    if age <= 16: return "15-16"
    return "17-18"

def _era(swim_date):
    d = swim_date if isinstance(swim_date, date) else date.fromisoformat(swim_date)
    return "2024-2028" if d >= date(2024, 9, 1) else "2021-2024"

def _parse_std_time(t):
    t = str(t).strip()
    if ":" in t:
        m, s = t.split(":")
        return float(m) * 60 + float(s)
    return float(t)

def lookup_tier(swim_date, course, event_ui, time_s):
    std_ev = UI_TO_STD.get(event_ui)
    if not std_ev:
        return ""
    age = _age_at(swim_date)
    ag  = _age_group(age)
    era = _era(swim_date)
    for tier in TIER_ORDER:
        try:
            cut = _parse_std_time(STANDARDS[era][ag][ATHLETE_GENDER][course][std_ev][tier])
            if time_s <= cut:
                return tier
        except (KeyError, TypeError):
            continue
    return ""

COURSE_MAP = {
    "lcm": "LCM", "long course": "LCM", "long course meters": "LCM",
    "scy": "SCY", "short course yards": "SCY", "yards": "SCY",
    "scm": "SCM", "short course meters": "SCM", "meters": "SCM",
}
STROKE_CODE = {
    "free": "FR", "freestyle": "FR",
    "back": "BK", "backstroke": "BK",
    "breast": "BR", "breaststroke": "BR",
    "fly": "FL", "butterfly": "FL",
    "im": "IM", "individual medley": "IM",
}

def load_live():
    return json.loads(LIVE.read_text()) if LIVE.exists() else []

def save_live(swims):
    LIVE.write_text(json.dumps(swims, indent=2))

def parse_time(t):
    t = str(t).strip()
    if ":" in t:
        m, s = t.split(":", 1)
        return round(float(m) * 60 + float(s), 2)
    return round(float(t), 2)

def normalise_event(raw):
    """'100 Back' / 'Boys 100 Meter Back' / '100 Backstroke' → '100 BK'"""
    import re
    # Strip gender prefix (Boys/Girls/Men/Women) and noise words
    s = re.sub(r'(?i)^(boys?|girls?|men|women)\s+', '', str(raw).strip())
    # Strip units like "Meter", "Yard", "LCM", "SCY" etc.
    s = re.sub(r'(?i)\b(meter|meters|yard|yards?|lcm|scy|scm)\b', '', s).strip()
    parts = s.split()
    if not parts:
        return raw
    # Find the numeric distance
    dist = next((p for p in parts if p.isdigit()), parts[0])
    stroke_parts = [p for p in parts if not p.isdigit()]
    stroke_raw = " ".join(stroke_parts).lower().strip()
    code = STROKE_CODE.get(stroke_raw, stroke_raw.upper()[:2] if stroke_raw else 'FR')
    return f"{dist} {code}"

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/api/live-swims", methods=["GET"])
def get_live():
    return jsonify(load_live())

@app.route("/api/live-swims/<int:swim_id>", methods=["DELETE"])
def del_live(swim_id):
    swims = [s for s in load_live() if s.get("id") != swim_id]
    save_live(swims)
    return jsonify({"ok": True})

@app.route("/api/photo-swim", methods=["POST"])
def photo_swim():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({"error": "ANTHROPIC_API_KEY not set on server"}), 500

    if "photo" not in request.files:
        return jsonify({"error": "No photo file in request"}), 400

    f = request.files["photo"]
    img_b64 = base64.standard_b64encode(f.read()).decode()
    media_type = f.content_type or "image/jpeg"

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": img_b64},
                },
                {
                    "type": "text",
                    "text": (
                        "This is a Meet Mobile screenshot of a swim result.\n"
                        "Extract the data and return ONLY this JSON (no markdown, no explanation):\n"
                        "{\n"
                        '  "meet": "full meet name e.g. 2026 AquaHawgs Long Course Opener",\n'
                        '  "event": "distance + stroke only, e.g. 100 Back, 200 Butterfly, 50 Free, 200 IM",\n'
                        '  "course": "LCM or SCY or SCM",\n'
                        '  "date": "YYYY-MM-DD",\n'
                        '  "time": "finals time e.g. 1:10.84",\n'
                        '  "place": 17,\n'
                        '  "splits": [35.24, 35.60]\n'
                        "}\n"
                        "For event: strip gender (Boys/Girls) and units (Meter/Yard). "
                        "Just distance number and stroke name. "
                        "splits = individual leg times only (not cumulative). "
                        "Empty array if not shown."
                    ),
                },
            ],
        }],
    )

    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()

    ex = json.loads(raw)

    swims = load_live()
    new_id = max((s["id"] for s in swims), default=0) + 1

    swim_date  = ex.get("date", str(date.today()))
    course     = COURSE_MAP.get(str(ex.get("course", "LCM")).lower(), "LCM")
    event_norm = normalise_event(ex.get("event", ""))
    time_s     = parse_time(ex.get("time", 0))
    tier       = lookup_tier(swim_date, course, event_norm, time_s)

    swim = {
        "id":     new_id,
        "date":   swim_date,
        "meet":   ex.get("meet", ""),
        "course": course,
        "event":  event_norm,
        "time":   time_s,
        "place":  ex.get("place"),
        "splits": ex.get("splits", []),
        "tier":   tier,
        "pb":     False,
        "live":   True,
    }
    swims.append(swim)
    save_live(swims)
    return jsonify(swim)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
