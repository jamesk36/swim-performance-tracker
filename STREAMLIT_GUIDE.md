# Swim Tracker Streamlit App Guide

## 🚀 Quick Start

### Installation

1. **Make sure you have Python installed** (3.8 or higher)

2. **Install dependencies:**
```bash
cd Desktop/PY/swim_project
pip install -r requirements.txt
```

3. **Run the app:**
```bash
streamlit run swim_app.py
```

4. **Open your browser:**
   - The app automatically opens at `http://localhost:8501`
   - If not, manually navigate to that URL

---

## 📱 Using the App

### 📊 Dashboard Page

**What you'll see:**
- Key metrics (Total swims, AAA/AA/A counts, current age)
- Personal Best Lookup with dropdown selectors
- Time Progression charts
- Standards Distribution graph
- Recent swims table

**How to use:**
1. Select an event and course from the dropdowns
2. See your best time, standard, and date instantly
3. View time progression chart below
4. Explore other events by changing the selection

---

### 📁 Upload Data Page

**Upload GoMotion Results:**
1. Go to GoMotion website
2. Save results page as HTML (`swim_history.html`)
3. Upload the HTML file using the file uploader
4. Click "Process GoMotion Data"
5. Wait for all 3 steps to complete (extract → clean → grade)
6. Check Dashboard to see results!

**Add High School Swims:**
1. Fill out the form with swim details:
   - Date, Age, Distance, Stroke
   - Round (Finals/Prelims), Course (Yards/LCM)
   - Time (e.g., "52.45" or "1:02.34")
   - Meet name
2. Click "Add Swim"
3. Swim appears in table above
4. Click "Merge High School Swims" when ready
5. Run grader from terminal to include in dashboard

**Pro tip:** You can add multiple high school swims before merging!

---

### 🎯 Goals Page

**View Current Goals:**
- See all your season goals
- View current best vs. goal
- See how many seconds to drop
- Track progress with visual indicators

**Add New Goal:**
1. Enter event (e.g., "100 Free")
2. Select course (Yards or LCM)
3. Enter goal time (e.g., "50.00" or "1:45.00")
4. Optionally select target standard
5. Add notes (e.g., "Winter Championships")
6. Click "Add Goal"

**Goal Status Colors:**
- 🎉 Green "Goal Achieved!" = You beat your goal!
- 🔥 Yellow "So Close!" = Within 1 second
- 📊 Blue "Keep Working!" = More than 1 second away

---

### 📈 Analytics Page

**Event Comparison:**
- Radar chart showing strength by stroke
- See which strokes are your strongest
- Based on proportion of AAA/AA/A times

**Improvement Timeline:**
- Select any event
- See improvement graph over time
- Positive values = you got faster!
- Helps identify trends

---

### ⚙️ Settings Page

**Data Management:**
- Download all data (coming soon)
- Clear cache if app feels slow

**About:**
- Version information
- Feature list
- Credits

---

## 🎨 Features Comparison: Web App vs. Excel Dashboard

| Feature | Streamlit App | Excel Dashboard |
|---------|---------------|-----------------|
| **Accessibility** | Any device with browser | Desktop only |
| **File Upload** | Drag & drop in browser | Manual save to folder |
| **Add HS Swims** | Web form, instant | Edit CSV in Excel |
| **Charts** | Interactive (zoom, hover) | Static |
| **Updates** | One-click processing | Run multiple scripts |
| **Goal Tracking** | Visual progress bars | Formulas in cells |
| **Mobile** | ✅ Fully responsive | ❌ Desktop only |
| **Sharing** | Can deploy online | Email Excel file |

---

## 💡 Pro Tips

### Quick Workflow:
1. **After each meet:**
   - Upload new `swim_history.html`
   - Click "Process GoMotion Data"
   - Done! Dashboard updates automatically

2. **Managing goals:**
   - Add goals at start of season
   - Check progress after each meet
   - Update goals as you achieve them

