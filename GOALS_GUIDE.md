# Goal Tracker User Guide

## 🎯 Overview

Your dashboard now includes two powerful motivational features:

1. **GOALS & PROGRESS** - Track your personal season goals
2. **NEXT STANDARD TARGETS** - See exactly what you need for the next USA Swimming standard

---

## 📋 GOALS & PROGRESS Section

### What It Shows:
- Your target times for key events
- Current best time vs. goal time
- How many seconds you need to drop
- Progress percentage

### How to Set Your Goals:

**Step 1: Open goals.csv**
- Located in your Desktop/PY folder
- Open in Excel or any text editor

**Step 2: Edit the file**
The file has these columns:
- **Event**: e.g., "100 Free", "200 IM", "500 Free"
- **Course**: "Yards" or "LCM"
- **Goal_Time_Seconds**: Your target time in seconds
- **Goal_Standard**: (Optional) The standard you're aiming for (AAA, AA, etc.)
- **Notes**: (Optional) Any notes like "Sectionals Cut" or "Winter Champs Goal"

**Example rows:**
```csv
Event,Course,Goal_Time_Seconds,Goal_Standard,Notes
100 Free,Yards,50.00,AAA,Winter Championship Goal
500 Free,Yards,295.00,AAA,Season Goal
200 IM,Yards,125.00,AAA,Sectionals Cut
1650 Free,Yards,1020.00,AAAA,Mile Goal
```

**Step 3: Save and regenerate dashboard**
```bash
cd Desktop/PY
python create_dashboard.py
```

**Step 4: Open Swim_Dashboard.xlsx**
Your goals are now displayed with progress!

### Understanding the Display:

**"To Drop" Column:**
- **Positive number (red)** = You need to drop this many seconds to reach your goal
  - Example: "2.41" means you need to go 2.41 seconds faster
- **Negative number (green)** = You've already beaten your goal!
  - Example: "-0.50" means you're 0.50 seconds faster than your goal

**% Complete:**
- Shows your progress toward the goal
- 0% = Starting point
- 100% = Goal achieved!

---

## 🎖️ NEXT STANDARD TARGETS Section

### What It Shows Automatically:

For your **top 8 events**, the dashboard shows:
- **Current Best** - Your fastest time
- **Current Std** - Your current USA Swimming standard (AA, A, etc.)
- **Next Std** - The next level up (AAA, AAAA)
- **Target Time** - The time needed for that next standard
- **To Drop** - Seconds you need to drop to reach it

### Color Coding:

**Next Standard Level (Column E):**
- 🥇 **Gold background** = AAAA (highest level)
- 🥈 **Silver background** = AAA
- 🥉 **Bronze background** = AA

**To Drop (Column G):**
- 🟢 **Green background** = Within 1 second! So close!
- 🟡 **Yellow background** = Within 3 seconds - very achievable
- ⚪ **White background** = More than 3 seconds - keep working!

### Example:

```
Event       Course  Current  Curr Std  Next Std  Target   To Drop
100 Free    Yards   51.07    AAA       AAAA      45.09    4.58
```

**Translation:** 
"You're currently AAA in 100 Free with a 51.07. To get AAAA, you need a 45.09, which means dropping 4.58 seconds."

---

## 💡 How to Use This for Training

### Setting Smart Goals:

1. **Look at "Next Standard Targets"** to see what's achievable
2. **Pick events where "To Drop" is small** (under 3 seconds)
3. **Set those as your goals** in goals.csv
4. **Track progress** after each meet

### Example Goal-Setting Strategy:

Looking at Next Standard Targets, you see:
- 50 Free: Need to drop 1.93s for AAA ✅ **Achievable this season!**
- 100 Free: Need to drop 4.58s for AAAA ❌ **Long-term goal**
- 200 IM: Need to drop 2.41s for AAA ✅ **Good season goal**

So you might set your goals.csv like:
```csv
Event,Course,Goal_Time_Seconds,Goal_Standard,Notes
50 Free,Yards,22.59,AAA,Winter Champs - Drop 1.93s
200 IM,Yards,125.00,AAA,Conference Meet - Drop 2.41s
100 Free,Yards,47.00,AAA,End of season stretch goal
```

### Motivation Tips:

