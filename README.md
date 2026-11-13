# ⚡ Pewbeam Automated Church Outreach Hub

An automated lead generation, scraping, and personalized outreach engine built for **[Pewbeam](https://pewbeam.com/)** using **Apify**, Python, and Streamlit.

---

## 🎨 Pewbeam Brand Aesthetic
The dashboard is styled using Pewbeam's signature visual identity:
* **Background:** Obsidian Black & Deep Carbon (`#080707`, `#121010`)
* **Primary Brand Accent:** Radiant Pewbeam Orange (`#ff5700` / `#d44900`)
* **Live Status / Highlights:** Electric Neon Green (`#00ec66`) & Amber Warm Gold (`#ffd2b5`)
* **Borders & Elevation:** Sleek dark glassmorphism with subtle 1px border glow

---

## 📁 Directory Structure
```
pewbeam-outreach/
├── dashboard.py                   # Full interactive Web Dashboard (Streamlit)
├── run_dashboard.bat              # Double-click to launch on Windows
├── run_dashboard.ps1              # PowerShell launcher
├── scrape_churches.py             # CLI scraper for Google Maps + Website Emails (Apify)
├── generate_outreach.py           # CLI cold email & LinkedIn DM generator
├── pewbeam_church_leads_sample.csv# Preloaded sample leads to test the UI immediately
├── verify_apify.py                # Token verification script
├── .env.example                   # API Token configuration template
└── README.md                      # Documentation
```

---

## 🚀 How to Launch the Dashboard

### Option A: Double-Click (Easiest)
Simply double-click [`run_dashboard.bat`](file:///C:/Users/HP/.gemini/antigravity/scratch/pewbeam-outreach/run_dashboard.bat) inside the project folder.

### Option B: Terminal / PowerShell
```powershell
cd "C:\Users\HP\.gemini\antigravity\scratch\pewbeam-outreach"
python -m streamlit run dashboard.py
```
This will open `http://localhost:8501` in your browser.

---

## 🖥️ Dashboard Features

1. **📊 Scraped Church Leads Explorer:**
   * View all churches in interactive tables with live links to their websites and Google Maps.
   * Real-time metrics: Total Churches, Active Websites, Contact Emails Found, Average Google Rating.
   * Filters: Search by name/city, filter only churches with verified emails or websites.
   * One-click CSV download.

2. **🚀 New Scrape Job (Apify Engine):**
   * Input your target search cities (e.g. *Dallas TX, Atlanta GA, Nashville TN, London UK, Lagos NG*).
   * Customize max results and toggle automated website email extraction.
   * Real-time progress bar and status updates directly in the UI.

3. **✉️ Outreach Generator & Preview:**
   * Pick any church from the list to preview the customized Cold Email and LinkedIn DM.
   * Highlights church name, city, and pain points (e.g., pastor quoting unscripted verses, volunteer booth panic).
   * Export full mail-merge CSV ready for cold email platforms (**Instantly.ai**, **Smartlead.ai**, **Lemlist**).
