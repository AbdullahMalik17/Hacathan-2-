#!/usr/bin/env python3
"""
API Diagnostics and Fixes

Diagnoses API configuration issues and provides step-by-step fixes.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / "config" / ".env")

# Colors
class C:
    G = '\033[92m'  # Green
    R = '\033[91m'  # Red
    Y = '\033[93m'  # Yellow
    B = '\033[94m'  # Blue
    E = '\033[0m'   # End

def main():
    print(f"\n{C.B}{'='*60}")
    print(f"  API DIAGNOSTICS & CONFIGURATION HELPER")
    print(f"{'='*60}{C.E}\n")

    # Check Facebook/Meta
    print(f"{C.B}[1] FACEBOOK & INSTAGRAM DIAGNOSTICS{C.E}\n")

    access_token = os.getenv("META_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    ig_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

    if not access_token:
        print(f"{C.R}[ERROR]{C.E} META_ACCESS_TOKEN not configured\n")
        print(f"{C.Y}FIX:{C.E}")
        print("1. Go to https://developers.facebook.com/tools/explorer/")
        print("2. Select your app")
        print("3. Add permissions: pages_manage_posts, pages_read_engagement")
        print("4. Generate Access Token")
        print("5. Update META_ACCESS_TOKEN in config/.env\n")
    else:
        print(f"{C.G}[OK]{C.E} Access token configured")

        # Get user pages
        try:
            url = "https://graph.facebook.com/v18.0/me/accounts"
            params = {"access_token": access_token}
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                pages = data.get('data', [])

                if pages:
                    print(f"{C.G}[OK]{C.E} Found {len(pages)} page(s):\n")
                    for page in pages:
                        print(f"   Page Name: {page.get('name')}")
                        print(f"   Page ID: {page.get('id')}")
                        print(f"   Category: {page.get('category', 'N/A')}")

                        # Get Instagram account if linked
                        page_token = page.get('access_token')
                        if page_token:
                            ig_url = f"https://graph.facebook.com/v18.0/{page['id']}"
                            ig_params = {
                                "access_token": page_token,
                                "fields": "instagram_business_account"
                            }
                            ig_response = requests.get(ig_url, params=ig_params)

                            if ig_response.status_code == 200:
                                ig_data = ig_response.json()
                                ig_account = ig_data.get('instagram_business_account')
                                if ig_account:
                                    print(f"   Instagram ID: {ig_account.get('id')}")
                                else:
                                    print(f"   Instagram: Not linked")
                        print()

                    # Check if configured IDs match
                    if page_id:
                        page_ids = [p['id'] for p in pages]
                        if page_id in page_ids:
                            print(f"{C.G}[OK]{C.E} Configured FACEBOOK_PAGE_ID is valid\n")
                        else:
                            print(f"{C.Y}[WARN]{C.E} Configured FACEBOOK_PAGE_ID ({page_id}) not found in your pages\n")
                            print(f"{C.Y}FIX:{C.E} Update FACEBOOK_PAGE_ID in config/.env to one of:")
                            for p in pages:
                                print(f"   {p['id']} ({p['name']})")
                            print()
                    else:
                        print(f"{C.Y}[WARN]{C.E} FACEBOOK_PAGE_ID not configured\n")
                        print(f"{C.Y}FIX:{C.E} Add one of these to config/.env:")
                        for p in pages:
                            print(f"   FACEBOOK_PAGE_ID={p['id']}  # {p['name']}")
                        print()

                    # Check Instagram configuration
                    if ig_id:
                        # Verify the Instagram ID
                        print(f"{C.B}[INFO]{C.E} Verifying Instagram ID: {ig_id}")
                        ig_verify_url = f"https://graph.facebook.com/v18.0/{ig_id}"
                        ig_verify_params = {
                            "access_token": access_token,
                            "fields": "username,name"
                        }
                        ig_verify_response = requests.get(ig_verify_url, params=ig_verify_params)

                        if ig_verify_response.status_code == 200:
                            ig_verify_data = ig_verify_response.json()
                            print(f"{C.G}[OK]{C.E} Instagram @{ig_verify_data.get('username')} is valid\n")
                        else:
                            print(f"{C.R}[ERROR]{C.E} Instagram ID is invalid or inaccessible")
                            print(f"{C.R}Error:{C.E} {ig_verify_response.text}\n")
                            print(f"{C.Y}FIX:{C.E} Use Instagram IDs from above or check Page → Instagram settings\n")
                else:
                    print(f"{C.R}[ERROR]{C.E} No pages found for this access token\n")
                    print(f"{C.Y}FIX:{C.E}")
                    print("1. Make sure you have a Facebook Page")
                    print("2. Regenerate access token with correct permissions")
                    print("3. Token must have pages_manage_posts permission\n")
            else:
                print(f"{C.R}[ERROR]{C.E} Cannot access pages")
                print(f"{C.R}Response:{C.E} {response.text}\n")

        except Exception as e:
            print(f"{C.R}[ERROR]{C.E} {str(e)}\n")

    # Check Twitter
    print(f"\n{C.B}[2] TWITTER DIAGNOSTICS{C.E}\n")

    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    if not bearer_token:
        print(f"{C.R}[ERROR]{C.E} TWITTER_BEARER_TOKEN not configured\n")
        print(f"{C.Y}FIX:{C.E}")
        print("1. Go to https://developer.twitter.com/en/portal/dashboard")
        print("2. Select your app → Keys and Tokens")
        print("3. Generate Bearer Token")
        print("4. Update TWITTER_BEARER_TOKEN in config/.env\n")
    else:
        print(f"{C.G}[OK]{C.E} Bearer token configured")

        try:
            # Try a simple request to test the token
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {"Authorization": f"Bearer {bearer_token}"}
            params = {"query": "twitter", "max_results": 10}
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                print(f"{C.G}[OK]{C.E} Bearer token is valid\n")
            elif "credits" in response.text.lower():
                print(f"{C.Y}[WARN]{C.E} API credits depleted (monthly limit reached)")
                print(f"{C.B}[INFO]{C.E} This is normal for free tier Twitter accounts")
                print(f"{C.B}[INFO]{C.E} Credits reset monthly")
                print(f"{C.B}[INFO]{C.E} You can still post tweets (posting uses different quota)\n")
            else:
                print(f"{C.R}[ERROR]{C.E} Bearer token may be invalid")
                print(f"{C.R}Response:{C.E} {response.text}\n")

        except Exception as e:
            print(f"{C.R}[ERROR]{C.E} {str(e)}\n")

    # Summary and next steps
    print(f"\n{C.B}{'='*60}")
    print(f"  NEXT STEPS")
    print(f"{'='*60}{C.E}\n")

    print(f"{C.G}1.{C.E} Fix any [ERROR] or [WARN] items above")
    print(f"{C.G}2.{C.E} Update config/.env with correct IDs")
    print(f"{C.G}3.{C.E} Run: python tests/test_social_media_apis.py")
    print(f"{C.G}4.{C.E} Test posting with approval workflow\n")


if __name__ == "__main__":
    main()
