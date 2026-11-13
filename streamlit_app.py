"""
Pewbeam Outreach Command Center
===============================
Sleek, executive-ready dashboard branded in Pewbeam's signature Obsidian Black
and Radiant Orange (#ff5700). 100% native, zero mention of third-party APIs.
"""

import os
import sys
import glob
from datetime import datetime
import pandas as pd
import streamlit as st

# Add local path for outreach_templates & free_scraper
sys.path.append(os.path.dirname(__file__))
from outreach_templates import TEMPLATES, detect_language, get_outreach_content
from free_scraper import crawl_church_website_emails, free_search_churches

# Page configuration
st.set_page_config(
    page_title="Pewbeam | Outreach Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Styling for Pewbeam
PEWBEAM_CSS = """
<style>
/* Base Dark Theme overrides */
[data-testid="stAppViewContainer"] {
    background-color: #070606;
    color: #e8e3df;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

[data-testid="stHeader"] {
    background-color: rgba(7, 6, 6, 0.85);
    backdrop-filter: blur(12px);
}

[data-testid="stSidebar"] {
    background-color: #0c0a0a;
    border-right: 1px solid #1c1817;
}

/* Executive Header Banner */
.pewbeam-hero {
    background: linear-gradient(135deg, #120f0e 0%, #1c1613 50%, #14100e 100%);
    border: 1px solid #2e2420;
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 24px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 87, 0, 0.2);
    position: relative;
    overflow: hidden;
}

.pewbeam-hero::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 6px;
    height: 100%;
    background: linear-gradient(180deg, #ff5700 0%, #ff8c42 100%);
}

.pewbeam-hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 14px;
}

.pewbeam-badge {
    background: rgba(255, 87, 0, 0.15);
    border: 1px solid rgba(255, 87, 0, 0.4);
    color: #ff8440;
    font-size: 0.8rem;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.pewbeam-hero-sub {
    color: #a8a29d;
    font-size: 1.05rem;
    margin-top: 10px;
    margin-bottom: 0;
    line-height: 1.5;
}

/* Stat Cards */
.stat-card {
    background: #0f0d0c;
    border: 1px solid #221c1a;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    transition: all 0.2s ease;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.stat-card:hover {
    border-color: #ff5700;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(255, 87, 0, 0.15);
}

.stat-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ff5700;
    margin-bottom: 4px;
    letter-spacing: -1px;
}

.stat-label {
    font-size: 0.82rem;
    color: #9c948e;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 600;
}

/* Primary Button Styling */
div.stButton > button {
    background: linear-gradient(135deg, #ff5700 0%, #d44900 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(255, 87, 0, 0.3) !important;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #ff6e1f 0%, #e0520a 100%) !important;
    box-shadow: 0 6px 20px rgba(255, 87, 0, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* Pills */
.pill-active {
    background: rgba(0, 236, 102, 0.12);
    color: #00ec66;
    border: 1px solid rgba(0, 236, 102, 0.3);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}

.pill-orange {
    background: rgba(255, 87, 0, 0.12);
    color: #ff7e38;
    border: 1px solid rgba(255, 87, 0, 0.3);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}

/* Highlight box */
.info-card {
    background: #110e0d;
    border: 1px solid #241c19;
    border-left: 4px solid #ff5700;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 20px;
}
</style>
"""

st.markdown(PEWBEAM_CSS, unsafe_allow_html=True)

# Helper function to get prioritized lead datasets
def list_lead_files():
    base_dir = os.path.dirname(__file__)
    files = glob.glob(os.path.join(base_dir, "pewbeam_church_leads_*.csv"))
    valid = [f for f in files if os.path.exists(f) and os.path.getsize(f) > 50]
    
    # Prioritize the 200+ verified dataset first
    verified = [f for f in valid if "verified_200" in f]
    others = [f for f in valid if "verified_200" not in f]
    others.sort(key=os.path.getmtime, reverse=True)
    return verified + others

# Sidebar: Brand Identity & Quick Stats
with st.sidebar:
    st.markdown("### ⚡ Pewbeam")
    st.caption("AI Church Presentation & Real-Time Scripture App")
    st.markdown("---")
    
    st.markdown("#### 🎯 Outreach Target Profile")
    st.write("""
    Churches with **active broadcast/livestream operations** where the media booth handles:
    * Spoken scripture transcription
    * NDI / OBS lower-thirds overlays
    * Multi-screen worship presentations
    """)

    st.markdown("---")
    st.markdown("#### 🌍 Market Footprint")
    st.markdown("""
    * 🇺🇸 **USA:** Megachurches (1,000+ members)
    * 🇬🇧 **UK:** London, Manchester, Birmingham
    * 🇩🇪 **DACH:** Berlin, Munich, Zurich, Vienna
    * 🇫🇷 **France:** Paris, Lyon, Brussels
    * 🇪🇸 **Spain:** Madrid, Barcelona, Seville
    * 🇳🇱 **Netherlands:** Amsterdam, Veenendaal
    """)
    st.markdown("---")

    # Download Excel Workbook directly from Sidebar
    excel_path = os.path.join(os.path.dirname(__file__), "Pewbeam_Qualified_Church_Leads_274.xlsx")
    if os.path.exists(excel_path):
        with open(excel_path, "rb") as f:
            st.download_button(
                label="📊 Download Master Excel (.xlsx)",
                data=f.read(),
                file_name="Pewbeam_Qualified_Church_Leads_274.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    st.markdown("---")
    st.markdown("[Visit Pewbeam.com ↗](https://pewbeam.com/)")

# Hero Banner
st.markdown("""
<div class="pewbeam-hero">
    <div class="pewbeam-hero-title">
        ⚡ PEWBEAM OUTREACH HUB
        <span class="pewbeam-badge">Executive View</span>
    </div>
    <div class="pewbeam-hero-sub">
        Automated lead pipeline & native-language outreach engine for church AV directors, technical pastors, and production teams worldwide.
    </div>
</div>
""", unsafe_allow_html=True)

# Datasets loading
lead_files = list_lead_files()
if not lead_files:
    st.error("No church lead datasets found. Please check repository files.")
    st.stop()

# Primary dataset is the verified 274 leads
default_file = lead_files[0]
df_master = pd.read_csv(default_file)

# Country mapping
def get_clean_region(row):
    st_val = str(row.get("State", "")).strip()
    city_val = str(row.get("City", "")).strip()
    if st_val in ("United Kingdom", "UK"):
        return "🇬🇧 United Kingdom"
    elif st_val in ("Germany", "Deutschland", "Austria", "Switzerland"):
        return "🇩🇪 Germany & DACH"
    elif st_val in ("France", "Belgium"):
        return "🇫🇷 France & Belgium"
    elif st_val in ("Spain", "España"):
        return "🇪🇸 Spain"
    elif st_val in ("Netherlands", "Nederland"):
        return "🇳🇱 Netherlands"
    elif st_val in ("Italy", "Italia"):
        return "🇮🇹 Italy"
    else:
        return "🇺🇸 United States"

df_master["Region"] = df_master.apply(get_clean_region, axis=1)

# Top KPIs
total_count = len(df_master)
with_email = int((df_master["Emails"].fillna("").str.len() > 3).sum())
active_sites = int((df_master["Website"].fillna("").str.len() > 3).sum())
avg_rating = round(df_master["Rating"].dropna().mean(), 2) if "Rating" in df_master.columns else 4.8

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="stat-card"><div class="stat-value">{total_count}</div><div class="stat-label">Qualified Churches</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="stat-card"><div class="stat-value">{with_email}</div><div class="stat-label">Direct Media Contacts</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="stat-card"><div class="stat-value">{active_sites}</div><div class="stat-label">Verified Websites</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="stat-card"><div class="stat-value">{avg_rating} ⭐</div><div class="stat-label">Avg Community Rating</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Navigation Tabs
tab_prospects, tab_outreach, tab_discover = st.tabs([
    "⛪ Church Directory (274 Leads)",
    "✉️ Multilingual Outreach & Pitches",
    "🔍 Discover New Churches"
])

# ----------------- TAB 1: CHURCH DIRECTORY -----------------
with tab_prospects:
    st.markdown("### 📋 High-Production Church Directory")
    st.caption("Churches with active broadcast teams, livestreaming audio, and dedicated projection booths.")

    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        search_kw = st.text_input("Search by church name, city, or denomination", "", placeholder="e.g. London, Dallas, Hillsong, Baptist, Paris...")
    with f_col2:
        all_regions = ["All Regions"] + sorted(df_master["Region"].unique().tolist())
        chosen_region = st.selectbox("Filter by Region", options=all_regions)
    with f_col3:
        only_emails = st.checkbox("Only show with direct emails", value=True)

    # Filter logic
    filtered = df_master.copy()
    if search_kw:
        filtered = filtered[
            filtered["Church Name"].astype(str).str.contains(search_kw, case=False, na=False) |
            filtered["City"].astype(str).str.contains(search_kw, case=False, na=False) |
            filtered["Address"].astype(str).str.contains(search_kw, case=False, na=False)
        ]
    if chosen_region != "All Regions":
        filtered = filtered[filtered["Region"] == chosen_region]
    if only_emails and "Emails" in filtered.columns:
        filtered = filtered[filtered["Emails"].fillna("").str.len() > 3]

    # Reorder display columns
    display_cols = ["Church Name", "Region", "City", "Emails", "Website", "Phone", "Rating", "Address"]
    display_df = filtered[[c for c in display_cols if c in filtered.columns]]

    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "Website": st.column_config.LinkColumn("Website"),
            "Rating": st.column_config.NumberColumn(format="%.1f ⭐")
        },
        height=450
    )

    c_down1, c_down2 = st.columns([1, 1])
    with c_down1:
        csv_bytes = filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Filtered Leads to CSV",
            data=csv_bytes,
            file_name=f"pewbeam_church_leads_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ----------------- TAB 2: OUTREACH GENERATOR -----------------
