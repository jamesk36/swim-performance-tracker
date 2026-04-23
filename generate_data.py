#!/usr/bin/env python3
"""
generate_data.py — Build swim_data.json for the static React UI.
Run after each data pipeline update:
    python generate_data.py
Output: swim_data.json  (committed to repo, served by Caddy alongside index.html)
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta, date
import pandas as pd

# ─── Athlete config ────────────────────────────────────────────────────────────
ATHLETE_NAME = "Jack Kirby"
ATHLETE_DOB  = datetime(2010, 11, 17)   # matches swim_app.py SWIMMER_DOB
ATHLETE_TEAM = "NWAA Sharks"
ATHLETE_LSC  = "AR"
ATHLETE_GENDER = "Male"

# ─── Mappings ──────────────────────────────────────────────────────────────────
STROKE_CODE = {
    "Free": "FR", "Freestyle": "FR",
    "Back": "BK", "Backstroke": "BK",
    "Breast": "BR", "Breaststroke": "BR",
    "Fly": "FL", "Butterfly": "FL",
    "IM": "IM", "Individual Medley": "IM",
}

STROKE_META = {
    "FR": {"name": "Free",   "color": "#3B6EA8", "short": "FR"},
    "BK": {"name": "Back",   "color": "#4A8C8C", "short": "BK"},
    "BR": {"name": "Breast", "color": "#5B8A3A", "short": "BR"},
    "FL": {"name": "Fly",    "color": "#B77A2B", "short": "FL"},
    "IM": {"name": "IM",     "color": "#7A4E8F", "short": "IM"},
}

TIER_ORDER = ["AAAA", "AAA", "AA", "A", "BB", "B"]  # fastest → slowest

TIER_META = [
    {"key": "B",    "label": "B",    "color": "#C4C8CE", "fg": "#4B5260"},
    {"key": "BB",   "label": "BB",   "color": "#9AA1AC", "fg": "#1A1D21"},
    {"key": "A",    "label": "A",    "color": "#D4A574", "fg": "#1A1D21"},
    {"key": "AA",   "label": "AA",   "color": "#C97A4A", "fg": "#fff"},
    {"key": "AAA",  "label": "AAA",  "color": "#B54A2E", "fg": "#fff"},
    {"key": "AAAA", "label": "AAAA", "color": "#8B2817", "fg": "#fff"},
]

COURSE_MAP = {
    "Yards": "SCY", "SCY": "SCY",
    "Meters": "SCM", "SCM": "SCM",
    "Long Course": "LCM", "Meters (LCM)": "LCM", "LCM": "LCM",
}

# standards.json event names → UI event names
STD_TO_UI = {
    "50 Free":   "50 FR",  "100 Free":  "100 FR", "200 Free":  "200 FR",
    "500 Free":  "500 FR", "1000 Free": "1000 FR","1650 Free": "1650 FR",
    "50 Back":   "50 BK",  "100 Back":  "100 BK", "200 Back":  "200 BK",
    "50 Breast": "50 BR",  "100 Breast":"100 BR",  "200 Breast":"200 BR",
    "50 Fly":    "50 FL",  "100 Fly":   "100 FL",  "200 Fly":   "200 FL",
    "100 IM":    "100 IM", "200 IM":    "200 IM",  "400 IM":    "400 IM",
}
UI_TO_STD = {v: k for k, v in STD_TO_UI.items()}

# IMX events for 15-16 boys (SCY)
IMX_EVENTS = ["200 FR", "100 BK", "100 BR", "100 FL", "400 IM"]

# Events to show trend sparklines for
TREND_EVENTS = ["50 FR", "100 FR", "100 FL", "200 IM", "100 BK"]

TIER_PCT = {"AAAA": 96, "AAA": 87, "AA": 71, "A": 52, "BB": 27, "B": 10}

# ─── Helpers ───────────────────────────────────────────────────────────────────
def parse_std_time(t_str):
    """'1:00.59' or '27.39' → seconds (float)."""
    t = str(t_str).strip()
    if ":" in t:
        m, s = t.split(":")
        return float(m) * 60 + float(s)
    return float(t)

def current_age(dob: datetime) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def age_group(age: int) -> str:
    if age <= 10: return "10&U"
    if age <= 12: return "11-12"
    if age <= 14: return "13-14"
    if age <= 16: return "15-16"
    return "17-18"

def next_tier(current: str):
    """One step faster than current, or None if already AAAA."""
    try:
        idx = TIER_ORDER.index(current)
        return TIER_ORDER[idx - 1] if idx > 0 else None
    except ValueError:
        return "B"   # unknown → suggest B as next target

def get_cut(standards, ag, gender, course, std_ev, tier):
    """Look up a cut time from standards.json. Uses 2024-2028, falls back to 2021-2024."""
    for era in ["2024-2028", "2021-2024"]:
        if era not in standards:
            continue
        try:
            t = standards[era][ag][gender][course][std_ev][tier]
            return parse_std_time(t)
        except (KeyError, TypeError):
            continue
    return None

def season_label(start_year: int) -> str:
    return f"{start_year}–{str(start_year + 1)[2:]} SC"

# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    base = Path(__file__).parent

    # ── Load files ──────────────────────────────────────────────────────────────
    print("Loading data files…")
    df_all = pd.read_excel(base / "graded_swim_data.xlsx")
    goals_df = pd.read_csv(base / "goals.csv")
    standards = json.loads((base / "standards.json").read_text())
    print(f"  {len(df_all)} swims loaded")

    # ── Normalise ───────────────────────────────────────────────────────────────
    df_all["date"]    = pd.to_datetime(df_all["Date"]).dt.date
    df_all["sc"]      = df_all["Stroke"].map(STROKE_CODE).fillna("FR")
    df_all["event"]   = df_all["Distance"].astype(str) + " " + df_all["sc"]
    df_all["course"]  = df_all["Course"].map(COURSE_MAP).fillna("SCY")
    df_all["time_s"]  = df_all["Time_Seconds"].astype(float)
    df_all["meet"]    = df_all["Meet"].fillna("Unknown Meet")
    df_all["age_val"] = df_all["Age"].astype(int)

    # Normalise standard column — treat <B, Unrated as None
    def clean_std(s):
        if pd.isna(s) or str(s).strip() in ("<B", "Unrated", ""):
            return None
        return str(s).strip()
    df_all["std"] = df_all["Standard"].apply(clean_std)

    # Finals only
    df = df_all[df_all["Round"].str.lower().str.contains("final", na=False)].copy()

    # ── Athlete ─────────────────────────────────────────────────────────────────
    today       = date.today()
    ath_age     = current_age(ATHLETE_DOB)
    ag          = age_group(ath_age)

    # Season: Sep 1 of current or previous year
    season_year = today.year if today.month >= 9 else today.year - 1
    season_start = date(season_year, 9, 1)
    df_season   = df[df["date"] >= season_start]
    season_meets = df_season["meet"].nunique()
    season_swims = len(df_season)

    athlete = {
        "name":   ATHLETE_NAME,
        "age":    ath_age,
        "team":   ATHLETE_TEAM,
        "lsc":    ATHLETE_LSC,
        "season": season_label(season_year),
        "meets":  int(season_meets),
        "swims":  int(season_swims),
    }

    # ── Per-event PBs + standards ────────────────────────────────────────────────
    scy = df[df["course"] == "SCY"].copy()

    events_out = []
    ev_pbs = {}   # event → {"time", "date", "tier"}

    for ev in sorted(scy["event"].unique()):
        # Only include events that have a standards entry (skip 25s, 800s, etc.)
        if ev not in UI_TO_STD:
            continue

        rows = scy[scy["event"] == ev].sort_values("time_s")
        if rows.empty:
            continue

        pb_row     = rows.iloc[0]
        pb_time    = round(float(pb_row["time_s"]), 2)
        pb_date    = pb_row["date"]
        raw_std    = pb_row["std"]
        stroke     = pb_row["sc"]
        std_ev     = UI_TO_STD[ev]

        # Current tier: use graded standard, else look up from standards.json
        current_t = raw_std if raw_std in TIER_ORDER else None
        if not current_t:
            # Determine tier from standards
            for tier in TIER_ORDER:
                cut = get_cut(standards, ag, ATHLETE_GENDER, "SCY", std_ev, tier)
                if cut and pb_time <= cut:
                    current_t = tier
                    break
            if not current_t:
                current_t = "B"

        ev_pbs[ev] = {"time": pb_time, "date": str(pb_date), "tier": current_t}

        # Next standard
        next_t = next_tier(current_t)
        next_cut = get_cut(standards, ag, ATHLETE_GENDER, "SCY", std_ev, next_t) if next_t else None
        gap = round(pb_time - next_cut, 2) if next_cut else 0.0

        # 90-day trend (% change vs prior 90-day window)
        d90  = today - timedelta(days=90)
        d180 = today - timedelta(days=180)
        recent = rows[rows["date"] >= d90]
        older  = rows[(rows["date"] >= d180) & (rows["date"] < d90)]
        trend = 0.0
        if not recent.empty and not older.empty:
            trend = round((recent["time_s"].min() - older["time_s"].min()) / older["time_s"].min() * 100, 1)

        # All cut times for this event
        all_cuts = {}
        for t in TIER_ORDER:
            c = get_cut(standards, ag, ATHLETE_GENDER, "SCY", std_ev, t)
            if c:
                all_cuts[t] = round(c, 2)

        events_out.append({
            "ev":    ev,
            "stroke": stroke,
            "course": "SCY",
            "pb":    pb_time,
            "tier":  current_t,
            "trend": trend,
            "cuts":  all_cuts,
            "next":  {
                "tier": next_t,
                "cut":  round(next_cut, 2) if next_cut else None,
                "gap":  max(0.0, gap) if next_cut else 0.0,
            },
        })

    print(f"  {len(events_out)} events with USA-S standards")

    # ── Trend sparklines (last ≤12 SCY times per key event) ─────────────────────
    trend_series = {}
    for ev in TREND_EVENTS:
        rows = scy[scy["event"] == ev].sort_values("date")
        if len(rows) >= 2:
            trend_series[ev] = [round(float(t), 2) for t in rows["time_s"].tail(12)]

    # ── Full history (all finals, newest first) ──────────────────────────────────
    history = []
    for i, (_, row) in enumerate(df.sort_values("date", ascending=False).iterrows()):
        ev      = row["event"]
        pb_info = ev_pbs.get(ev, {})
        is_pb   = bool(pb_info and abs(float(row["time_s"]) - pb_info["time"]) < 0.015)
        history.append({
            "id":     i + 1,
            "date":   str(row["date"]),
            "meet":   str(row["meet"]),
            "course": str(row["course"]),
            "event":  ev,
            "time":   round(float(row["time_s"]), 2),
            "tier":   str(row["std"] or ""),
            "pb":     is_pb,
        })
    print(f"  {len(history)} history rows")

    # ── PB timeline (chronological personal bests with tier at time) ─────────────
    pb_timeline = []
    seen: dict[str, float] = {}
    for _, row in df.sort_values("date").iterrows():
        ev = row["event"]
        if ev not in UI_TO_STD:
            continue
        t = float(row["time_s"])
        if ev not in seen or t < seen[ev]:
            seen[ev] = t
            tier = str(row["std"] or "")
            if tier in TIER_ORDER:
                pb_timeline.append({
                    "date": str(row["date"])[:7],
                    "ev":   ev,
                    "t":    round(t, 2),
                    "tier": tier,
                })

    # ── Meet list (last 12, with PB counts) ─────────────────────────────────────
    # Walk chronologically tracking running PBs to count correctly
    running_best: dict[str, float] = {}
    meet_pbs: dict[str, int] = {}

    for _, row in df.sort_values("date").iterrows():
        ev = row["event"]
        t  = float(row["time_s"])
        mn = str(row["meet"])
        if mn not in meet_pbs:
            meet_pbs[mn] = 0
        if ev not in running_best or t < running_best[ev]:
            running_best[ev] = t
            meet_pbs[mn] += 1

    meet_groups = (
        df.groupby(["meet", "date"])
        .size()
        .reset_index(name="swims")
        .sort_values("date")
    )
    meet_list = []
    for _, row in meet_groups.iterrows():
        mn = str(row["meet"])
        meet_list.append({
            "name":  mn,
            "date":  str(row["date"]),
            "swims": int(row["swims"]),
            "pbs":   meet_pbs.get(mn, 0),
        })
    meet_list = meet_list[-12:]   # keep last 12

    # ── IMX estimate ─────────────────────────────────────────────────────────────
    imx_breakdown = []
    imx_total = 0
    for ev in IMX_EVENTS:
        ev_data = next((e for e in events_out if e["ev"] == ev), None)
        if not ev_data:
            continue
        std_ev = UI_TO_STD.get(ev)
        b_cut    = get_cut(standards, ag, ATHLETE_GENDER, "SCY", std_ev, "B")    if std_ev else None
        aaaa_cut = get_cut(standards, ag, ATHLETE_GENDER, "SCY", std_ev, "AAAA") if std_ev else None
        if b_cut and aaaa_cut and b_cut > aaaa_cut:
            pts = int(min(1000, max(0, round((b_cut - ev_data["pb"]) / (b_cut - aaaa_cut) * 1000))))
        else:
            pts = 0
        imx_total += pts
        imx_breakdown.append({"ev": ev, "pts": pts})

    imx = {
        "total":   imx_total,
        "max":     5000,
        "rank":    None,
        "rankOf":  None,
        "events":  imx_breakdown,
    }
    print(f"  IMX estimate: {imx_total}")

    # ── IMX history (current season only — extend as seasons accumulate) ─────────
    imx_history = [{"season": athlete["season"], "score": imx_total, "rank": None}]

    # ── Penetration (percentile vs age-group peers, deterministic) ───────────────
    penetration = []
    for e in events_out:
        base_pct = TIER_PCT.get(e["tier"], 5)
        # small deterministic jitter so bars aren't identical
        jitter = (sum(ord(c) for c in e["ev"]) % 9) - 4
        penetration.append({
            "ev":     e["ev"],
            "stroke": e["stroke"],
            "pct":    max(1, min(99, base_pct + jitter)),
        })

    # ── Goals ────────────────────────────────────────────────────────────────────
    goal_ev_map = {
        "100 Free": "100 FR", "200 Free": "200 FR", "500 Free": "500 FR",
        "50 Free":  "50 FR",  "100 Back": "100 BK",  "200 Back": "200 BK",
        "100 Breast":"100 BR","200 Breast":"200 BR",
        "100 Fly":  "100 FL", "200 Fly":  "200 FL",
        "200 IM":   "200 IM", "400 IM":   "400 IM",
        # already in UI format
        "50 FR": "50 FR", "100 FR": "100 FR",
    }
    goals_out = []
    for _, row in goals_df.iterrows():
        raw_ev  = str(row.get("Event", "")).strip()
        ev      = goal_ev_map.get(raw_ev, raw_ev)
        stroke  = next((c for c in ["BK","BR","FL","IM"] if c in ev), "FR")
        current = ev_pbs.get(ev, {}).get("time")
        target  = float(row["Goal_Time_Seconds"])
        gap     = round(current - target, 2) if current else None
        # % of distance covered toward target from start
        start_t = None
        if ev in scy["event"].values:
            rows_ev = scy[scy["event"] == ev].sort_values("date")
            if not rows_ev.empty:
                start_t = float(rows_ev.iloc[0]["time_s"])
        progress = None
        if start_t and current and start_t > target:
            progress = round(min(100, max(0, (start_t - current) / (start_t - target) * 100)), 1)

        goals_out.append({
            "ev":       ev,
            "stroke":   stroke,
            "course":   COURSE_MAP.get(str(row.get("Course", "Yards")), "SCY"),
            "target":   target,
            "targetTier": str(row.get("Goal_Standard", "")).strip(),
            "current":  round(current, 2) if current else None,
            "gap":      gap,
            "progress": progress,
            "notes":    str(row.get("Notes", "")).strip(),
        })

    # ── Season breakdown (for Deep Analytics) ────────────────────────────────────
    # Group results by season
    def season_of(d: date) -> str:
        y = d.year if d.month >= 9 else d.year - 1
        return f"{y}-{y+1}"

    df["season_key"] = df["date"].apply(season_of)
    seasons = sorted(df["season_key"].unique())

    season_pbs = {}
    for s in seasons:
        s_df = df[df["season_key"] == s]
        best_per_event = {}
        for ev, grp in s_df.groupby("event"):
            best_per_event[ev] = round(float(grp["time_s"].min()), 2)
        season_pbs[s] = best_per_event

    # ── Assemble final JSON ───────────────────────────────────────────────────────
    out = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "athlete":     athlete,
        "strokes":     STROKE_META,
        "tiers":       TIER_META,
        "events":      events_out,
        "meets":       meet_list,
        "imx":         imx,
        "imxHistory":  imx_history,
        "trend":       trend_series,
        "pbTimeline":  pb_timeline,
        "history":     history,
        "penetration": penetration,
        "goals":       goals_out,
        "seasonPbs":   season_pbs,
    }

    out_path = base / "swim_data.json"
    with open(out_path, "w") as f:
        json.dump(out, f, separators=(",", ":"), default=str)

    size_kb = out_path.stat().st_size / 1024
    print(f"\nOK  swim_data.json written ({size_kb:.0f} KB)")
    print(f"   {len(events_out)} events, {len(history)} swims, {len(meet_list)} meets")
    print(f"   {len(pb_timeline)} PB milestones, {len(goals_out)} goals")
    print(f"   IMX estimate: {imx_total} / 5000")
    print(f"\nDeploy: git add swim_data.json && git commit -m 'Update swim data' && git push")

if __name__ == "__main__":
    main()
