# Swim Data Processing Guide
### From GoMotion Download to Live Website
**Updated 2026-07-12** — stale `/var/www/swim` clone deleted from server; site is served by **Caddy** (not nginx), config at `/etc/caddy/Caddyfile`.

---

## TL;DR (the whole update in 4 steps)

```powershell
# Location: C:\Users\james\Projects\swim-tracker
# Environment: PowerShell
python update_data.py
git add swim_data.json graded_swim_data.xlsx
git commit -m "Update swim data"
git push
ssh root@5.78.198.96 "cd /var/www/swimtracker && git checkout -- swim_data.json && git pull && venv/bin/python3 generate_data.py"
```

Site: https://swim.james-kirby.uk

---

## PART 1: Download New Results from GoMotion

1. Go to GoMotion, navigate to Jack's results page
2. Right-click on page → "Save As..." → **"Webpage, Complete"**
   - ⚠️ NOT "Text" or Ctrl+A copy/paste — the scraper needs real HTML `<table>` tags
3. Save as exactly `swim_history.html` in `C:\Users\james\Projects\swim-tracker`
   - (The old Desktop\PY location is retired — everything lives in the repo now)

**Sanity check:** the file should be roughly 200 KB. If it's ~35 KB, you got the
text-only version — re-save as "Webpage, Complete".

---

## PART 2: Add High School Swims (Optional)

New HS meet? Add a row per swim to `high_school_swims.csv` **before** running the pipeline:

| Column | Format | Example |
|---|---|---|
| Date | YYYY-MM-DD | 2025-12-12 |
| Age | Age at meet | 15 |
| Distance | Number only | 200 |
| Stroke | Free/Back/Breast/Fly/IM | Free |
| Round | Finals or Prelims | Finals |
| Course | Yards or LCM | Yards |
| Finals | Time with Y or L | 2:01.24Y |
| Time_Seconds | Numeric seconds | 121.24 |
| Meet | Meet name | Bentonville Schools Classic |

The merge step now runs automatically inside `update_data.py` — no separate command needed.

---

## PART 3: Run the Pipeline

```powershell
# Location: C:\Users\james\Projects\swim-tracker
# Environment: PowerShell
python update_data.py
```

This runs six steps in order:

```
swim_history.html → scraper.py → raw_swim_data.csv
                  → cleaner.py → clean_swim_data.xlsx
                  → merge_swims.py → (adds high_school_swims.csv)
                  → grader.py → graded_swim_data.xlsx
                  → create_dashboard.py → Swim_Dashboard.xlsx
                  → generate_data.py → swim_data.json
```

Individual scripts can still be run one at a time for debugging.

---

## PART 4: Deploy to the Website

```powershell
# Location: C:\Users\james\Projects\swim-tracker
# Environment: PowerShell
git add swim_data.json graded_swim_data.xlsx
git commit -m "Update swim data"
git push
ssh root@5.78.198.96 "cd /var/www/swimtracker && git checkout -- swim_data.json && git pull && venv/bin/python3 generate_data.py"
```

**Why each piece matters:**

- `graded_swim_data.xlsx` must be committed — the server rebuilds `swim_data.json` from it
- The server directory is **`/var/www/swimtracker`** — the only clone on the server
  (the stale `/var/www/swim` duplicate was verified unused and deleted 2026-07-12)
- `git checkout -- swim_data.json` first: a **3 AM nightly cron** on the server re-runs
  `generate_data.py`, which locally modifies `swim_data.json` and would otherwise block the pull
- Running `generate_data.py` after the pull makes the site update immediately instead
  of waiting for the 3 AM cron

**Server cron (for reference):**
```
0 3 * * * cd /var/www/swimtracker && /var/www/swimtracker/venv/bin/python3 generate_data.py >> /var/log/swimtracker-generate.log 2>&1
```

**Server stack (for reference):**
- Hetzner VPS, Ubuntu 24.04, `root@5.78.198.96`
- Web server: **Caddy** (nginx is NOT installed) — config: `/etc/caddy/Caddyfile`
- Caddy serves `swim.james-kirby.uk` from `root * /var/www/swimtracker`, with no-cache
  rules on `/index.html`, `/swim_data.json`, `/live_swims.json`

---

## Sectional Standards

The **Sectionals** tab compares Jack's PBs against Sectional qualifying
cuts, read from `sectional_standards.json`. Arkansas Swimming (LSC: AR) is
in the **Central Zone**; Jack's Sectional meet is the **Speedo Sectionals
at Columbia, MO — Central Section Region VIII** (Arkansas, Missouri Valley,
Oklahoma, Midwestern, Ozark LSCs), sanctioned by Missouri Valley Swimming.
There is no "Zone" comparison — Central Zone's age-group championship is
14-and-under only, so it doesn't apply to Jack at 15+.

`sectional_standards.json` is currently seeded from the **2026 CSRVIII
Spring meet book** (SCY meet, held March 12-15, 2026 — already past by the
time you read this, so treat it as a benchmark, not an upcoming entry). Its
`meta.note` field documents two caveats worth knowing:
- The LCM cuts come from that same meet book's "long-course equivalent"
  entry-proof column, not a dedicated Summer (LCM) Sectional standard.
  If Arkansas Swimming/CSRVIII publishes a separate Summer meet book, load
  that instead for a more precise LCM comparison (see steps below).
- 50 Back/Breast/Fly cuts are intentionally omitted — the source PDF had
  those rows duplicated from the 100-distance event (a document error, not
  a rule), so they were left blank rather than publish wrong numbers.

**To update with a newer/corrected standards document:**
1. Get the current Region VIII (CSRVIII) Sectional meet book/time-standards
   PDF — same idea as `swim_history.html`.
2. Edit `sectional_standards.json`: update per-event `Priority`/`Bonus`
   cuts under `Sectional.Open.Male.{SCY,LCM}`, matching the existing
   event-name structure (`standards.json`-style event names, e.g. `"100
   Free"`).
3. Update `meta` (meetName, note, etc.) to describe the new source.
4. Re-run `python generate_data.py` (or the full pipeline) and redeploy.

If a document ever needs age-bracketed splits or a genuine Zone standard,
extend the same file with additional keys — `generate_data.py`'s lookup
tries `"Open"` first, then falls back to the athlete's current age-group
key.

---

## Important Files

- `swim_history.html` — GoMotion download (input)
- `high_school_swims.csv` — manually maintained HS swims (never overwritten by scripts)
- `graded_swim_data.xlsx` — all swims + USA Swimming standards (committed to git)
- `swim_data.json` — feeds the website (committed, but server regenerates nightly)
- `standards.json` — USA Swimming time standards (don't delete!)
- `Swim_Dashboard.xlsx` — Excel dashboard (local only, gitignored)

---

## Troubleshooting

**Scraper says "couldn't find any table tags"**
- The HTML download was text-only. Re-save from GoMotion as "Webpage, Complete".

**Website didn't update after deploy**
- Did the pull fail on local changes? Use the `git checkout -- swim_data.json` prefix.
- Check the site's data freshness: `swim.james-kirby.uk/swim_data.json` → `generatedAt` field.
- Cron log on server: `/var/log/swimtracker-generate.log`

**HS swims missing from site**
- Confirm `merge_swims.py` ran (it's step 3 of `update_data.py`) and you committed
  `graded_swim_data.xlsx`, not just `swim_data.json`.

**All swims show "Unrated"**
- `standards.json` missing or the limited version. Restore from git.

**Time format errors in high_school_swims.csv**
- Finals needs Y or L suffix ("1:02.34Y"); Time_Seconds is plain numeric (62.34).