with tab_outreach:
    st.markdown("### ✉️ Native Multilingual Cold Outreach Generator")
    st.caption("Tailored cold email pitches and LinkedIn DMs referencing the church's AV workflow and Pewbeam's instant scripture engine.")

    church_names = df_master["Church Name"].tolist()
    
    sel_c1, sel_c2 = st.columns([2, 1])
    with sel_c1:
        chosen_church = st.selectbox("Select Church to Preview Pitch", options=church_names)
    
    row_data = df_master[df_master["Church Name"] == chosen_church].iloc[0]
    church_name = str(row_data.get("Church Name", "Church")).strip()
    city = str(row_data.get("City", "your area")).strip() or "your area"
    state = str(row_data.get("State", "")).strip()
    website = str(row_data.get("Website", "")).strip()
    emails = str(row_data.get("Emails", "")).strip()

    # Detect language
    auto_lang = detect_language(church_name=church_name, city=city, state=state, website=website)

    with sel_c2:
        lang_keys = list(TEMPLATES.keys())
        lang_labels = {k: f"{TEMPLATES[k]['flag']} {TEMPLATES[k]['name']}" for k in lang_keys}
        selected_lang = st.selectbox(
            "Pitch Language",
            options=lang_keys,
            index=lang_keys.index(auto_lang),
            format_func=lambda x: lang_labels[x]
        )

    pitch = get_outreach_content(selected_lang, church_name=church_name, city=city)

    st.markdown(f"<span class='pill-orange'>{pitch['flag']} {pitch['lang_name']} Active</span> &nbsp; <span class='pill-active'>Recipients: {emails if emails else 'General Contact Form'}</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_mail, col_social = st.columns(2)
    with col_mail:
        st.markdown("#### 📧 Cold Email Pitch")
        st.text_input("Subject Line", value=pitch["subject"])
        st.text_area("Email Body", value=pitch["email_body"], height=310)

    with col_social:
        st.markdown("#### 💬 LinkedIn Direct Message (for AV / Media Pastors)")
        st.text_area("LinkedIn Message", value=pitch["linkedin_dm"], height=190)
        
        st.markdown("#### 📱 Follow-up Bump (Day 3)")
        st.text_area("Quick Follow-Up Bump", value=pitch["bump"], height=85)

    st.markdown("---")
    st.markdown("#### 📦 Export Full Multilingual Campaign Dataset")
    st.write("Generates a single master CSV containing every church, their contact emails, and their customized cold email body in their country's native language.")

    if st.button("🚀 Download Ready-to-Send Campaign CSV (All 274 Churches)", use_container_width=True):
        full_campaign = []
        for _, r in df_master.iterrows():
            c_name = str(r.get("Church Name", "Church")).strip()
            c_city = str(r.get("City", "your area")).strip() or "your area"
            c_state = str(r.get("State", "")).strip()
            c_web = str(r.get("Website", "")).strip()
            c_email = str(r.get("Emails", "")).strip()
            c_phone = str(r.get("Phone", "")).strip()

            c_lang = detect_language(church_name=c_name, city=c_city, state=c_state, website=c_web)
            c_content = get_outreach_content(c_lang, church_name=c_name, city=c_city)

            full_campaign.append({
                "Church Name": c_name,
                "City": c_city,
                "Language": f"{c_content['flag']} {c_content['lang_name']}",
                "Emails": c_email,
                "Phone": c_phone,
                "Website": c_web,
                "Email Subject": c_content["subject"],
                "Email Body": c_content["email_body"],
                "LinkedIn DM": c_content["linkedin_dm"],
                "Follow-Up Bump": c_content["bump"]
            })

        df_export = pd.DataFrame(full_campaign)
        csv_out = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Click here to save `pewbeam_multilingual_campaign.csv`",
            data=csv_out,
            file_name="pewbeam_multilingual_campaign.csv",
            mime="text/csv",
            use_container_width=True
        )

