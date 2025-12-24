# Swim Data Processing Guide
### From GoMotion Download to Graded Results (+ High School Swims)

---

## 📥 PART 1: Download New Results from GoMotion

1. Go to GoMotion website
2. Navigate to swimmer's results page
3. **Save page as HTML:**
   - Right-click on page → "Save As..."
   - Save as: `swim_history.html`
   - Location: Desktop → PY folder
   - ⚠️ **Important:** Use the exact filename `swim_history.html`

---

## 🏫 PART 2: Add High School Swims (Optional)

If your son has swims from high school meets:

### First Time Setup:
1. Open `high_school_swims.csv` in Excel
2. Delete the example rows (keep the header row!)

### Adding New High School Swims:
1. Open `high_school_swims.csv` in Excel
2. Add a new row for each swim
3. Fill in the columns:
   - **Date**: Format as YYYY-MM-DD (e.g., 2024-12-05)
   - **Age**: Swimmer's age at time of meet
   - **Distance**: Just the number (e.g., 100, 200, 500)
   - **Stroke**: Free, Back, Breast, Fly, or IM
   - **Round**: Finals or Prelims
   - **Course**: Yards or LCM
   - **Finals**: Time with Y or L (e.g., 52.45Y or 1:02.34L)
   - **Time_Seconds**: Time in seconds (e.g., 52.45 or 62.34)
   - **Meet**: Meet name (e.g., "HS Dual Meet vs Rogers")

### Example Row:
```
2024-12-05,14,100,Free,Finals,Yards,52.45Y,52.45,HS Dual Meet vs Rogers
```

4. Save the file (keep as .csv format)

---

## 🔄 PART 3: Run the Data Pipeline

Open **Command Prompt** or **Terminal** and navigate to your PY folder:

```bash
cd Desktop/PY
```

### 3a. Extract Data from HTML → CSV

```bash
python scraper.py
```

✅ **Expected Output:**
- Creates: `raw_swim_data.csv`
- Message: "✅ Success! Found X tables in the file"

---

### 3b. Clean and Format the Data

```bash
python cleaner.py
```

✅ **Expected Output:**
- Creates: `clean_swim_data.xlsx`
- Message: "✅ Success! Expanded X raw rows into Y individual swims"

---

### 3c. Merge High School Swims (if you have any)

```bash
python merge_swims.py
```

✅ **Expected Output:**
- Updates: `clean_swim_data.xlsx` (adds high school swims)
- Message: "✅ SUCCESS! Combined data saved"
- Shows count of GoMotion swims + High School swims

⚠️ **Skip this step if you don't have high school swims to add**

---

### 3d. Grade the Performances

```bash
python grader.py
```

✅ **Expected Output:**
- Creates: `graded_swim_data.xlsx`
- Message: "✅ Success! Graded data saved to graded_swim_data.xlsx"

---

### 3e. Create Interactive Dashboard

```bash
python create_dashboard.py
```

✅ **Expected Output:**
- Creates: `Swim_Dashboard.xlsx`
- Message: "✅ Dashboard created: Swim_Dashboard.xlsx"

---

## 📊 PART 4: View Results

Open `Swim_Dashboard.xlsx` in Excel to see:
- Interactive lookup tool with dropdown lists
- Personal bests for every event
- Time progression charts
- Complete swim history (GoMotion + High School combined!)

---

## 🔍 Quick Reference

### FULL WORKFLOW (with High School swims):
```
1. Download swim_history.html from GoMotion
2. python scraper.py
3. python cleaner.py
4. [Add high school swims to high_school_swims.csv in Excel]
5. python merge_swims.py
6. python grader.py
7. python create_dashboard.py
8. Open Swim_Dashboard.xlsx
```

### QUICK WORKFLOW (GoMotion only, no high school):
```
1. Download swim_history.html from GoMotion
2. python scraper.py
3. python cleaner.py
4. python grader.py
5. python create_dashboard.py
6. Open Swim_Dashboard.xlsx
```

---

## 📁 Important Files

**Data Pipeline:**
- `swim_history.html` - Downloaded from GoMotion
- `high_school_swims.csv` - Manually maintained (add new HS swims here!)
- `clean_swim_data.xlsx` - Combined GoMotion + High School data
- `graded_swim_data.xlsx` - All swims with USA Swimming standards
- `Swim_Dashboard.xlsx` - Interactive Excel dashboard

**Scripts:**
- `scraper.py` - Extract from HTML
- `cleaner.py` - Clean and format
- `merge_swims.py` - Combine GoMotion + High School 🆕
- `grader.py` - Add standards
- `create_dashboard.py` - Build dashboard

**Reference:**
- `standards.json` - USA Swimming time standards (don't delete!)

---

## ❓ Troubleshooting

**Problem:** "File not found" when running merge_swims.py
- ✅ Make sure you ran `cleaner.py` first to create `clean_swim_data.xlsx`
- ✅ If you don't have high school swims yet, skip the merge step

**Problem:** High school swims not showing in dashboard
- ✅ Make sure you ran `merge_swims.py` BEFORE `grader.py`
- ✅ Check that dates in high_school_swims.csv are formatted correctly (YYYY-MM-DD)
- ✅ Make sure Time_Seconds column has numeric values (no "Y" or "L")

**Problem:** Times in high_school_swims.csv are wrong
- ✅ Finals column should have Y or L (e.g., "52.45Y")
- ✅ Time_Seconds should be just the number (e.g., 52.45)
- ✅ For times over 1 minute: Finals = "1:02.34Y", Time_Seconds = 62.34

---

## 💡 Pro Tips

### Managing High School Swims:
1. **Update after each HS meet** - Add new swims to `high_school_swims.csv` immediately
2. **Keep it simple** - The CSV is meant for manual entry of just a few swims
3. **Run full pipeline** - After adding HS swims, run merge → grade → dashboard

### When to Run Merge:
- ✅ Run merge_swims.py whenever you add new high school swims
- ✅ Run merge_swims.py after cleaner.py and before grader.py
- ⚠️ Don't need to run merge if you haven't added any new HS swims

### Backup Your High School Data:
- Keep a backup copy of `high_school_swims.csv` 
- This file is manually maintained and won't be overwritten by scripts

---

## 🎯 Example: Adding a High School Meet

Let's say your son swam at a dual meet on December 10, 2024:

1. Open `high_school_swims.csv` in Excel
2. Add rows:
```
2024-12-10,14,50,Free,Finals,Yards,23.45Y,23.45,HS Dual Meet vs Bentonville West
2024-12-10,14,100,Back,Finals,Yards,58.67Y,58.67,HS Dual Meet vs Bentonville West
```
3. Save the file
4. Run the pipeline:
```bash
python scraper.py       # Get latest GoMotion data
python cleaner.py       # Clean GoMotion data
python merge_swims.py   # Add high school swims
python grader.py        # Grade everything
python create_dashboard.py  # Update dashboard
```
5. Open `Swim_Dashboard.xlsx` - the HS swims are now included!

---

**Questions?** The high_school_swims.csv file is your friend for manually entering any swims that aren't on GoMotion!
