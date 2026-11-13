"""
Quick script to verify that your Apify API Token is valid and check available credits.
Usage:
    python verify_apify.py
    or:
    python verify_apify.py apify_api_XXXXXXXXXXXX
"""

import sys
import os
from apify_client import ApifyClient

def load_token():
    # 1. From CLI argument
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        return sys.argv[1].strip()
    
    # 2. From environment variable
    if os.environ.get("APIFY_API_TOKEN"):
        return os.environ.get("APIFY_API_TOKEN").strip()

    # 3. From local .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("APIFY_API_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    
    return None

def main():
    token = load_token()
    if not token or token == "your_apify_token_here":
        print("[!] No Apify API token found.")
        print("Please provide it via:")
        print("  1. python verify_apify.py <YOUR_TOKEN>")
        print("  2. Adding APIFY_API_TOKEN=... to a .env file")
        print("  3. Setting $env:APIFY_API_TOKEN='...' in PowerShell")
        sys.exit(1)

    print("[*] Connecting to Apify API...")
    try:
        client = ApifyClient(token)
        user_info = client.user().get()
        
        username = getattr(user_info, "username", "Unknown") if not isinstance(user_info, dict) else user_info.get("username", "Unknown")
        email = getattr(user_info, "email", "Unknown") if not isinstance(user_info, dict) else user_info.get("email", "Unknown")
        plan_obj = getattr(user_info, "plan", None) if not isinstance(user_info, dict) else user_info.get("plan")
        plan = getattr(plan_obj, "id", None) or getattr(plan_obj, "name", None) or str(plan_obj) if plan_obj else "Free/Standard"
        
        print("\n[+] Success! Apify connection established.")
        print(f"    - Username: {username}")
        print(f"    - Email:    {email}")
        print(f"    - Plan:     {plan}")
        print("\nYou are ready to run lead generation for Pewbeam!")
    except Exception as e:
        print(f"\n[-] Authentication failed: {e}")
        print("Please double check that your API token is active and copied correctly from https://console.apify.com/account/integrations")
        sys.exit(1)

if __name__ == "__main__":
    main()