3. **Analytics:**
   - Use event comparison to identify weak strokes
   - Use improvement timeline to track training effectiveness
   - Compare different training periods

### Performance Tips:
- App loads faster if you keep data files in same folder
- Clear cache occasionally if app slows down
- Use sidebar for quick navigation

### Mobile Use:
- Works great on tablets and phones
- Sidebar auto-collapses on mobile
- Charts are touch-friendly
- Perfect for checking stats at meets!

---

## 🚀 Advanced: Deploy Online

Want to access your app from anywhere? Deploy it for free!

### Option 1: Streamlit Cloud (Easiest)

1. **Create GitHub repository:**
   - Upload your code to GitHub
   - Include: `swim_app.py`, `requirements.txt`, all Python scripts

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Click "Deploy"

3. **Access from anywhere:**
   - Get a public URL like `yourapp.streamlit.app`
   - Share with coaches, family
   - Update data from any device

**Note:** Be careful about sharing personal data publicly!

### Option 2: Local Network Access

Run on your computer, access from other devices on your network:

```bash
streamlit run swim_app.py --server.address 0.0.0.0
```

Then access from other devices using your computer's IP address.

---

## ❓ Troubleshooting

**Problem: "streamlit: command not found"**
```bash
# Install Streamlit
pip install streamlit
```

**Problem: "ModuleNotFoundError: No module named 'plotly'"**
```bash
# Install all requirements
pip install -r requirements.txt
```

**Problem: App won't start**
- Make sure you're in the right folder (`cd Desktop/PY/swim_project`)
- Check that `swim_app.py` is in the current folder
- Try: `python -m streamlit run swim_app.py`

**Problem: Upload not working**
- Make sure scraper.py, cleaner.py, grader.py are in same folder
- Check that standards.json exists
- Try running scripts manually first to verify they work

**Problem: Charts not showing**
- Install plotly: `pip install plotly`
- Clear browser cache
- Try a different browser

**Problem: Slow performance**
- Click "Clear Cache" in Settings
- Close other browser tabs
- Restart the app

---

## 🔄 Updating the App

When you want to modify the app:

1. **Stop the current app:** Press `Ctrl+C` in terminal
2. **Edit `swim_app.py`** in any text editor
3. **Save changes**
4. **Restart:** `streamlit run swim_app.py`
5. **Refresh browser** - changes appear automatically!

Streamlit has "hot reload" - you can often just save and it updates!

---

## 🆚 When to Use Web App vs. Excel

**Use Streamlit App when:**
- ✅ You want easy data upload
- ✅ You need to check stats on your phone
- ✅ You want interactive charts
- ✅ You want to share with others
- ✅ You prefer a modern interface

**Use Excel Dashboard when:**
- ✅ You need to print reports
- ✅ You want to edit data directly
- ✅ You need custom formulas
- ✅ You're comfortable with Excel
- ✅ You don't have internet access

**Best approach:** Use both!
- Web app for daily tracking and viewing
- Excel for detailed analysis and printing

---

## 🎯 Next Steps

Once you're comfortable with the basic app, you can:

1. **Customize the look:**
   - Edit the CSS in `swim_app.py`
   - Change colors, fonts, layouts

2. **Add features:**
   - Race splits analysis
   - Training log integration
   - Teammate comparisons
   - Meet predictions

3. **Deploy online:**
   - Free hosting on Streamlit Cloud
   - Access from anywhere
   - Share with coach/family

4. **Connect to database:**
   - Replace CSV files with SQLite
   - Better performance
   - More reliable data storage

---

## 📞 Need Help?

If you run into issues:

1. Check this guide first
2. Read error messages carefully
3. Try the troubleshooting section
4. Google the error message
5. Check Streamlit documentation: [docs.streamlit.io](https://docs.streamlit.io)

---

**Have fun tracking your progress! 🏊‍♂️💪**
