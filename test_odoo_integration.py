"""
Test Odoo MCP Server Integration

Tests the Odoo MCP server by:
1. Connecting to Odoo
2. Creating a test invoice
3. Recording a test expense
4. Getting financial summary
5. Listing recent transactions
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.mcp_servers.odoo_server import (
    create_customer_invoice,
    record_expense,
    get_financial_summary,
    list_recent_invoices,
    list_recent_bills
)


def test_odoo_integration():
    """Test Odoo integration."""
    print("=" * 60)
    print("TESTING ODOO MCP SERVER INTEGRATION")
    print("=" * 60)

    try:
        # Test 1: Create a customer invoice
        print("\n1. Creating test customer invoice...")
        invoice = create_customer_invoice(
            customer_name="Test Customer Inc",
            invoice_lines=[
                {
                    'product_name': 'Consulting Services',
                    'quantity': 5,
                    'unit_price': 200.00,
                    'description': 'Strategic consulting - 5 hours'
                }
            ]
        )
        print(f"[OK] Invoice created: {invoice['invoice_number']}")
        print(f"  Customer: {invoice['customer']}")
        print(f"  Total: ${invoice['total']:.2f}")
        print(f"  Status: {invoice['status']}")

        # Test 2: Record an expense
        print("\n2. Recording test expense...")
        expense = record_expense(
            vendor_name="Office Depot",
            expense_lines=[
                {
                    'product_name': 'Office Supplies',
                    'quantity': 1,
                    'unit_price': 125.50,
                    'description': 'Monthly office supplies'
                }
            ]
        )
        print(f"[OK] Expense recorded: {expense['bill_number']}")
        print(f"  Vendor: {expense['vendor']}")
        print(f"  Total: ${expense['total']:.2f}")
        print(f"  Status: {expense['status']}")

        # Test 3: Get financial summary
        print("\n3. Getting financial summary...")
        summary = get_financial_summary()
        print(f"[OK] Financial summary:")
        print(f"  Period: {summary['date_from']} to {summary['date_to']}")
        print(f"  Revenue: ${summary['revenue']:.2f}")
        print(f"  Expenses: ${summary['expenses']:.2f}")
        print(f"  Profit: ${summary['profit']:.2f}")
        print(f"  Profit Margin: {summary['profit_margin']:.1f}%")
        print(f"  Invoices: {summary['invoice_count']}")
        print(f"  Bills: {summary['bill_count']}")

        # Test 4: List recent invoices
        print("\n4. Listing recent invoices...")
        invoices = list_recent_invoices(limit=5)
        print(f"[OK] Found {len(invoices)} recent invoices:")
        for inv in invoices[:3]:  # Show first 3
            print(f"  - {inv['invoice_number']}: {inv['customer']} - ${inv['total']:.2f} ({inv['status']})")

        # Test 5: List recent bills
        print("\n5. Listing recent bills...")
        bills = list_recent_bills(limit=5)
        print(f"[OK] Found {len(bills)} recent bills:")
        for bill in bills[:3]:  # Show first 3
            print(f"  - {bill['bill_number']}: {bill['vendor']} - ${bill['total']:.2f} ({bill['status']})")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nOdoo MCP Server is ready for integration!")

        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_odoo_integration()
    sys.exit(0 if success else 1)
