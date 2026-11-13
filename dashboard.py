"""
Pewbeam Outreach Hub - Streamlit Dashboard
Branded with Pewbeam's signature Obsidian Black & Radiant Orange theme (#ff5700).
Supports Europe, Americas, UK, and automatic localized messaging in English, German, French, Spanish, Italian, Dutch, and Portuguese.
"""

import os
import sys
import glob
import json
import csv
from datetime import datetime
import pandas as pd
import streamlit as st
from apify_client import ApifyClient

# Add local path for outreach_templates import
sys.path.append(os.path.dirname(__file__))
from outreach_templates import TEMPLATES, detect_language, get_outreach_content

# Set page configuration
st.set_page_config(
    page_title="Pewbeam Outreach Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Pewbeam Brand Identity
PEWBEAM_CSS = """
<style>
/* Base Dark Theme overrides */
[data-testid="stAppViewContainer"] {
    background-color: #080707;
    color: #e5e0db;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

[data-testid="stHeader"] {
    background-color: rgba(8, 7, 7, 0.85);
    backdrop-filter: blur(10px);
}

[data-testid="stSidebar"] {
    background-color: #0e0d0d;
    border-right: 1px solid #1f1d1b;
}

/* Pewbeam Header Banner */
.pewbeam-header {
    background: linear-gradient(135deg, #131110 0%, #1a1614 100%);
    border: 1px solid #2f2724;
    border-left: 5px solid #ff5700;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.pewbeam-title {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.pewbeam-title span.badge {
    background-color: #ff5700;
    color: #ffffff;
    font-size: 0.8rem;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.pewbeam-subtitle {
    color: #9f9a95;
    font-size: 1.05rem;
    margin-top: 8px;
    margin-bottom: 0;
}

/* Metric Cards */
.metric-box {
    background: #121010;
    border: 1px solid #262220;
    border-radius: 10px;
    padding: 18px;
    text-align: center;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.metric-box:hover {
    border-color: #ff5700;
    transform: translateY(-2px);
}

.metric-num {
    font-size: 2rem;
    font-weight: 700;
    color: #ff5700;
    margin-bottom: 4px;
}

.metric-label {
    font-size: 0.85rem;
    color: #a49f99;
    text-transform: uppercase;
    letter-spacing: 0.5px;
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
    box-shadow: 0 4px 12px rgba(255, 87, 0, 0.25) !important;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #ff6a1a 0%, #e0520a 100%) !important;
    box-shadow: 0 6px 18px rgba(255, 87, 0, 0.4) !important;
    transform: translateY(-1px) !important;
}

/* Badge pills */
.pill-active {
    background-color: rgba(0, 236, 102, 0.15);
    color: #00ec66;
    border: 1px solid rgba(0, 236, 102, 0.3);
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}

.pill-orange {
    background-color: rgba(255, 87, 0, 0.15);
    color: #ff8440;
    border: 1px solid rgba(255, 87, 0, 0.3);
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}

.pill-blue {
    background-color: rgba(41, 150, 255, 0.15);
    color: #4da3ff;
    border: 1px solid rgba(41, 150, 255, 0.3);
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}
</style>
"""

st.markdown(PEWBEAM_CSS, unsafe_allow_html=True)

# Helper functions
def get_user_details(user_obj):
    if user_obj is None:
        return "Unknown", "Unknown", "Standard"
    if isinstance(user_obj, dict):
        uname = user_obj.get("username", "Unknown")
        email = user_obj.get("email", "")
        plan = user_obj.get("plan", {})
        plan_name = plan.get("id") or plan.get("name") if isinstance(plan, dict) else str(plan)
    else:
        uname = getattr(user_obj, "username", "Unknown")
        email = getattr(user_obj, "email", "")
        plan = getattr(user_obj, "plan", None)
        plan_name = getattr(plan, "id", None) or getattr(plan, "name", None) or str(plan) if plan else "Standard"
    return uname, email, plan_name or "Active"

def get_dataset_id(run_obj):
    if run_obj is None:
        return ""
    if isinstance(run_obj, dict):
        return run_obj.get("defaultDatasetId") or run_obj.get("default_dataset_id") or ""
    return getattr(run_obj, "default_dataset_id", None) or getattr(run_obj, "defaultDatasetId", None) or ""

def get_env_token():
    # 1. Streamlit Cloud Secrets (for live hosting)
    try:
        if "APIFY_API_TOKEN" in st.secrets:
            return str(st.secrets["APIFY_API_TOKEN"]).strip()
    except Exception:
        pass
    # 2. Environment variable
    if os.environ.get("APIFY_API_TOKEN"):
        return os.environ.get("APIFY_API_TOKEN").strip()
    # 3. Local .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("APIFY_API_TOKEN="):
                    val = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                    if val and val != "your_apify_token_here":
                        return val
    return ""

def list_lead_files():
    files = glob.glob(os.path.join(os.path.dirname(__file__), "pewbeam_church_leads_*.csv"))
    valid_files = [f for f in files if os.path.exists(f) and os.path.getsize(f) > 30]
    valid_files.sort(key=os.path.getmtime, reverse=True)
    return valid_files

# Sidebar
with st.sidebar:
    st.markdown("### ⚡ Pewbeam Settings")
    
    saved_token = get_env_token()
    api_token = st.text_input(
        "Apify API Token", 
        value=saved_token, 
        type="password",
        help="Find this at console.apify.com/account/integrations"
    )
    
    if api_token:
        if st.button("🔌 Test Connection", use_container_width=True):
            try:
                client = ApifyClient(api_token)
                u = client.user().get()
                username, email, plan = get_user_details(u)
                st.success(f"Connected as: {username}")
                st.caption(f"Plan: {plan} | Email: {email}")
            except Exception as e:
                st.error(f"Connection failed: {e}")
    else:
        st.warning("⚠️ Enter your Apify API Token to run live scrapers.")

    st.markdown("---")
    st.markdown("### 🌍 Supported Regions & Languages")
    st.markdown("""
    * 🇬🇧 **English:** UK, USA, Australia, Global
    * 🇩🇪 **German:** Germany, Austria, Switzerland
    * 🇫🇷 **French:** France, Belgium, Switzerland
    * 🇪🇸 **Spanish:** Spain, Latin America
    * 🇮🇹 **Italian:** Italy, Ticino
    * 🇳🇱 **Dutch:** Netherlands, Belgium
    * 🇵🇹 **Portuguese:** Portugal, Brazil
    """)
    st.markdown("---")
    st.caption("Pewbeam AI Outreach Dashboard v2.0 (Multilingual Europe & Global)")

# Header Section
st.markdown("""
<div class="pewbeam-header">
    <div class="pewbeam-title">
        ⚡ PEWBEAM OUTREACH ENGINE
        <span class="badge">Europe & Global</span>
    </div>
    <div class="pewbeam-subtitle">
        Automated church prospect finder, AV lead scraper, and native-language cold outreach generator for 
        <a href="https://pewbeam.com/" target="_blank" style="color: #ff5700; text-decoration: underline;">Pewbeam.com</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_leads, tab_scraper, tab_templates = st.tabs(["📊 Scraped Church Leads", "🚀 New Scrape Job (Europe & Global)", "✉️ Multilingual Outreach & Preview"])

# TAB 2: SCRAPER
with tab_scraper:
    st.markdown("### 🔍 Launch Church Lead Extraction (Powered by Apify)")
    st.write("Searches Google Maps for churches across Europe, the US, or globally, and crawls websites for AV/media contacts.")

    preset_choice = st.selectbox(
        "Quick Presets (Loads top cities into the search box below)",
        options=[
            "Custom (Type your own below)",
            "🇪🇺 Top European Hubs (London, Berlin, Paris, Madrid, Amsterdam, Rome)",
            "🇩🇪 DACH Region (Berlin, Munich, Frankfurt, Vienna, Zurich)",
            "🇬🇧 UK Hubs (London, Birmingham, Manchester, Glasgow)",
            "🇫🇷 France & French-Speaking (Paris, Lyon, Marseille, Brussels)",
            "🇪🇸 Spain Hubs (Madrid, Barcelona, Valencia, Seville)",
            "🇺🇸 US Metro Hubs (Dallas TX, Atlanta GA, Houston TX, Nashville TN)"
        ]
    )

    preset_map = {
        "🇪🇺 Top European Hubs (London, Berlin, Paris, Madrid, Amsterdam, Rome)": "London UK\nBerlin Germany\nParis France\nMadrid Spain\nAmsterdam Netherlands\nRome Italy",
        "🇩🇪 DACH Region (Berlin, Munich, Frankfurt, Vienna, Zurich)": "Berlin Germany\nMunich Germany\nFrankfurt Germany\nVienna Austria\nZurich Switzerland",
        "🇬🇧 UK Hubs (London, Birmingham, Manchester, Glasgow)": "London UK\nBirmingham UK\nManchester UK\nGlasgow UK",
        "🇫🇷 France & French-Speaking (Paris, Lyon, Marseille, Brussels)": "Paris France\nLyon France\nMarseille France\nBrussels Belgium",
        "🇪🇸 Spain Hubs (Madrid, Barcelona, Valencia, Seville)": "Madrid Spain\nBarcelona Spain\nValencia Spain\nSeville Spain",
        "🇺🇸 US Metro Hubs (Dallas TX, Atlanta GA, Houston TX, Nashville TN)": "Dallas TX\nAtlanta GA\nHouston TX\nNashville TN"
    }

    default_text = preset_map.get(preset_choice, "London UK\nBerlin Germany\nParis France\nMadrid Spain")

    col1, col2 = st.columns([2, 1])
    
    with col1:
        locations_input = st.text_area(
            "Target Search Cities / Regions (one per line)",
            value=default_text,
            height=140,
            help="Enter target metropolitan areas where churches and production teams are located."
        )
    
    with col2:
        max_places = st.slider("Churches per Location", min_value=5, max_value=100, value=15, step=5)
        enrich_emails = st.checkbox("Scrape Website Contact Emails (Recommended)", value=True)
        save_env = st.checkbox("Save Token to local .env", value=True)

    if st.button("🚀 Start Multilingual Lead Extraction Now", use_container_width=True):
        if not api_token:
            st.error("Please provide your Apify API Token in the sidebar before starting!")
        else:
            if save_env and api_token != saved_token:
                with open(os.path.join(os.path.dirname(__file__), ".env"), "w", encoding="utf-8") as f:
                    f.write(f"APIFY_API_TOKEN={api_token}\n")

            locations = [loc.strip() for loc in locations_input.split("\n") if loc.strip()]
            
            progress_bar = st.progress(0, text="Initializing Apify actors...")
            client = ApifyClient(api_token)
            
            try:
                progress_bar.progress(20, text=f"Scraping Google Maps across {len(locations)} locations...")
                search_queries = [f"church in {loc}" for loc in locations]
                map_input = {
                    "searchStringsArray": search_queries,
                    "maxCrawledPlacesPerSearch": max_places,
                    "language": "en",
                    "skipClosedPlaces": True,
                }
                
                run = client.actor("compass/crawler-google-places").call(run_input=map_input)
                dataset = client.dataset(get_dataset_id(run))
                
                churches = []
                for item in dataset.iterate_items():
                    title = item.get("title")
                    if title:
                        churches.append({
                            "Church Name": title,
                            "Website": item.get("website") or "",
                            "Phone": item.get("phone") or "",
                            "Address": item.get("address") or "",
                            "City": item.get("city") or "",
                            "State": item.get("state") or "",
                            "Rating": item.get("totalScore") or "",
                            "Reviews Count": item.get("reviewsCount") or 0,
                            "Google Maps URL": item.get("url") or "",
                            "Emails": []
                        })
                
                progress_bar.progress(60, text=f"Found {len(churches)} churches! Crawling websites for contact emails...")

                # 2. Email Crawl
                if enrich_emails:
                    sites = [c["Website"] for c in churches if c["Website"] and c["Website"].startswith("http")][:60]
                    if sites:
                        contact_input = {
                            "startUrls": [{"url": u} for u in sites],
                            "maxDepth": 1,
                            "maxRequestsPerCrawl": len(sites) * 2,
                        }
                        c_run = client.actor("vdrmota/contact-info-scraper").call(run_input=contact_input)
                        c_dataset = client.dataset(get_dataset_id(c_run))
                        
                        email_map = {}
                        for c_item in c_dataset.iterate_items():
                            u = c_item.get("url", "").rstrip("/")
                            ems = c_item.get("emails", [])
                            if u and ems:
                                email_map[u] = ems

                        for church in churches:
                            web = church["Website"].rstrip("/")
                            for u, ems in email_map.items():
                                if u in web or web in u:
                                    church["Emails"].extend(ems)
                
                progress_bar.progress(90, text="Detecting regions and saving CSV...")
                
                for c in churches:
                    c["Emails"] = "; ".join(sorted(list(set(c["Emails"]))))
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(os.path.dirname(__file__), f"pewbeam_church_leads_{timestamp}.csv")
                
                church_cols = ["Church Name", "Address", "Phone", "Website", "City", "State", "Rating", "Reviews Count", "Google Maps URL", "Emails"]
                df_new = pd.DataFrame(churches, columns=church_cols if not churches else None)
                df_new.to_csv(filename, index=False)
                
                progress_bar.progress(100, text="Complete!")
                st.success(f"🎉 Successfully scraped {len(churches)} churches! Saved to `{os.path.basename(filename)}`")
                st.rerun()

            except Exception as err:
                st.error(f"Error during scrape: {err}")

# TAB 1: LEADS EXPLORER
with tab_leads:
    lead_files = list_lead_files()
    
    if not lead_files:
        st.info("No lead files found yet. Go to the **'🚀 New Scrape Job'** tab to run your first scrape!")
    else:
        selected_file = st.selectbox(
            "Select Lead Dataset", 
            options=lead_files, 
            format_func=lambda x: f"{os.path.basename(x)} ({datetime.fromtimestamp(os.path.getmtime(x)).strftime('%Y-%m-%d %H:%M')})"
        )
        
        try:
            df = pd.read_csv(selected_file)
            if df.empty:
                st.warning(f"The selected dataset '{os.path.basename(selected_file)}' has no records.")
                st.stop()
        except Exception as e:
            st.warning(f"Could not read '{os.path.basename(selected_file)}': {e}")
            st.stop()
        
        # Add Language detection column
        detected_langs = []
        for _, r in df.iterrows():
            l_code = detect_language(
                church_name=str(r.get("Church Name", "")),
                city=str(r.get("City", "")),
                state=str(r.get("State", "")),
                website=str(r.get("Website", ""))
            )
            detected_langs.append(f"{TEMPLATES[l_code]['flag']} {TEMPLATES[l_code]['name'].split(' ')[0]}")
        df["Language / Region"] = detected_langs

        # Metric indicators
        total_churches = len(df)
        with_website = int((df["Website"].fillna("").str.len() > 3).sum()) if "Website" in df.columns else 0
        with_email = int((df["Emails"].fillna("").str.len() > 3).sum()) if "Emails" in df.columns else 0
        avg_rating = round(df["Rating"].dropna().mean(), 2) if "Rating" in df.columns and not df["Rating"].empty else "N/A"

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""<div class="metric-box"><div class="metric-num">{total_churches}</div><div class="metric-label">Total Churches</div></div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-box"><div class="metric-num">{with_website}</div><div class="metric-label">Active Websites</div></div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class="metric-box"><div class="metric-num">{with_email}</div><div class="metric-label">Contacts Found</div></div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""<div class="metric-box"><div class="metric-num">{avg_rating} ⭐</div><div class="metric-label">Avg Google Rating</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Filters
        fcol1, fcol2, fcol3 = st.columns([2, 1, 1])
        with fcol1:
            search_query = st.text_input("Filter by Church Name, City, or Language", "")
        with fcol2:
            only_with_emails = st.checkbox("Only show with emails", value=False)
        with fcol3:
            only_with_sites = st.checkbox("Only show with websites", value=True)

        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df["Church Name"].astype(str).str.contains(search_query, case=False, na=False) |
                filtered_df["City"].astype(str).str.contains(search_query, case=False, na=False) |
                filtered_df["Language / Region"].astype(str).str.contains(search_query, case=False, na=False)
            ]
        if only_with_emails and "Emails" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Emails"].fillna("").str.len() > 3]
        if only_with_sites and "Website" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Website"].fillna("").str.len() > 3]

        # Reorder columns to put Language / Region near the front
        cols = filtered_df.columns.tolist()
        if "Language / Region" in cols:
            cols.remove("Language / Region")
            cols.insert(2, "Language / Region")
            filtered_df = filtered_df[cols]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "Website": st.column_config.LinkColumn("Website"),
                "Google Maps URL": st.column_config.LinkColumn("Maps"),
                "Rating": st.column_config.NumberColumn(format="%.1f ⭐")
            },
            height=400
        )

        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Leads (CSV)",
            data=csv_data,
            file_name=f"pewbeam_filtered_leads_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# TAB 3: OUTREACH GENERATOR
with tab_templates:
    st.markdown("### ✉️ Multilingual Personalized Outreach (Native European Languages)")
    st.write("Generates culturally tailored, native cold emails and LinkedIn messages in **German, French, Spanish, Italian, Dutch, Portuguese, or English**.")

    lead_files = list_lead_files()
    if not lead_files:
        st.warning("Please scrape leads first before generating personalized messages.")
    else:
        df_out = pd.read_csv(lead_files[0])
        church_list = df_out["Church Name"].tolist()
        
        sel_col1, sel_col2 = st.columns([2, 1])
        with sel_col1:
            selected_church_name = st.selectbox("Select Church to Preview Personalized Pitch", options=church_list)
        
        selected_row = df_out[df_out["Church Name"] == selected_church_name].iloc[0]

        church_name = str(selected_row.get("Church Name", "Church")).strip()
        city = str(selected_row.get("City", "your area")).strip() or "your area"
        state = str(selected_row.get("State", "")).strip()
        website = str(selected_row.get("Website", "")).strip()
        emails = str(selected_row.get("Emails", "")).strip()

        # Automatic language detection
        detected_code = detect_language(church_name=church_name, city=city, state=state, website=website)

        with sel_col2:
            lang_options = list(TEMPLATES.keys())
            lang_labels = {k: f"{TEMPLATES[k]['flag']} {TEMPLATES[k]['name']}" for k in lang_options}
            chosen_lang = st.selectbox(
                "Target Language / Translation",
                options=lang_options,
                index=lang_options.index(detected_code),
                format_func=lambda x: lang_labels[x]
            )

        # Get localized content
        content = get_outreach_content(chosen_lang, church_name=church_name, city=city)

        st.markdown(f"<span class='pill-blue'>Active Language: {content['flag']} {content['lang_name']}</span>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        c_left, c_right = st.columns(2)

        with c_left:
            st.markdown(f"#### 📧 Cold Email ({content['lang_name']})")
            st.text_input("Subject Line", value=content["subject"])
            st.text_area("Email Body", value=content["email_body"], height=300)
            
            if emails:
                st.markdown(f"<span class='pill-active'>Available Recipient: {emails}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='pill-orange'>No direct email found — use Contact Form / Phone</span>", unsafe_allow_html=True)

        with c_right:
            st.markdown(f"#### 💬 LinkedIn DM ({content['lang_name']})")
            st.text_area("LinkedIn Message", value=content["linkedin_dm"], height=190)
            
            st.markdown(f"#### 📱 Follow-up Bump (Day 3)")
            st.text_area("Quick Follow-Up Bump", value=content["bump"], height=95)

        st.markdown("---")
        st.markdown("#### 📦 Export Multilingual Mail-Merge CSV (All Churches in their Native Language)")
        st.caption("Each church will automatically receive an email subject and body in their country's language (German for German churches, French for French churches, Spanish for Spanish churches, etc.)")

        if st.button("🚀 Generate Full Multilingual Campaign Dataset", use_container_width=True):
            full_outreach = []
            for _, row in df_out.iterrows():
                c_name = str(row.get("Church Name", "Church")).strip()
                c_city = str(row.get("City", "your area")).strip() or "your area"
                c_state = str(row.get("State", "")).strip()
                c_web = str(row.get("Website", "")).strip()
                c_email = str(row.get("Emails", "")).strip()
                c_phone = str(row.get("Phone", "")).strip()

                # Detect each church's language
                row_lang = detect_language(church_name=c_name, city=c_city, state=c_state, website=c_web)
                row_content = get_outreach_content(row_lang, church_name=c_name, city=c_city)

                full_outreach.append({
                    "Church Name": c_name,
                    "City": c_city,
                    "Country / Language": f"{row_content['flag']} {row_content['lang_name']}",
                    "Language Code": row_lang,
                    "Emails": c_email,
                    "Phone": c_phone,
                    "Website": c_web,
                    "Email Subject": row_content["subject"],
                    "Email Body": row_content["email_body"],
                    "LinkedIn DM": row_content["linkedin_dm"],
                    "Follow-Up Bump": row_content["bump"]
                })
            
            df_full = pd.DataFrame(full_outreach)
            csv_export = df_full.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Ready-To-Import Multilingual Campaign CSV (Instantly / Smartlead)",
                data=csv_export,
                file_name=f"pewbeam_multilingual_outreach_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
