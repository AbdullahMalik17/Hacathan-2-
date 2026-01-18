"""
Simple Odoo Test - Just verify connection and basic operations
"""

import xmlrpc.client
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
PROJECT_ROOT = Path(__file__).parent
load_dotenv(PROJECT_ROOT / ".env")

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "digital_fte")
ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

print("=" * 60)
print("ODOO MCP SERVER - SIMPLE TEST")
print("=" * 60)

try:
    # Connect
    print("\n1. Connecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

    if not uid:
        print("[ERROR] Authentication failed")
        exit(1)

    print(f"[OK] Connected! User ID: {uid}")

    # Get models
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # Test: List installed modules
    print("\n2. Checking installed modules...")
    module_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.module.module', 'search',
        [[('state', '=', 'installed'), ('name', 'like', 'account')]], {'limit': 10}
    )

    modules = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.module.module', 'read',
        [module_ids], {'fields': ['name', 'shortdesc']}
    )

    print(f"[OK] Found {len(modules)} accounting-related modules:")
    for mod in modules:
        print(f"  - {mod['shortdesc']}")

    # Test: Query partners
    print("\n3. Querying partners...")
    partner_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search',
        [[]], {'limit': 5}
    )

    partners = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'read',
        [partner_ids], {'fields': ['name']}
    )

    print(f"[OK] Found {len(partners)} partners:")
    for partner in partners:
        print(f"  - {partner['name']}")

    # Test: Query products
    print("\n4. Querying products...")
    product_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'product.product', 'search',
        [[]], {'limit': 5}
    )

    products = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'product.product', 'read',
        [product_ids], {'fields': ['name', 'list_price']}
    )

    print(f"[OK] Found {len(products)} products:")
    for product in products:
        print(f"  - {product['name']}: ${product.get('list_price', 0):.2f}")

    print("\n" + "=" * 60)
    print("SUCCESS! ODOO CONNECTION WORKING")
    print("=" * 60)
    print("\nOdoo MCP Server is ready to integrate!")
    print("\nNote: To use invoice/expense features, ensure the")
    print("      Accounting module is installed in Odoo.")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    exit(1)
