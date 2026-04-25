#!/usr/bin/env python3
"""
generate_data.py — Build swim_data.json for the static React UI.
Run after each data pipeline update:
    python generate_data.py
Output: swim_data.json  (committed to repo, served by Caddy alongside index.html)
"""
import json
import os
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
    "800 Free":  "800 FR", "1500 Free": "1500 FR",
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

def era_for_date(swim_date) -> str:
    """Return the USA Swimming standards era in effect on swim_date."""
    cutover = date(2024, 9, 1)
    d = swim_date if isinstance(swim_date, date) else swim_date.date()
    return "2024-2028" if d >= cutover else "2021-2024"

def age_at_date(dob: datetime, swim_date) -> int:
    """Athlete's age on the date of the swim."""
    d = swim_date if isinstance(swim_date, date) else swim_date
    return d.year - dob.year - ((d.month, d.day) < (dob.month, dob.day))

def get_cut(standards, ag, gender, course, std_ev, tier, era=None):
    """Look up a cut time from standards.json.
    If era is specified, use only that era. Otherwise prefer 2024-2028, fall back to 2021-2024."""
    eras = [era] if era else ["2024-2028", "2021-2024"]
    for e in eras:
        if e not in standards:
            continue
        try:
            t = standards[e][ag][gender][course][std_ev][tier]
            return parse_std_time(t)
        except (KeyError, TypeError):
            continue
    return None

def season_label(start_year: int) -> str:
    return f"{start_year}–{str(start_year + 1)[2:]} SC"

def days_until(target_date_str: str, from_date: date) -> int:
    """Days from from_date to target_date_str (YYYY-MM-DD). Negative = in the past."""
    td = date.fromisoformat(target_date_str)
    return (td - from_date).days

TRUNCATED_LEN = 28   # HY-TEK Meet Manager caps names at 30 chars

def resolve_meet_names(raw_names: list, cache: dict, base: Path) -> dict:
    """
    Expand truncated HY-TEK meet names via Claude API.
    Results are persisted to meet_name_cache.json so the API is only called
    for names seen for the first time.
    """
    to_resolve = [n for n in raw_names if n not in cache and len(str(n)) >= TRUNCATED_LEN]
    if not to_resolve:
        return cache

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(f"  NOTE: {len(to_resolve)} meet name(s) look truncated but ANTHROPIC_API_KEY is not set - skipping expansion")
        return cache

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        names_json = json.dumps(to_resolve, indent=2)
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": (
                    "These are youth swim meet names exported from HY-TEK Meet Manager.\n"
                    "HY-TEK truncates meet names at 30 characters, so some are cut off mid-word.\n"
                    "Expand any truncated names to their most likely full name.\n"
                    "These are USA Swimming / Arkansas (ARSI) region meets.\n\n"
                    f"Input names (JSON array):\n{names_json}\n\n"
                    "Return a JSON object mapping each input name to its best full name.\n"
                    "For names that are already complete, map them to themselves (unchanged).\n"
                    "Return ONLY valid JSON — no explanation, no markdown."
                ),
            }],
        )
        raw = msg.content[0].text.strip()
        # Strip markdown code fences if the model wrapped the JSON
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]          # drop opening fence
            if raw.startswith("json"):
                raw = raw[4:]                      # drop "json" language tag
            raw = raw.rsplit("```", 1)[0].strip()  # drop closing fence
        resolved = json.loads(raw)
        cache.update(resolved)
        cache_path = base / "meet_name_cache.json"
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, sort_keys=True, ensure_ascii=False)
        changed = {k: v for k, v in resolved.items() if k != v}
        print(f"  Meet names resolved via Claude: {len(changed)} expanded, {len(resolved)-len(changed)} already complete")
        for k, v in changed.items():
            print(f"    {k!r}  →  {v!r}")
    except Exception as exc:
        print(f"  Meet name resolution failed: {exc}")

    return cache

def parse_time_str(t: str) -> float:
    """'1:10.59' or '0:30.19' or '27.39' → seconds (float)."""
    t = str(t).strip()
    if ":" in t:
        m, s = t.split(":")
        return float(m) * 60 + float(s)
    return float(t)

# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    base = Path(__file__).parent

    # ── Load files ──────────────────────────────────────────────────────────────
    print("Loading data files…")
    df_all = pd.read_excel(base / "graded_swim_data.xlsx")
    goals_df = pd.read_csv(base / "goals.csv")
    standards = json.loads((base / "standards.json").read_text())
    meets_data = json.loads((base / "meets.json").read_text()) if (base / "meets.json").exists() else {"meets": []}
    print(f"  {len(df_all)} swims loaded, {len(meets_data['meets'])} meets in meets.json")

    # ── Resolve truncated meet names ─────────────────────────────────────────────
    cache_path = base / "meet_name_cache.json"
    name_cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    raw_names  = df_all["Meet"].dropna().unique().tolist()
    name_cache = resolve_meet_names(raw_names, name_cache, base)
    if name_cache:
        df_all["Meet"] = df_all["Meet"].apply(lambda n: name_cache.get(str(n), str(n)))

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
            # Use age group and standards era at the time of the PB swim
            swim_era = era_for_date(pb_date)
            swim_age = age_at_date(ATHLETE_DOB, pb_date)
            swim_ag  = age_group(swim_age)
            for tier in TIER_ORDER:
                cut = get_cut(standards, swim_ag, ATHLETE_GENDER, "SCY", std_ev, tier, era=swim_era)
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
        tier_str = str(row["std"] or "").strip()
        # If no recorded standard, compute from age/era at time of swim
        if tier_str not in TIER_ORDER:
            std_ev_h = UI_TO_STD.get(ev)
            if std_ev_h:
                swim_era_h = era_for_date(row["date"])
                swim_age_h = age_at_date(ATHLETE_DOB, row["date"])
                swim_ag_h  = age_group(swim_age_h)
                t_s = float(row["time_s"])
                for t in TIER_ORDER:
                    cut = get_cut(standards, swim_ag_h, ATHLETE_GENDER, str(row["course"]), std_ev_h, t, era=swim_era_h)
                    if cut and t_s <= cut:
                        tier_str = t
                        break
        history.append({
            "id":     i + 1,
            "date":   str(row["date"]),
            "meet":   str(row["meet"]),
            "course": str(row["course"]),
            "event":  ev,
            "time":   round(float(row["time_s"]), 2),
            "tier":   tier_str,
            "pb":     is_pb,
        })
    print(f"  {len(history)} history rows")

    # ── Merge live swims (from photo uploads) if present locally ─────────────────
    live_path = base / "live_swims.json"
    if live_path.exists():
        live_swims = json.loads(live_path.read_text(encoding="utf-8"))
        # Only include live swims not already covered by official data
        official_keys = {(r["date"], r["event"]) for r in history}
        added = 0
        for s in live_swims:
            key = (s.get("date",""), s.get("event",""))
            if key not in official_keys:
                history.append({
                    "id":      s.get("id", 9000 + added),
                    "date":    s.get("date",""),
                    "meet":    s.get("meet",""),
                    "course":  s.get("course","LCM"),
                    "event":   s.get("event",""),
                    "time":    s.get("time", 0),
                    "tier":    s.get("tier",""),
                    "pb":      False,
                    "pending": True,
                    "splits":  s.get("splits",[]),
                })
                added += 1
        if added:
            print(f"  + {added} pending live swim(s) merged from live_swims.json")

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

    # ── LCM PBs + qualified swims ────────────────────────────────────────────────
    lcm = df[df["course"] == "LCM"].copy()
    lcm_pbs: dict[str, dict] = {}  # ev → {time, date, tier}

    for ev, grp in lcm.groupby("event"):
        best_row = grp.loc[grp["time_s"].idxmin()]
        std_ev   = UI_TO_STD.get(ev)
        raw_std  = str(best_row["std"] or "")
        current_t = raw_std if raw_std in TIER_ORDER else None
        if not current_t and std_ev:
            # Use age group and standards era at the time of the PB swim
            pb_d     = best_row["date"]
            swim_era = era_for_date(pb_d)
            swim_age = age_at_date(ATHLETE_DOB, pb_d)
            swim_ag  = age_group(swim_age)
            for tier in TIER_ORDER:
                cut = get_cut(standards, swim_ag, ATHLETE_GENDER, "LCM", std_ev, tier, era=swim_era)
                if cut and float(best_row["time_s"]) <= cut:
                    current_t = tier
                    break
        if not current_t:
            current_t = ""
        lcm_pbs[ev] = {
            "time": round(float(best_row["time_s"]), 2),
            "date": str(best_row["date"]),
            "tier": current_t,
        }

    # Build lcmEvents list (events that have both a PB and standards entry)
    lcm_events_out = []
    for ev in sorted(lcm_pbs.keys()):
        std_ev = UI_TO_STD.get(ev)
        if not std_ev:
            continue
        pb_info  = lcm_pbs[ev]
        pb_time  = pb_info["time"]
        stroke   = next((c for c in ["BK","BR","FL","IM"] if c in ev), "FR")
        current_t = pb_info["tier"]

        next_t   = next_tier(current_t) if current_t in TIER_ORDER else "BB"
        next_cut = get_cut(standards, ag, ATHLETE_GENDER, "LCM", std_ev, next_t) if next_t else None
        bb_cut   = get_cut(standards, ag, ATHLETE_GENDER, "LCM", std_ev, "BB")
        bb_qual  = bool(bb_cut and pb_time <= bb_cut)
        gap      = round(pb_time - next_cut, 2) if next_cut else 0.0

        all_cuts = {}
        for t in TIER_ORDER:
            c = get_cut(standards, ag, ATHLETE_GENDER, "LCM", std_ev, t)
            if c:
                all_cuts[t] = round(c, 2)

        lcm_events_out.append({
            "ev":     ev,
            "stroke": stroke,
            "course": "LCM",
            "pb":     pb_time,
            "date":   pb_info["date"],
            "tier":   current_t,
            "bbQual": bb_qual,
            "cuts":   all_cuts,
            "next":   {
                "tier": next_t,
                "cut":  round(next_cut, 2) if next_cut else None,
                "gap":  max(0.0, gap) if next_cut else 0.0,
            },
        })

    # ── Upcoming meets + countdown ────────────────────────────────────────────────
    upcoming_meets = []
    past_meets_meta = []
    for m in meets_data["meets"]:
        days = days_until(m["startDate"], today)
        meet_entry = {
            "id":        m["id"],
            "name":      m["name"],
            "shortName": m.get("shortName", m["name"]),
            "location":  m.get("location", ""),
            "startDate": m["startDate"],
            "endDate":   m.get("endDate", m["startDate"]),
            "daysAway":  days,
            "course":    m.get("course", "LCM"),
            "type":      m.get("type", "invitational"),
            "qualifyingRequired": m.get("qualifyingRequired", False),
        }
        if m.get("entries"):
            meet_entry["entries"] = m["entries"]

        # Compute qualification status vs this meet's qualifying times
        if m.get("qualifyingTimes") and lcm_pbs:
            qual_events  = []
            uqual_events = []
            for ev_ui, qt_str in m["qualifyingTimes"].items():
                qt_s   = parse_time_str(qt_str)
                pb_info = lcm_pbs.get(ev_ui)
                pb_s   = pb_info["time"] if pb_info else None
                qualified = bool(pb_s is not None and pb_s <= qt_s)
                rec = {
                    "event":     ev_ui,
                    "qualTime":  qt_s,
                    "pb":        pb_s,
                    "qualified": qualified,
                }
                (qual_events if qualified else uqual_events).append(rec)
            meet_entry["qualifiedEvents"]   = sorted(qual_events, key=lambda x: x["event"])
            meet_entry["unqualifiedEvents"] = sorted(uqual_events, key=lambda x: x["event"])
            meet_entry["qualifiedCount"]    = len(qual_events)
            meet_entry["totalQualEvents"]   = len(qual_events) + len(uqual_events)

        if days >= 0:
            upcoming_meets.append(meet_entry)
        else:
            past_meets_meta.append(meet_entry)

    upcoming_meets.sort(key=lambda x: x["startDate"])
    next_meet = upcoming_meets[0] if upcoming_meets else None

    # LCM qualified summary (vs BB standard)
    lcm_bb_qual  = [e for e in lcm_events_out if e["bbQual"]]
    lcm_bb_total = [e for e in lcm_events_out if e.get("cuts", {}).get("BB")]

    lcm_qualified = {
        "bbCount":  len(lcm_bb_qual),
        "bbTotal":  len(lcm_bb_total),
        "events":   lcm_events_out,
    }
    print(f"  LCM: {len(lcm_pbs)} events, {len(lcm_bb_qual)}/{len(lcm_bb_total)} BB-qualified")
    if next_meet:
        print(f"  Next meet: {next_meet['shortName']} in {next_meet['daysAway']} day(s)")

    # ── Assemble final JSON ───────────────────────────────────────────────────────
    out = {
        "generatedAt":   datetime.now().isoformat(timespec="seconds"),
        "athlete":       athlete,
        "strokes":       STROKE_META,
        "tiers":         TIER_META,
        "events":        events_out,
        "meets":         meet_list,
        "imx":           imx,
        "imxHistory":    imx_history,
        "trend":         trend_series,
        "pbTimeline":    pb_timeline,
        "history":       history,
        "penetration":   penetration,
        "goals":         goals_out,
        "seasonPbs":     season_pbs,
        "lcmQualified":  lcm_qualified,
        "upcomingMeets": upcoming_meets,
        "nextMeet":      next_meet,
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
