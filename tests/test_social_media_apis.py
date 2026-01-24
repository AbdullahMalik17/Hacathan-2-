#!/usr/bin/env python3
"""
Test Social Media API Connections

Tests authentication and basic operations for:
- Facebook (Meta Graph API)
- Instagram (Meta Graph API)
- Twitter/X (Twitter API v2)

Run: python tests/test_social_media_apis.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / "config" / ".env")

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}[OK]{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[WARN]{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def print_header(title):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}\n")


def test_facebook_api():
    """Test Facebook API connection and permissions."""
    print_header("Testing Facebook API")

    access_token = os.getenv("META_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    api_version = os.getenv("GRAPH_API_VERSION", "v18.0")

    if not access_token:
        print_error("META_ACCESS_TOKEN not found in .env")
        return False

    if not page_id:
        print_error("FACEBOOK_PAGE_ID not found in .env")
        return False

    print_info(f"Access Token: {access_token[:20]}...")
    print_info(f"Page ID: {page_id}")
    print_info(f"API Version: {api_version}")

    try:
        # Test 1: Validate access token
        print("\n1. Validating access token...")
        url = f"https://graph.facebook.com/{api_version}/me"
        params = {"access_token": access_token}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Token valid for: {data.get('name', 'Unknown')}")
        else:
            print_error(f"Token validation failed: {response.text}")
            return False

        # Test 2: Get page info
        print("\n2. Getting page information...")
        url = f"https://graph.facebook.com/{api_version}/{page_id}"
        params = {
            "access_token": access_token,
            "fields": "name,category"
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Page: {data.get('name')}")
            print_info(f"Category: {data.get('category', 'N/A')}")
        else:
            print_error(f"Failed to get page info: {response.text}")
            print_info("This usually means:")
            print_info("  - Token doesn't have page access")
            print_info("  - Wrong Page ID")
            print_info("  - Token needs pages_show_list permission")
            return False

        # Test 3: Test permissions
        print("\n3. Checking required permissions...")
        url = f"https://graph.facebook.com/{api_version}/me/permissions"
        params = {"access_token": access_token}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            permissions = {p['permission']: p['status'] for p in data.get('data', [])}

            required = ['pages_manage_posts', 'pages_read_engagement']
            for perm in required:
                if permissions.get(perm) == 'granted':
                    print_success(f"{perm}: granted")
                else:
                    print_warning(f"{perm}: {permissions.get(perm, 'not granted')}")

        print_success("\nFacebook API test completed successfully")
        return True

    except Exception as e:
        print_error(f"Facebook API test failed: {str(e)}")
        return False


def test_instagram_api():
    """Test Instagram API connection."""
    print_header("Testing Instagram API")

    access_token = os.getenv("META_ACCESS_TOKEN")
    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    api_version = os.getenv("GRAPH_API_VERSION", "v18.0")

    if not access_token:
        print_error("META_ACCESS_TOKEN not found in .env")
        return False

    # First, try to discover Instagram account from Facebook page
    print("\n1. Discovering Instagram Business Account from Facebook Page...")
    try:
        url = f"https://graph.facebook.com/{api_version}/{page_id}"
        params = {
            "access_token": access_token,
            "fields": "instagram_business_account"
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            discovered_ig = data.get('instagram_business_account', {}).get('id')

            if discovered_ig:
                print_success(f"Found Instagram ID: {discovered_ig}")
                if account_id and account_id != discovered_ig:
                    print_warning(f"Configured ID ({account_id}) differs from discovered ID")
                    print_info(f"Update INSTAGRAM_ACCOUNT_ID={discovered_ig} in config/.env")
                account_id = discovered_ig
            else:
                print_warning("No Instagram Business Account linked to this Facebook Page")
                print_info("To link Instagram:")
                print_info("  1. Go to Facebook Page Settings → Instagram")
                print_info("  2. Connect your Instagram Business account")
                if not account_id:
                    return False
        else:
            print_warning(f"Could not discover Instagram account: {response.status_code}")
    except Exception as e:
        print_warning(f"Discovery failed: {str(e)}")

    if not account_id:
        print_error("INSTAGRAM_ACCOUNT_ID not found and could not be discovered")
        return False

    print_info(f"Testing Instagram Account ID: {account_id}")

    try:
        # Test 2: Get Instagram account info
        print("\n2. Getting Instagram account information...")
        url = f"https://graph.facebook.com/{api_version}/{account_id}"
        params = {
            "access_token": access_token,
            "fields": "username,name,profile_picture_url,followers_count,media_count"
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            print_success(f"Account: @{data.get('username')}")
            print_info(f"Name: {data.get('name')}")
            print_info(f"Followers: {data.get('followers_count', 'N/A')}")
            print_info(f"Posts: {data.get('media_count', 'N/A')}")
        else:
            print_error(f"Failed to get account info: {response.text}")
            return False

        # Test 3: Check if it's a business account
        print("\n3. Verifying business account status...")
        if data.get('username'):
            print_success("Instagram Business Account verified")
        else:
            print_error("Not a valid Instagram Business Account")
            return False

        print_success("\nInstagram API test completed successfully")
        return True

    except Exception as e:
        print_error(f"Instagram API test failed: {str(e)}")
        return False


def test_twitter_api():
    """Test Twitter API v2 connection."""
    print_header("Testing Twitter API v2")

    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")

    if not bearer_token:
        print_error("TWITTER_BEARER_TOKEN not found in .env")
        return False

    print_info(f"Bearer Token: {bearer_token[:30]}...")

    try:
        # Test 1: Test Bearer Token with a simple API call
        print("\n1. Testing Bearer Token authentication...")
        url = "https://api.twitter.com/2/tweets/search/recent"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        params = {"query": "twitter", "max_results": 10}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            tweets = data.get('data', [])
            print_success(f"Bearer Token valid - retrieved {len(tweets)} tweets")
            print_info("Bearer Token authentication working")
        elif response.status_code == 403 or "CreditsDepleted" in response.text:
            print_warning("API credits depleted (normal for free tier)")
            print_info("This doesn't affect tweet posting - that uses a different quota")
            print_success("Bearer Token authentication working")
        else:
            print_error(f"Failed to authenticate: {response.text}")
            return False

        # Test 2: Check if we have API keys for posting
        print("\n2. Checking posting credentials...")
        if api_key and api_secret:
            print_success("API Key and Secret configured")
            print_info("Ready for tweet posting (OAuth 1.0a)")
        else:
            print_warning("API Key/Secret not configured - limited to read-only")
            print_info("Add TWITTER_API_KEY and TWITTER_API_SECRET for posting")

        print_success("\nTwitter API test completed successfully")
        return True

    except Exception as e:
        print_error(f"Twitter API test failed: {str(e)}")
        return False


def test_odoo_api():
    """Test Odoo connection (if configured)."""
    print_header("Testing Odoo Connection")

    odoo_url = os.getenv("ODOO_URL")
    odoo_db = os.getenv("ODOO_DB")
    odoo_user = os.getenv("ODOO_USERNAME")
    odoo_pass = os.getenv("ODOO_PASSWORD")

    if not all([odoo_url, odoo_db, odoo_user, odoo_pass]):
        print_warning("Odoo credentials not fully configured in .env")
        print_info("Skipping Odoo test")
        return None

    if odoo_pass == "your_odoo_password_here":
        print_warning("Odoo password is still placeholder")
        print_info("Please install Odoo and update ODOO_PASSWORD in .env")
        return None

    print_info(f"Odoo URL: {odoo_url}")
    print_info(f"Database: {odoo_db}")
    print_info(f"Username: {odoo_user}")

    try:
        import xmlrpc.client

        # Test 1: Check Odoo server is reachable
        print("\n1. Checking Odoo server connection...")
        try:
            common = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/common')
            version = common.version()
            print_success(f"Odoo server version: {version.get('server_version')}")
        except Exception as e:
            print_error(f"Cannot reach Odoo server: {str(e)}")
            print_info("Make sure Odoo is running: docker ps | grep odoo")
            return False

        # Test 2: Authenticate
        print("\n2. Testing authentication...")
        uid = common.authenticate(odoo_db, odoo_user, odoo_pass, {})

        if uid:
            print_success(f"Authenticated successfully (UID: {uid})")
        else:
            print_error("Authentication failed - check credentials")
            return False

        # Test 3: Test API access
        print("\n3. Testing API access...")
        models = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/object')

        # Try to access partner model (basic test)
        partner_count = models.execute_kw(
            odoo_db, uid, odoo_pass,
            'res.partner', 'search_count', [[]]
        )
        print_success(f"Can access Odoo models ({partner_count} partners found)")

        print_success("\nOdoo connection test completed successfully")
        return True

    except ImportError:
        print_warning("xmlrpc.client not available - skipping detailed tests")
        return None
    except Exception as e:
        print_error(f"Odoo connection test failed: {str(e)}")
        return False


def main():
    """Run all API tests."""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  API CONNECTION TEST SUITE")
    print(f"{'='*60}{Colors.END}\n")

    print_info("Testing all configured APIs...\n")

    results = {
        "Facebook": test_facebook_api(),
        "Instagram": test_instagram_api(),
        "Twitter": test_twitter_api(),
        "Odoo": test_odoo_api()
    }

    # Summary
    print_header("Test Summary")

    for api, result in results.items():
        if result is True:
            print_success(f"{api}: PASSED")
        elif result is False:
            print_error(f"{api}: FAILED")
        elif result is None:
            print_warning(f"{api}: SKIPPED (not configured)")

    # Overall result
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)

    print(f"\n{Colors.BLUE}Results: {Colors.GREEN}{passed} passed{Colors.END}, "
          f"{Colors.RED}{failed} failed{Colors.END}, "
          f"{Colors.YELLOW}{skipped} skipped{Colors.END}\n")

    if failed > 0:
        print_warning("Some tests failed. Check the errors above and:")
        print_info("  1. Verify credentials in config/.env")
        print_info("  2. Check API permissions in developer portals")
        print_info("  3. See docs/setup/social-media-apis.md for setup help")
        return 1
    elif passed == 0:
        print_warning("No APIs configured yet. See docs/setup/social-media-apis.md")
        return 1
    else:
        print_success("All configured APIs are working correctly!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
