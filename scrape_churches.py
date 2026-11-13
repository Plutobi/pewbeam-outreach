"""
Pewbeam Church Outreach Lead Scraper using Apify
=================================================
Automates finding churches and their AV/Media contacts:
1. Searches Google Maps for target regions/cities.
2. Extracts church names, websites, phone numbers, addresses, and ratings.
3. Automatically scrapes contact emails from the church websites.
4. Outputs clean CSV file ready for cold email outreach (Instantly / Smartlead / CSV import).

Usage:
    python scrape_churches.py --locations "Dallas TX" "Atlanta GA" --max-per-location 20
    python scrape_churches.py --help
"""

import os
import sys
import argparse
import csv
from datetime import datetime
from apify_client import ApifyClient

def get_dataset_id(run_obj):
    if run_obj is None:
        return ""
    if isinstance(run_obj, dict):
        return run_obj.get("defaultDatasetId") or run_obj.get("default_dataset_id") or ""
    return getattr(run_obj, "default_dataset_id", None) or getattr(run_obj, "defaultDatasetId", None) or ""

def load_token():
    if os.environ.get("APIFY_API_TOKEN"):
        return os.environ.get("APIFY_API_TOKEN").strip()

    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("APIFY_API_TOKEN="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val and val != "your_apify_token_here":
                        return val
    return None

def scrape_google_maps(client: ApifyClient, locations: list[str], max_per_location: int = 25):
    print(f"\n[*] [Step 1/2] Scraping churches across {len(locations)} locations...")
    search_queries = [f"church in {loc}" for loc in locations]
    
    run_input = {
        "searchStringsArray": search_queries,
        "maxCrawledPlacesPerSearch": max_per_location,
        "language": "en",
        "skipClosedPlaces": True,
    }
    
    print(f"    - Target queries: {search_queries}")
    print(f"    - Max places per query: {max_per_location}")
    print("    - Launching Google Maps Scraper Actor ('compass/crawler-google-places')...")
    
    run = client.actor("compass/crawler-google-places").call(run_input=run_input)
    dataset = client.dataset(get_dataset_id(run))
    
    churches = []
    for item in dataset.iterate_items():
        title = item.get("title")
        website = item.get("website")
        if not title:
            continue
            
        churches.append({
            "name": title,
            "website": website or "",
            "phone": item.get("phone") or "",
            "address": item.get("address") or "",
            "city": item.get("city") or "",
            "state": item.get("state") or "",
            "rating": item.get("totalScore") or "",
            "reviews_count": item.get("reviewsCount") or 0,
            "google_maps_url": item.get("url") or "",
            "emails": set(),
        })

    print(f"[+] Found {len(churches)} churches. {sum(1 for c in churches if c['website'])} have websites.")
    return churches

def enrich_emails(client: ApifyClient, churches: list[dict], max_sites_to_crawl: int = 50):
    websites_to_crawl = [c["website"] for c in churches if c.get("website") and c["website"].startswith("http")][:max_sites_to_crawl]
    
    if not websites_to_crawl:
        print("[!] No website URLs found to scrape contact info.")
        return churches
        
    print(f"\n[*] [Step 2/2] Crawling {len(websites_to_crawl)} church websites for emails and staff contacts...")
    print("    - Launching Contact Info Scraper Actor ('vdrmota/contact-info-scraper')...")

    contact_input = {
        "startUrls": [{"url": url} for url in websites_to_crawl],
        "maxDepth": 1,
        "maxRequestsPerCrawl": len(websites_to_crawl) * 3,
    }

    try:
        contact_run = client.actor("vdrmota/contact-info-scraper").call(run_input=contact_input)
        contact_dataset = client.dataset(get_dataset_id(contact_run))
        
        # Map scraped emails back to corresponding church website
        scraped_by_url = {}
        for item in contact_dataset.iterate_items():
            base_url = item.get("url", "").rstrip("/")
            emails = item.get("emails", [])
            if base_url and emails:
                scraped_by_url[base_url] = emails

        for church in churches:
            web = church["website"].rstrip("/")
            for scraped_url, emails in scraped_by_url.items():
                if scraped_url in web or web in scraped_url:
                    church["emails"].update(emails)
                    
        print(f"[+] Enrichment complete!")
    except Exception as e:
        print(f"[!] Warning: Email crawler encountered an issue: {e}")
        print("    Proceeding with existing church data...")

    return churches

def save_leads_to_csv(churches: list[dict], output_file: str):
    fieldnames = [
        "Church Name",
        "Emails",
        "Website",
        "Phone",
        "City",
        "State",
        "Rating",
        "Reviews Count",
        "Google Maps URL"
    ]
    
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for c in churches:
            writer.writerow({
                "Church Name": c["name"],
                "Emails": "; ".join(sorted(list(c["emails"]))) if c["emails"] else "",
                "Website": c["website"],
                "Phone": c["phone"],
                "City": c["city"],
                "State": c["state"],
                "Rating": c["rating"],
                "Reviews Count": c["reviews_count"],
                "Google Maps URL": c["google_maps_url"]
            })
            
    print(f"\n[+] Results successfully saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Scrape target churches for Pewbeam outreach.")
    parser.add_argument(
        "--locations", 
        nargs="+", 
        default=["Dallas TX", "Atlanta GA"], 
        help="List of cities/states to search (e.g. 'Dallas TX' 'Atlanta GA')"
    )
    parser.add_argument(
        "--max-per-location", 
        type=int, 
        default=20, 
        help="Maximum churches to fetch per location (default: 20)"
    )
    parser.add_argument(
        "--skip-enrichment", 
        action="store_true", 
        help="Skip website email scraping to save credits/time"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default=None, 
        help="Path to output CSV file"
    )

    args = parser.parse_args()

    token = load_token()
    if not token:
        print("[!] Error: No Apify API token found.")
        print("Please save your token in .env or run: $env:APIFY_API_TOKEN='your_token'")
        sys.exit(1)

    client = ApifyClient(token)

    # 1. Scrape Google Maps
    churches = scrape_google_maps(client, args.locations, max_per_location=args.max_per_location)

    # 2. Enrich with emails if not skipped
    if not args.skip_enrichment:
        churches = enrich_emails(client, churches)

    # 3. Export to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = args.output or f"pewbeam_church_leads_{timestamp}.csv"
    save_leads_to_csv(churches, out_file)

if __name__ == "__main__":
    main()
