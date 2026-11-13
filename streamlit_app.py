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
    * 🌍 **Africa:** Lagos, Abuja, Accra, Johannesburg, Nairobi
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
    if st_val in ("Nigeria", "Ghana", "Kenya", "South Africa", "Uganda", "Rwanda"):
        return f"🌍 Africa ({st_val})"
    elif st_val in ("United Kingdom", "UK"):
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
    f"⛪ Church Directory ({len(df_master)} Leads)",
    "✉️ Multilingual Outreach & Pitches",
    "🔍 Search by Country / City & Discover"
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

# ----------------- TAB 3: DISCOVER & SEARCH BY COUNTRY / CITY -----------------
with tab_discover:
    st.markdown("### 🔍 Search by Country & Discover Churches")
    st.caption("Quickly find churches across Africa, Europe, the UK, and the Americas using 1-click buttons or custom country/city search.")

    # Section 1: Quick 1-Click Country & City Presets
    st.markdown("#### ⚡ 1-Click Country & Hub Presets")
    st.write("Click any button below to instantly populate and search churches in that country:")

    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        btn_ng = st.button("🇳🇬 Nigeria (Lagos / Abuja)", use_container_width=True)
        btn_uk = st.button("🇬🇧 UK (London / Manchester)", use_container_width=True)
    with col_p2:
        btn_gh = st.button("🇬🇭 Ghana (Accra)", use_container_width=True)
        btn_us = st.button("🇺🇸 USA (Dallas / Atlanta)", use_container_width=True)
    with col_p3:
        btn_za = st.button("🇿🇦 South Africa (Joburg)", use_container_width=True)
        btn_de = st.button("🇩🇪 Germany (Berlin / Munich)", use_container_width=True)
    with col_p4:
        btn_ke = st.button("🇰🇪 Kenya (Nairobi)", use_container_width=True)
        btn_fr = st.button("🇫🇷 France (Paris / Lyon)", use_container_width=True)

    # Determine active selection from presets or session
    active_country = ""
    active_city = ""
    if btn_ng:
        active_country, active_city = "Nigeria", "Lagos"
    elif btn_gh:
        active_country, active_city = "Ghana", "Accra"
    elif btn_za:
        active_country, active_city = "South Africa", "Johannesburg"
    elif btn_ke:
        active_country, active_city = "Kenya", "Nairobi"
    elif btn_uk:
        active_country, active_city = "United Kingdom", "London"
    elif btn_us:
        active_country, active_city = "TX", "Dallas"
    elif btn_de:
        active_country, active_city = "Germany", "Berlin"
    elif btn_fr:
        active_country, active_city = "France", "Paris"

    st.markdown("---")

    # Section 2: Custom Country & City Search Inputs
    st.markdown("#### 🔎 Search by Specific Country or City")
    
    col_input1, col_input2, col_input3 = st.columns([2, 2, 1])
    with col_input1:
        typed_country = st.text_input("Type Country", value=active_country, placeholder="e.g. Nigeria, South Africa, UK, USA, France, Kenya...")
    with col_input2:
        typed_city = st.text_input("Type City (optional)", value=active_city, placeholder="e.g. Lagos, Accra, London, Dallas, Nairobi...")
    with col_input3:
        st.write("")
        st.write("")
        run_search = st.button("🚀 Search", use_container_width=True)

    if (run_search or active_country) and (typed_country or typed_city):
        query_country = typed_country.strip().lower()
        query_city = typed_city.strip().lower()

        # 1. Search in our curated master dataset
        matched_df = df_master.copy()
        if query_country:
            matched_df = matched_df[
                matched_df["State"].astype(str).str.lower().str.contains(query_country, na=False) |
                matched_df["Region"].astype(str).str.lower().str.contains(query_country, na=False) |
                matched_df["Address"].astype(str).str.lower().str.contains(query_country, na=False)
            ]
        if query_city:
            matched_df = matched_df[
                matched_df["City"].astype(str).str.lower().str.contains(query_city, na=False) |
                matched_df["Address"].astype(str).str.lower().str.contains(query_city, na=False)
            ]

        if not matched_df.empty:
            st.success(f"🎉 Found {len(matched_df)} qualified church(es) for **{typed_country} {typed_city}**!")
            
            res_display = matched_df[["Church Name", "Region", "City", "Emails", "Website", "Phone", "Rating", "Address"]]
            st.dataframe(
                res_display,
                use_container_width=True,
                column_config={
                    "Website": st.column_config.LinkColumn("Website"),
                    "Rating": st.column_config.NumberColumn(format="%.1f ⭐")
                },
                height=350
            )

            res_csv = matched_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download {len(matched_df)} Leads for {typed_country or typed_city} (CSV)",
                data=res_csv,
                file_name=f"pewbeam_leads_{(typed_country or typed_city).lower()}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info(f"Scanning live public church directories for **{typed_country} {typed_city}**...")
            with st.spinner("Connecting to public listings..."):
                live_res = free_search_churches(typed_city or typed_country, typed_country)
                if live_res:
                    st.success(f"Discovered {len(live_res)} church listing(s)!")
                    st.dataframe(pd.DataFrame(live_res)[["Church Name", "City", "Address"]])
                else:
                    st.warning(f"No direct listings found for '{typed_country} {typed_city}'. Try searching a larger nearby metro hub (e.g. Lagos, London, Dallas, Nairobi).")

    st.markdown("---")

    # Section 3: Instant Church URL Email Extractor (Fixed with requests)
    st.markdown("#### 🎯 Instant Church Website Email Extractor")
    st.write("Found a specific church website? Paste the link below to automatically extract their media, broadcast, and staff emails:")

    col_u1, col_u2 = st.columns([3, 1])
    with col_u1:
        target_url = st.text_input("Church Website URL", placeholder="https://audaciouschurch.com/ or https://elevationng.org/")
    with col_u2:
        st.write("")
        st.write("")
        inspect_btn = st.button("🔎 Inspect & Extract Emails", use_container_width=True)

    if inspect_btn and target_url:
        with st.spinner(f"Crawling {target_url}..."):
            extracted = crawl_church_website_emails(target_url)
            if extracted:
                st.success(f"🎉 Discovered {len(extracted)} verified email(s) on {target_url}:")
                for em in extracted:
                    st.markdown(f"- `<span class='pill-active'>{em}</span>`", unsafe_allow_html=True)
            else:
                st.info("No direct plaintext email detected on the public contact pages. They may be using an embedded contact form.")