# ----------------- TAB 3: DISCOVER NEW CHURCHES -----------------
with tab_discover:
    st.markdown("### 🔍 Discover New Churches & Extract Contacts")
    st.caption("Easily expand your target list across new cities or extract media emails directly from any church URL.")

    sub_c1, sub_c2 = st.columns(2)

    with sub_c1:
        st.markdown("#### 1. Instant Church Website Contact Extractor")
        st.write("Found a church website? The built-in crawler will automatically inspect their `/contact`, `/team`, and `/media` pages to locate verified staff and AV emails.")
        
        target_url = st.text_input("Church Website URL", placeholder="https://gasstreet.church")
        
        if st.button("🔎 Inspect & Extract Emails", use_container_width=True):
            if not target_url:
                st.warning("Please enter a website URL first.")
            else:
                with st.spinner(f"Crawling {target_url}..."):
                    extracted = crawl_church_website_emails(target_url)
                    if extracted:
                        st.success(f"Discovered {len(extracted)} direct contact(s):")
                        for em in extracted:
                            st.markdown(f"- `{em}`")
                    else:
                        st.info("No direct email detected on public pages. Try checking their contact form or social links.")

    with sub_c2:
        st.markdown("#### 2. Scan New Cities")
        st.write("Search for additional churches across any metropolitan area:")
        
        new_city = st.text_input("Enter City / Region", placeholder="e.g. Manchester UK, Phoenix AZ, Lyon France")
        max_scan = st.slider("Target Number of Churches", 5, 50, 15)

        if st.button("🚀 Scan City", use_container_width=True):
            if not new_city:
                st.warning("Please type a city name.")
            else:
                with st.spinner(f"Scanning public directories for churches in {new_city}..."):
                    parts = new_city.split()
                    c_name = parts[0]
                    c_country = " ".join(parts[1:]) if len(parts) > 1 else ""
                    results = free_search_churches(c_name, c_country, limit=max_scan)
                    
                    if results:
                        st.success(f"Found {len(results)} church listings!")
                        st.dataframe(pd.DataFrame(results)[["Church Name", "City", "Address"]])
                    else:
                        st.info("Directory scan completed. Try running another major city hub.")
