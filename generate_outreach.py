"""
Pewbeam Multilingual Outreach Generator (CLI)
==============================================
Takes a scraped church CSV file and generates native-language cold email sequences
and LinkedIn DMs (English, German, French, Spanish, Italian, Dutch, Portuguese).

Usage:
    python generate_outreach.py --csv <path_to_leads.csv>
"""

import os
import sys
import csv
import glob
import argparse

sys.path.append(os.path.dirname(__file__))
from outreach_templates import TEMPLATES, detect_language, get_outreach_content

def find_latest_leads_csv():
    files = glob.glob("pewbeam_church_leads_*.csv")
    if not files:
        files = glob.glob("*.csv")
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

def main():
    parser = argparse.ArgumentParser(description="Generate multilingual personalized outreach copy for European & Global churches.")
    parser.add_argument("--csv", type=str, default=None, help="Path to input leads CSV")
    parser.add_argument("--language", type=str, default="auto", help="Language code (en, de, fr, es, it, nl, pt) or 'auto'")
    parser.add_argument("--output", type=str, default="pewbeam_multilingual_outreach.csv", help="Path to output CSV")
    args = parser.parse_args()

    csv_path = args.csv or find_latest_leads_csv()
    if not csv_path or not os.path.exists(csv_path):
        print(f"[!] Error: No leads CSV file found. Run 'scrape_churches.py' first or specify --csv <file>")
        sys.exit(1)

    print(f"[*] Reading leads from: {csv_path}")

    leads_out = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            church_name = row.get("Church Name", "Church").strip()
            city = row.get("City", "your area").strip() or "your area"
            state = row.get("State", "").strip()
            website = row.get("Website", "").strip()
            emails = row.get("Emails", "").strip()
            phone = row.get("Phone", "").strip()

            if args.language == "auto":
                lang = detect_language(church_name=church_name, city=city, state=state, website=website)
            else:
                lang = args.language

            content = get_outreach_content(lang, church_name=church_name, city=city)

            leads_out.append({
                "Church Name": church_name,
                "City": city,
                "Country / Language": f"{content['flag']} {content['lang_name']}",
                "Emails": emails,
                "Phone": phone,
                "Website": website,
                "Email Subject": content["subject"],
                "Email Body": content["email_body"],
                "LinkedIn DM": content["linkedin_dm"],
                "Follow-Up Bump": content["bump"]
            })

    fieldnames = [
        "Church Name",
        "City",
        "Country / Language",
        "Emails",
        "Phone",
        "Website",
        "Email Subject",
        "Email Body",
        "LinkedIn DM",
        "Follow-Up Bump"
    ]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads_out)

    print(f"[+] Generated native-language messages for {len(leads_out)} leads.")
    print(f"[+] Saved to: {args.output}")

if __name__ == "__main__":
    main()
