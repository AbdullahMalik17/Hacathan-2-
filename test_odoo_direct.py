"""
Direct Test of Odoo Connection

Tests Odoo XML-RPC connection and basic operations.
"""

import xmlrpc.client
import os
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

# Load environment
PROJECT_ROOT = Path(__file__).parent
load_dotenv(PROJECT_ROOT / ".env")

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "digital_fte")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

print("=" * 60)
print("TESTING ODOO DIRECT CONNECTION")
print("=" * 60)

print(f"\nConfiguration:")
print(f"  URL: {ODOO_URL}")
print(f"  Database: {ODOO_DB}")
print(f"  Username: {ODOO_USERNAME}")
print(f"  Password: {'*' * len(ODOO_PASSWORD) if ODOO_PASSWORD else 'NOT SET'}")

try:
    # Step 1: Connect to Odoo
    print("\n1. Connecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')

    # Authenticate
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

    if not uid:
        print("[ERROR] Authentication failed!")
        exit(1)

    print(f"[OK] Connected successfully! User ID: {uid}")

    # Step 2: Get models endpoint
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # Step 3: Query customers
    print("\n2. Querying existing customers...")
    partner_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search',
        [[('is_company', '=', True)]], {'limit': 5}
    )

    partners = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'read',
        [partner_ids], {'fields': ['name', 'email']}
    )

    print(f"[OK] Found {len(partners)} customers:")
    for partner in partners:
        print(f"  - {partner['name']}: {partner.get('email', 'No email')}")

    # Step 4: Query invoices
    print("\n3. Querying existing invoices...")
    invoice_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'account.move', 'search',
        [[('move_type', '=', 'out_invoice')]], {'limit': 5}
    )

    invoices = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'account.move', 'read',
        [invoice_ids], {'fields': ['name', 'partner_id', 'amount_total', 'state']}
    )

    print(f"[OK] Found {len(invoices)} invoices:")
    for inv in invoices:
        customer_name = inv['partner_id'][1] if inv['partner_id'] else 'Unknown'
        print(f"  - {inv['name']}: {customer_name} - ${inv['amount_total']:.2f} ({inv['state']})")

    # Step 5: Create test invoice
    print("\n4. Creating test invoice...")

    # Find or create test customer
    test_customer = "Digital FTE Test Customer"
    customer_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search',
        [[('name', '=', test_customer)]], {'limit': 1}
    )

    if customer_ids:
        customer_id = customer_ids[0]
        print(f"[OK] Found existing customer: {test_customer} (ID: {customer_id})")
    else:
        customer_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'create',
            [{'name': test_customer, 'is_company': True}]
        )
        print(f"[OK] Created new customer: {test_customer} (ID: {customer_id})")

    # Find or create test product
    test_product = "Test Consulting Service"
    product_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'product.product', 'search',
        [[('name', '=', test_product)]], {'limit': 1}
    )

    if product_ids:
        product_id = product_ids[0]
        print(f"[OK] Found existing product: {test_product} (ID: {product_id})")
    else:
        product_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'create',
            [{'name': test_product, 'list_price': 150.0, 'type': 'service'}]
        )
        print(f"[OK] Created new product: {test_product} (ID: {product_id})")

    # Create invoice
    invoice_data = {
        'partner_id': customer_id,
        'move_type': 'out_invoice',
        'invoice_date': date.today().isoformat(),
        'invoice_line_ids': [(0, 0, {
            'product_id': product_id,
            'name': 'Test consulting - 10 hours',
            'quantity': 10,
            'price_unit': 150.0
        })]
    }

    invoice_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'account.move', 'create',
        [invoice_data]
    )

    # Read created invoice
    created_invoice = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'account.move', 'read',
        [[invoice_id]], {'fields': ['name', 'amount_total', 'state']}
    )[0]

    print(f"[OK] Invoice created successfully!")
    print(f"  Invoice Number: {created_invoice['name']}")
    print(f"  Total: ${created_invoice['amount_total']:.2f}")
    print(f"  Status: {created_invoice['state']}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\nOdoo integration is working correctly!")
    print("The Odoo MCP Server is ready to use.")

except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
