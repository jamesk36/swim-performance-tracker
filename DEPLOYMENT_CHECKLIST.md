# 🚀 Deployment Checklist

Use this checklist when you get home to quickly deploy your swim tracker to Streamlit Cloud.

## ✅ Pre-Deployment (Do This First)

### 1. Organize Your Files

**In your Desktop/PY/swim_project folder, you should have:**

**Core Application Files (MUST commit):**
- [ ] `swim_app.py` - Streamlit web app
- [ ] `scraper.py` - GoMotion parser
- [ ] `cleaner.py` - Data cleaner
- [ ] `grader.py` - Standards grader
- [ ] `merge_swims.py` - High school merger
- [ ] `create_dashboard.py` - Excel generator
- [ ] `check_hs_swims.py` - Diagnostic tool

**Configuration Files (MUST commit):**
- [ ] `requirements.txt` - Python dependencies
- [ ] `standards.json` - USA Swimming standards
- [ ] `.gitignore` - Files to exclude
- [ ] `README.md` - Project documentation

**Template Files (RECOMMENDED to commit):**
- [ ] `goals.csv` - Empty or example goals
- [ ] `high_school_swims.csv` - Empty or example swims

**Documentation (OPTIONAL but recommended):**
- [ ] `PROCESS_GUIDE.md`
- [ ] `DASHBOARD_GUIDE.md`
- [ ] `GOALS_GUIDE.md`
- [ ] `STREAMLIT_GUIDE.md`

**Data Files (DO NOT commit - add to .gitignore):**
- [ ] ~~`swim_history.html`~~ - Too large, personal
- [ ] ~~`raw_swim_data.csv`~~ - Generated file
- [ ] ~~`clean_swim_data.xlsx`~~ - Generated file
- [ ] ~~`graded_swim_data.xlsx`~~ - Generated file
- [ ] ~~`Swim_Dashboard.xlsx`~~ - Generated file

---

## 📝 Step-by-Step Deployment

### Step 1: Initialize Git Repository (5 minutes)

Open terminal in your project folder:

```bash
cd Desktop/PY/swim_project

# Initialize git
git init

# Add all files (respects .gitignore)
git add .

# First commit
git commit -m "Initial commit - Swim Performance Tracker v1.0"
```

**Verify what's being committed:**
```bash
git status
```

**Expected output:**
- ✅ All .py files
- ✅ .md documentation files
- ✅ requirements.txt
- ✅ standards.json
- ✅ Template CSV files
- ❌ NO .xlsx, .html, or large data files

---

### Step 2: Create GitHub Repository (3 minutes)

1. **Go to GitHub.com**
2. **Click "New repository"** (green button)
3. **Repository settings:**
   - Name: `swim-performance-tracker` (or your choice)
   - Description: "Track and analyze competitive swimming performance"
   - Visibility: **Private** (recommended) or Public
   - ❌ **DO NOT** initialize with README (you already have one)
   - ❌ **DO NOT** add .gitignore (you already have one)
   - ❌ **DO NOT** choose a license yet
4. **Click "Create repository"**

**Copy the repository URL** (looks like: `https://github.com/YOUR_USERNAME/swim-performance-tracker.git`)

---

### Step 3: Push to GitHub (2 minutes)

Back in your terminal:

```bash
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/swim-performance-tracker.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Expected output:**
```
Enumerating objects: XX, done.
Counting objects: 100% (XX/XX), done.
Writing objects: 100% (XX/XX), done.
Total XX (delta 0), reused 0 (delta 0)
To https://github.com/YOUR_USERNAME/swim-performance-tracker.git
 * [new branch]      main -> main
```

**Verify on GitHub:**
- Refresh your repository page
- Should see all files listed
- README.md should be displayed at bottom

---

### Step 4: Deploy to Streamlit Cloud (5 minutes)

1. **Go to [share.streamlit.io](https://share.streamlit.io)**

2. **Sign in with GitHub** (you already linked this)

3. **Click "New app"**

4. **Configure deployment:**
   - **Repository:** Select `YOUR_USERNAME/swim-performance-tracker`
   - **Branch:** `main`
   - **Main file path:** `swim_app.py`
   - **App URL:** Choose a custom URL (e.g., `yourname-swim-tracker`)

5. **Advanced settings (click to expand):**
   - **Python version:** 3.9 or 3.10 (default is fine)
   - **Secrets:** Leave blank for now
   - **Resource limits:** Default is fine

6. **Click "Deploy!"**

**Wait for deployment (2-5 minutes):**
- You'll see logs streaming
- "Installing dependencies..."
- "Running streamlit..."
- ✅ "Your app is live!"

---

### Step 5: Test Your Deployed App (5 minutes)

1. **Open your app URL** (e.g., `https://yourname-swim-tracker.streamlit.app`)

2. **Test core features:**
   - [ ] Dashboard loads
   - [ ] Navigation works (sidebar)
   - [ ] Try uploading a small test file
   - [ ] Check all pages load

3. **Known limitations on deployed version:**
   - ⚠️ Data won't persist between sessions (files are temporary)
   - ⚠️ File uploads work, but data resets when you reload
   - ℹ️ This is normal for Streamlit Cloud free tier

---

## 🔧 Post-Deployment Configuration

### Option 1: Data Persistence (Recommended for Personal Use)

