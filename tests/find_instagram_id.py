#!/usr/bin/env python3
"""
Find Instagram Business Account ID linked to Facebook Page
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / "config" / ".env")

def main():
    access_token = os.getenv("META_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    api_version = os.getenv("GRAPH_API_VERSION", "v18.0")

    print("\nSearching for Instagram Business Account...\n")
    print(f"Facebook Page ID: {page_id}")

    # Method 1: Check if Instagram is linked to the page
    url = f"https://graph.facebook.com/{api_version}/{page_id}"
    params = {
        "access_token": access_token,
        "fields": "instagram_business_account"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        ig_account = data.get('instagram_business_account')

        if ig_account:
            ig_id = ig_account.get('id')
            print(f"\n[SUCCESS] Instagram Business Account found!")
            print(f"Instagram ID: {ig_id}")
            print(f"\nAdd this to config/.env:")
            print(f"INSTAGRAM_ACCOUNT_ID={ig_id}")

            # Get more info about the Instagram account
            ig_url = f"https://graph.facebook.com/{api_version}/{ig_id}"
            ig_params = {
                "access_token": access_token,
                "fields": "username,name,profile_picture_url"
            }
            ig_response = requests.get(ig_url, params=ig_params)

            if ig_response.status_code == 200:
                ig_data = ig_response.json()
                print(f"\nInstagram Account Details:")
                print(f"  Username: @{ig_data.get('username')}")
                print(f"  Name: {ig_data.get('name')}")

            return 0
        else:
            print("\n[NOT FOUND] No Instagram Business Account linked to this Facebook Page")
            print("\nTo link Instagram:")
            print("1. Go to your Facebook Page settings")
            print("2. Click on 'Instagram' in the left menu")
            print("3. Connect your Instagram Business account")
            print("4. Make sure it's a Business account, not Personal")
            return 1
    else:
        print(f"\n[ERROR] Failed to check Instagram connection")
        print(f"Response: {response.text}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