**Weekly Check-In:**
- After each meet, regenerate the dashboard
- Check your "To Drop" numbers
- Celebrate when they get smaller!

**Visual Motivation:**
- Print the "Next Standard Targets" table
- Hang it in your room or locker
- Update it after each meet to see progress

**Set Micro-Goals:**
- If you need to drop 5 seconds, break it into smaller chunks
- Goal 1: Drop 2 seconds by December
- Goal 2: Drop another 2 seconds by February
- Goal 3: Drop final 1 second by Championships

---

## 🔄 Updating Goals Throughout Season

### After Each Meet:

1. **Run the pipeline** to update data
```bash
python scraper.py
python cleaner.py
python merge_swims.py  # if you added high school swims
python grader.py
python create_dashboard.py
```

2. **Open dashboard** - "To Drop" numbers update automatically!

3. **Adjust goals if needed**:
   - Beat a goal? Set a new one!
   - Struggling? Adjust target to be more realistic
   - New event looking good? Add it to goals.csv

---

## 📊 Understanding Time Conversions

**Converting Time to Seconds:**

| Time | Seconds | How to Calculate |
|------|---------|------------------|
| 23.45 | 23.45 | Direct (under 1 minute) |
| 51.07 | 51.07 | Direct (under 1 minute) |
| 1:02.34 | 62.34 | (1×60) + 2.34 = 62.34 |
| 1:52.68 | 112.68 | (1×60) + 52.68 = 112.68 |
| 5:04.05 | 304.05 | (5×60) + 4.05 = 304.05 |
| 17:29.21 | 1049.21 | (17×60) + 29.21 = 1049.21 |

**Quick formula:** 
- Minutes × 60 + Seconds = Total Seconds

---

## 🎯 Example Goals for Different Levels

### **Beginner/Developmental Goals:**
Focus on achieving B or BB standards first
```csv
Event,Course,Goal_Time_Seconds,Goal_Standard,Notes
100 Free,Yards,65.00,B,First meet goal
50 Free,Yards,32.00,BB,End of season
```

### **Competitive Age Group Goals:**
Working toward A and AA
```csv
Event,Course,Goal_Time_Seconds,Goal_Standard,Notes
100 Free,Yards,55.00,AA,Sectionals Qualifying
200 Free,Yards,120.00,A,Championship cut
200 IM,Yards,125.00,AAA,Stretch goal
```

### **Elite/High School Goals:**
Targeting AAA and AAAA
```csv
Event,Course,Goal_Time_Seconds,Goal_Standard,Notes
100 Free,Yards,45.00,AAAA,State Championship
500 Free,Yards,280.00,AAAA,NCAA recruiting target
200 IM,Yards,115.00,AAAA,Ultimate season goal
```

---

## ❓ FAQ

**Q: Can I have goals for both Yards and LCM?**
A: Yes! Just add separate rows:
```csv
100 Free,Yards,50.00,AAA,Winter Goal
100 Free,LCM,56.00,AA,Summer Goal
```

**Q: What if I don't have a current time in an event?**
A: The dashboard will show "No time yet" but still display your goal. Once you swim that event, it'll start tracking progress.

**Q: Can I set goals that aren't USA Swimming standards?**
A: Absolutely! Set any target time you want. For example:
```csv
200 Free,Yards,118.50,,Beat my brother's time
50 Free,Yards,24.00,,School record
```

**Q: How many goals can I set?**
A: As many as you want! The dashboard will show all of them.

**Q: What if I beat all my goals?**
A: Congratulations! 🎉 Set new, more ambitious goals and keep pushing!

---

## 🚀 Pro Tips

1. **Set 3-5 goals max** - Too many goals dilutes focus
2. **Mix short and long term** - Some achievable this month, some for end of season
3. **Review monthly** - Adjust goals based on progress
4. **Celebrate wins** - When you hit a goal, acknowledge it before moving on
5. **Be realistic** - Dropping 10 seconds in 100 Free isn't happening in one season
6. **Focus on your weakest events** - Biggest room for improvement
7. **Use "Next Standard Targets"** - Let it guide your goal-setting

---

**Remember:** Goals are meant to motivate, not discourage. If you're consistently missing goals, adjust them. The point is to track progress and stay motivated! 🏊‍♂️