**Problem:** Streamlit Cloud doesn't save uploaded files between sessions.

**Solution A: Use GitHub as data storage**
1. Create a separate **private** repo for data: `swim-data-private`
2. Store your CSV/Excel files there
3. Modify app to read from GitHub (advanced)

**Solution B: Connect to Google Sheets**
1. Set up Google Sheets integration
2. Store data in sheets
3. Modify app to read/write to Sheets
4. Requires API credentials

**Solution C: Keep it local + manual updates**
1. Run app locally when you need to upload data
2. Use deployed version for viewing only
3. Simplest option!

### Option 2: Add Secrets (For Sensitive Data)

If you add features like email notifications or API integrations:

1. **In Streamlit Cloud:**
   - Click your app → Settings → Secrets
   - Add in TOML format:
   ```toml
   [database]
   username = "your_username"
   password = "your_password"
   ```

2. **In your code:**
   ```python
   import streamlit as st
   username = st.secrets["database"]["username"]
   ```

---

## 📱 Sharing Your App

### Share with Family/Coach

**URL to share:** `https://yourname-swim-tracker.streamlit.app`

**What they can do:**
- ✅ View dashboard
- ✅ See all visualizations
- ✅ Upload their own data (won't interfere with yours)
- ✅ Works on any device (phone, tablet, computer)

**What they CAN'T do:**
- ❌ See your data (it's only visible during your session)
- ❌ Modify your files
- ❌ Access your GitHub repo (unless you share it)

### Making it Private

**Option 1: Add password (Streamlit Cloud Pro - $20/month)**
- Built-in authentication
- User management
- Worth it for teams

**Option 2: Custom authentication (Free)**
- Add simple password in app code
- Not super secure, but deters casual access
- Example:
```python
password = st.text_input("Password", type="password")
if password != "your_password_here":
    st.stop()
```

**Option 3: Keep GitHub repo private**
- App URL is public but hard to guess
- Share URL only with people you trust
- Most common approach for personal apps

---

## 🔄 Updating Your Deployed App

When you make changes:

```bash
# Make your changes to code
# Test locally first
streamlit run swim_app.py

# Commit changes
git add .
git commit -m "Description of changes"

# Push to GitHub
git push

# Streamlit Cloud automatically redeploys! (1-2 minutes)
```

**Auto-deployment is ON by default** - any push to `main` triggers redeployment.

---

## ✅ Final Checklist

Before you leave work:
- [ ] README.md downloaded and reviewed
- [ ] Deployment checklist saved
- [ ] GitHub repo created and ready
- [ ] Streamlit Cloud account linked to GitHub
- [ ] Know your app URL format preference

When you get home (30-45 minutes total):
- [ ] Step 1: Git init & commit (5 min)
- [ ] Step 2: Create GitHub repo (3 min)
- [ ] Step 3: Push to GitHub (2 min)
- [ ] Step 4: Deploy to Streamlit (5 min)
- [ ] Step 5: Test deployed app (5 min)
- [ ] Share with family/coach (5 min)
- [ ] Celebrate! 🎉

---

## 🆘 Troubleshooting

### "git: command not found"
**Solution:** Install Git from [git-scm.com](https://git-scm.com/)

### "Permission denied (publickey)"
**Solution:** 
```bash
# Use HTTPS instead of SSH
git remote set-url origin https://github.com/YOUR_USERNAME/swim-performance-tracker.git
```

### Streamlit app won't start
**Check the logs in Streamlit Cloud:**
1. Click your app
2. Click "Manage app"
3. View logs
4. Common issues:
   - Missing file in requirements.txt
   - Python version mismatch
   - File path issues

### App is slow
**Free tier limitations:**
- Sleeps after inactivity
- Limited resources
- First visit after sleep is slow (15-30 seconds)
- Subsequent visits are fast

### Data doesn't persist
**This is normal!** Options:
1. Run locally when uploading data
2. Set up external storage (Google Sheets, database)
3. Upgrade to paid plan with storage

---

## 📊 Expected Timeline

**Total time when you get home:** ~30-45 minutes

- Initial setup: 15-20 min
- Deployment: 5-10 min
- Testing: 5-10 min
- Troubleshooting buffer: 5-10 min

**After that:**
- Updates: 2-3 minutes per change
- Viewing: Instant (just open URL)

---

## 🎯 Success Criteria

You'll know it worked when:
1. ✅ GitHub repo shows all your files
2. ✅ Streamlit Cloud shows "Your app is running"
3. ✅ You can open the URL and see your dashboard
4. ✅ Navigation works on all pages
5. ✅ You can upload a test file and process it

---

## 🚀 Next Steps After Deployment

**Week 1:**
- Share URL with family
- Upload a few test meets
- Set some goals
- Get feedback from users

**Week 2:**
- Add any requested features
- Fix any bugs found
- Customize styling if desired
- Consider adding authentication

**Month 1:**
- Track full season of meets
- Analyze improvement trends
- Share with coach if helpful
- Consider additional features

---

**You're ready to deploy! When you get home, just follow this checklist step-by-step.** 🎉

**Questions? Issues?** 
- Check Streamlit docs: [docs.streamlit.io](https://docs.streamlit.io)
- GitHub help: [docs.github.com](https://docs.github.com)
- Streamlit Community: [discuss.streamlit.io](https://discuss.streamlit.io)

Good luck! 🏊‍♂️
