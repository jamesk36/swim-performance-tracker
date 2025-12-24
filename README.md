# 🏊‍♂️ Swim Performance Tracker

A comprehensive swim performance tracking and analysis system for competitive swimmers. Track times, analyze progress, set goals, and visualize improvement over time using USA Swimming standards.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

### 📊 Data Processing Pipeline
- **Automated GoMotion scraping** - Extract swim results from HTML
- **Data cleaning & formatting** - Convert raw data to structured format
- **USA Swimming standards grading** - Automatic AAAA/AAA/AA/A/BB/B classification
- **High school swim integration** - Manually add non-GoMotion results

### 📈 Excel Dashboard
- **Personal best lookup** - Interactive dropdown search
- **Time progression charts** - Visualize improvement over time
- **Goal tracking** - Set targets and monitor progress
- **Next standard calculator** - See what's needed for the next level
- **Standards breakdown** - Complete swim history analysis

### 🌐 Web Application
- **Modern Streamlit interface** - Clean, responsive design
- **Mobile-friendly** - Track progress from any device
- **Drag-and-drop upload** - Easy data import
- **Interactive charts** - Zoom, hover, explore your data
- **Real-time processing** - One-click pipeline execution
- **Goal management** - Web forms for easy updates

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/swim-tracker.git
cd swim-tracker
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Add your data files:**
- Download `swim_history.html` from GoMotion
- Place in project folder

### Running the Pipeline (Command Line)

Process swim data in 4 steps:

```bash
# 1. Extract data from HTML
python scraper.py

# 2. Clean and format
python cleaner.py

# 3. Merge high school swims (optional)
python merge_swims.py

# 4. Grade performances
python grader.py

# 5. Create Excel dashboard
python create_dashboard.py
```

### Running the Web App

```bash
streamlit run swim_app.py
```

Then open your browser to `http://localhost:8501`

## 📁 Project Structure

```
swim-tracker/
│
├── swim_app.py              # Streamlit web application
├── scraper.py               # GoMotion HTML parser
├── cleaner.py               # Data cleaning & formatting
├── grader.py                # USA Swimming standards grader
├── merge_swims.py           # High school swim merger
├── create_dashboard.py      # Excel dashboard generator
│
├── standards.json           # USA Swimming time standards (2021-2028)
├── goals.csv                # Season goals (user-editable)
├── high_school_swims.csv    # Manual swim entries
│
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── PROCESS_GUIDE.md        # Step-by-step usage guide
├── DASHBOARD_GUIDE.md      # Excel dashboard guide
├── GOALS_GUIDE.md          # Goal tracking guide
└── STREAMLIT_GUIDE.md      # Web app guide

# Generated files (not in repo)
├── swim_history.html        # Downloaded from GoMotion
├── raw_swim_data.csv        # Scraper output
├── clean_swim_data.xlsx     # Cleaner output
├── graded_swim_data.xlsx    # Grader output
└── Swim_Dashboard.xlsx      # Final Excel dashboard
```

## 📖 Documentation

- **[Process Guide](PROCESS_GUIDE.md)** - Complete workflow from GoMotion to dashboard
- **[Dashboard Guide](DASHBOARD_GUIDE.md)** - How to use the Excel dashboard
- **[Goals Guide](GOALS_GUIDE.md)** - Setting and tracking season goals
- **[Streamlit Guide](STREAMLIT_GUIDE.md)** - Web application user guide

## 🎯 Key Workflows

### Workflow 1: Update After a Meet (GoMotion Only)

```bash
# Download swim_history.html from GoMotion
python scraper.py
python cleaner.py
python grader.py
python create_dashboard.py
# Open Swim_Dashboard.xlsx
```

### Workflow 2: Add High School Swims

```bash
# 1. Edit high_school_swims.csv in Excel
# 2. Run pipeline with merge step
python scraper.py
python cleaner.py
python merge_swims.py
python grader.py
python create_dashboard.py
```

### Workflow 3: Use Web Interface

```bash
streamlit run swim_app.py
# Upload HTML file in browser
# Click "Process Data"
# View updated dashboard
```

## 🏆 Features Deep Dive

### USA Swimming Standards Integration
- **Automatic grading** based on age, date, and event
- **Multi-era support** (2021-2024 and 2024-2028 standards)
- **All courses** (SCY, SCM, LCM)
- **All age groups** (10&U through 17-18)
- **Comprehensive events** (50-1650 distances, all strokes)

### Goal Tracking System
- **Custom goals** - Set target times for any event
- **Progress monitoring** - See how many seconds to drop
- **Next standard targets** - Automatic calculation of what's needed
- **Color-coded feedback** - Visual progress indicators
- **Notes support** - Add context to goals

### Interactive Visualizations
- **Time progression charts** - See improvement over time
- **Standards distribution** - Breakdown of all swims
- **Stroke comparison** - Radar charts showing strengths
- **Improvement timeline** - Track rate of change
- **Personal best tables** - Best times by event

## 🌐 Deployment

### Deploy to Streamlit Cloud (Free)

1. **Push code to GitHub:**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Select `swim_app.py` as the main file
   - Click "Deploy"

3. **Access your app:**
   - Get a URL like `yourapp.streamlit.app`
   - Share with coaches, family, teammates
   - Update by pushing to GitHub

### Environment Variables (Optional)

For secure deployments, you can set:
- `DATA_PATH` - Custom data directory
- `STANDARDS_PATH` - Path to standards.json

## 🛠️ Development

### Adding New Features

The codebase is modular and easy to extend:

**Add a new data source:**
1. Create parser in new file (e.g., `newsite_scraper.py`)
2. Output to same format as `cleaner.py`
3. Merge with existing data

**Add new visualizations:**
1. Edit `swim_app.py`
2. Add to Analytics page
3. Use Plotly for interactive charts

**Add new standards:**
1. Edit `standards.json`
2. Follow existing structure
3. Re-run `grader.py`

### Running Tests

```bash
# Validate standards file
python -c "import json; json.load(open('standards.json'))"

# Check data integrity
python check_hs_swims.py

# Test merge function
python merge_swims.py
```

## 📊 Data Format

### Input: GoMotion HTML
- Save results page as complete HTML
- Name: `swim_history.html`

### Input: High School Swims CSV
```csv
Date,Age,Distance,Stroke,Round,Course,Finals,Time_Seconds,Meet
2024-12-05,14,100,Free,Finals,Yards,52.45Y,52.45,HS Dual Meet
```

### Output: Graded Data
| Date | Age | Distance | Stroke | Course | Finals | Standard | Meet |
|------|-----|----------|--------|--------|--------|----------|------|
| 2024-12-05 | 14 | 100 | Free | Yards | 51.07Y | AAA | Winter Champs |

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Automatic GoMotion login/scraping
- [ ] Split time analysis
- [ ] Peer comparisons
- [ ] Training log integration
- [ ] Mobile app (React Native)
- [ ] Coach notes/feedback system
- [ ] Photo attachments
- [ ] Race predictions (ML)
- [ ] Video analysis integration

## 📝 License

MIT License - feel free to use for personal or team use.

## 🙏 Acknowledgments

- **USA Swimming** - Time standards
- **GoMotion** - Meet results platform
- **Streamlit** - Web framework
- **Plotly** - Interactive charts

## 📞 Support

Found a bug? Have a feature request?

1. Check existing issues on GitHub
2. Create a new issue with details
3. Include error messages and screenshots

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ GoMotion scraping
- ✅ USA Swimming standards
- ✅ Excel dashboard
- ✅ Streamlit web app
- ✅ Goal tracking

### Version 1.1 (Planned)
- [ ] Automatic meet result fetching
- [ ] Email notifications for new times
- [ ] PDF report generation
- [ ] Training log module
- [ ] Teammate comparisons

### Version 2.0 (Future)
- [ ] Mobile app
- [ ] Coach portal
- [ ] Team management
- [ ] Meet predictions
- [ ] Social features

## 💡 Tips

**Best Practices:**
- Update after every meet for accurate trends
- Set realistic, achievable goals
- Back up your data files regularly
- Use web app for daily checks, Excel for deep analysis

**Performance:**
- Keep standards.json in project root
- Don't commit large HTML files to GitHub
- Use .gitignore for generated data files

## 🏊‍♂️ Happy Swimming!

Track your progress, crush your goals, and achieve new personal bests! 🚀

---

**Built with ❤️ for competitive swimmers**
