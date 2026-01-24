"""
Odoo MCP Server - Business Accounting Integration

Provides MCP tools for Odoo ERP integration:
- Create customer invoices
- Record vendor bills (expenses)
- Query financial data
- Get business metrics
- Manage customers and products

Uses Odoo XML-RPC API for all operations.
"""

import os
import sys
import json
import logging
import xmlrpc.client
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from fastmcp import FastMCP

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from utils.audit_logger import log_audit, AuditDomain, AuditStatus
from utils.error_recovery import retry_with_backoff, RetryConfig, get_circuit_breaker
from models.business_metric import FinancialMetric, MetricSource

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Configuration
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "digital_fte")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

VAULT_PATH = PROJECT_ROOT / "Vault"
LOGS_PATH = VAULT_PATH / "Logs"

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OdooMCP")

# Initialize MCP
mcp = FastMCP("Odoo Accounting")

# Odoo API connection cache
_odoo_connection = None


class OdooConnection:
    """Manages Odoo XML-RPC connection."""

    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.models = None
        self.common = None

    def connect(self):
        """Establish connection to Odoo."""
        try:
            # Common endpoint for authentication
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')

            # Authenticate
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})

            if not self.uid:
                raise Exception("Authentication failed")

            # Object endpoint for operations
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

            logger.info(f"Connected to Odoo as user ID: {self.uid}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {e}")
            raise

    def execute(self, model: str, method: str, *args, **kwargs):
        """Execute a model method."""
        if not self.uid or not self.models:
            self.connect()

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )

    def search(self, model: str, domain: List, limit: int = None, offset: int = 0):
        """Search for records."""
        kwargs = {'offset': offset}
        if limit:
            kwargs['limit'] = limit

        return self.execute(model, 'search', domain, kwargs)

    def read(self, model: str, ids: List[int], fields: List[str] = None):
        """Read record data."""
        kwargs = {}
        if fields:
            kwargs['fields'] = fields

        return self.execute(model, 'read', ids, kwargs)

    def create(self, model: str, values: Dict) -> int:
        """Create a new record."""
        return self.execute(model, 'create', values)

    def write(self, model: str, ids: List[int], values: Dict) -> bool:
        """Update records."""
        return self.execute(model, 'write', ids, values)


def get_odoo() -> OdooConnection:
    """Get or create Odoo connection."""
    global _odoo_connection

    if _odoo_connection is None:
        _odoo_connection = OdooConnection(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)
        _odoo_connection.connect()

    return _odoo_connection


@mcp.tool()
@retry_with_backoff(RetryConfig(max_retries=3))
def create_customer_invoice(
    customer_name: str,
    invoice_lines: List[Dict[str, Any]],
    invoice_date: str = None
) -> Dict[str, Any]:
    """
    Create a customer invoice in Odoo.

    Args:
        customer_name: Customer name (will search or create)
        invoice_lines: List of invoice line items, each with:
            - product_name: Product/service name
            - quantity: Quantity
            - unit_price: Price per unit
            - description: Optional description
        invoice_date: Invoice date (YYYY-MM-DD), defaults to today

    Returns:
        Dictionary with invoice_id, invoice_number, total, and status
    """
    try:
        odoo = get_odoo()
        circuit_breaker = get_circuit_breaker("odoo_api")

        # Use circuit breaker
        def _create_invoice():
            # Find or create customer
            partner_ids = odoo.search('res.partner', [('name', '=', customer_name)], limit=1)

            if partner_ids:
                partner_id = partner_ids[0]
            else:
                # Create customer
                partner_id = odoo.create('res.partner', {
                    'name': customer_name,
                    'customer_rank': 1
                })
                logger.info(f"Created new customer: {customer_name} (ID: {partner_id})")

            # Prepare invoice lines
            invoice_line_values = []
            total_amount = 0.0

            for line in invoice_lines:
                product_name = line['product_name']
                quantity = float(line['quantity'])
                unit_price = float(line['unit_price'])
                description = line.get('description', product_name)

                # Find or create product
                product_ids = odoo.search('product.product', [('name', '=', product_name)], limit=1)

                if product_ids:
                    product_id = product_ids[0]
                else:
                    # Create product
                    product_id = odoo.create('product.product', {
                        'name': product_name,
                        'list_price': unit_price,
                        'type': 'service'
                    })
                    logger.info(f"Created new product: {product_name} (ID: {product_id})")

                # Add line
                line_total = quantity * unit_price
                total_amount += line_total

                invoice_line_values.append((0, 0, {
                    'product_id': product_id,
                    'name': description,
                    'quantity': quantity,
                    'price_unit': unit_price
                }))

            # Create invoice
            invoice_values = {
                'partner_id': partner_id,
                'move_type': 'out_invoice',  # Customer invoice
                'invoice_date': invoice_date or date.today().isoformat(),
                'invoice_line_ids': invoice_line_values
            }

            invoice_id = odoo.create('account.move', invoice_values)

            # Read invoice data
            invoice_data = odoo.read('account.move', [invoice_id], [
                'name', 'amount_total', 'state', 'invoice_date'
            ])[0]

            return {
                'invoice_id': invoice_id,
                'invoice_number': invoice_data['name'],
                'customer': customer_name,
                'total': invoice_data['amount_total'],
                'status': invoice_data['state'],
                'date': invoice_data['invoice_date']
            }

        result = circuit_breaker.call(_create_invoice)

        # Audit log
        log_audit(
            action="odoo.create_invoice",
            actor="odoo_mcp",
            domain=AuditDomain.BUSINESS,
            resource=f"invoice_{result['invoice_id']}",
            status=AuditStatus.SUCCESS,
            details={
                'customer': customer_name,
                'total': result['total'],
                'invoice_number': result['invoice_number']
            }
        )

        logger.info(f"Created invoice {result['invoice_number']} for {customer_name}: ${result['total']}")
        return result

    except Exception as e:
        logger.error(f"Failed to create invoice: {e}")
        log_audit(
            action="odoo.create_invoice",
            actor="odoo_mcp",
            domain=AuditDomain.BUSINESS,
            resource="invoice_failed",
            status=AuditStatus.FAILURE,
            error=str(e)
        )
        raise


@mcp.tool()
@retry_with_backoff(RetryConfig(max_retries=3))
def record_expense(
    vendor_name: str,
    expense_lines: List[Dict[str, Any]],
    bill_date: str = None
) -> Dict[str, Any]:
    """
    Record a vendor bill (expense) in Odoo.

    Args:
        vendor_name: Vendor name (will search or create)
        expense_lines: List of expense line items, each with:
            - product_name: Product/service name
            - quantity: Quantity
            - unit_price: Price per unit
            - description: Optional description
        bill_date: Bill date (YYYY-MM-DD), defaults to today

    Returns:
        Dictionary with bill_id, bill_number, total, and status
    """
    try:
        odoo = get_odoo()
        circuit_breaker = get_circuit_breaker("odoo_api")

        def _create_bill():
            # Find or create vendor
            partner_ids = odoo.search('res.partner', [('name', '=', vendor_name)], limit=1)

            if partner_ids:
                partner_id = partner_ids[0]
            else:
                # Create vendor
                partner_id = odoo.create('res.partner', {
                    'name': vendor_name,
                    'supplier_rank': 1
                })
                logger.info(f"Created new vendor: {vendor_name} (ID: {partner_id})")

            # Prepare bill lines
            bill_line_values = []
            total_amount = 0.0

            for line in expense_lines:
                product_name = line['product_name']
                quantity = float(line['quantity'])
                unit_price = float(line['unit_price'])
                description = line.get('description', product_name)

                # Find or create product
                product_ids = odoo.search('product.product', [('name', '=', product_name)], limit=1)

                if product_ids:
                    product_id = product_ids[0]
                else:
                    # Create product
                    product_id = odoo.create('product.product', {
                        'name': product_name,
                        'standard_price': unit_price,
                        'type': 'service'
                    })
                    logger.info(f"Created new product: {product_name} (ID: {product_id})")

                # Add line
                line_total = quantity * unit_price
                total_amount += line_total

                bill_line_values.append((0, 0, {
                    'product_id': product_id,
                    'name': description,
                    'quantity': quantity,
                    'price_unit': unit_price
                }))

            # Create bill
            bill_values = {
                'partner_id': partner_id,
                'move_type': 'in_invoice',  # Vendor bill
                'invoice_date': bill_date or date.today().isoformat(),
                'invoice_line_ids': bill_line_values
            }

            bill_id = odoo.create('account.move', bill_values)

            # Read bill data
            bill_data = odoo.read('account.move', [bill_id], [
                'name', 'amount_total', 'state', 'invoice_date'
            ])[0]

            return {
                'bill_id': bill_id,
                'bill_number': bill_data['name'],
                'vendor': vendor_name,
                'total': bill_data['amount_total'],
                'status': bill_data['state'],
                'date': bill_data['invoice_date']
            }

        result = circuit_breaker.call(_create_bill)

        # Audit log
        log_audit(
            action="odoo.record_expense",
            actor="odoo_mcp",
            domain=AuditDomain.BUSINESS,
            resource=f"bill_{result['bill_id']}",
            status=AuditStatus.SUCCESS,
            details={
                'vendor': vendor_name,
                'total': result['total'],
                'bill_number': result['bill_number']
            }
        )

        logger.info(f"Recorded expense {result['bill_number']} from {vendor_name}: ${result['total']}")
        return result

    except Exception as e:
        logger.error(f"Failed to record expense: {e}")
        log_audit(
            action="odoo.record_expense",
            actor="odoo_mcp",
            domain=AuditDomain.BUSINESS,
            resource="expense_failed",
            status=AuditStatus.FAILURE,
            error=str(e)
        )
        raise


@mcp.tool()
def get_financial_summary(
    date_from: str = None,
    date_to: str = None
) -> Dict[str, Any]:
    """
    Get financial summary from Odoo for a date range.

    Args:
        date_from: Start date (YYYY-MM-DD), defaults to first day of current month
        date_to: End date (YYYY-MM-DD), defaults to today

    Returns:
        Dictionary with revenue, expenses, profit, invoice count, bill count
    """
    try:
        odoo = get_odoo()

        # Default date range: current month
        if not date_from:
            date_from = date.today().replace(day=1).isoformat()
        if not date_to:
            date_to = date.today().isoformat()

        # Query customer invoices (revenue)
        invoice_domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', date_from),
            ('invoice_date', '<=', date_to)
        ]

        invoice_ids = odoo.search('account.move', invoice_domain)
        invoices = odoo.read('account.move', invoice_ids, ['amount_total'])

        total_revenue = sum(inv['amount_total'] for inv in invoices)
        invoice_count = len(invoices)

        # Query vendor bills (expenses)
        bill_domain = [
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', date_from),
            ('invoice_date', '<=', date_to)
        ]

        bill_ids = odoo.search('account.move', bill_domain)
        bills = odoo.read('account.move', bill_ids, ['amount_total'])

        total_expenses = sum(bill['amount_total'] for bill in bills)
        bill_count = len(bills)

        # Calculate profit
        profit = total_revenue - total_expenses
        profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0.0

        result = {
            'date_from': date_from,
            'date_to': date_to,
            'revenue': total_revenue,
            'expenses': total_expenses,
            'profit': profit,
            'profit_margin': profit_margin,
            'invoice_count': invoice_count,
            'bill_count': bill_count
        }

        logger.info(f"Financial summary {date_from} to {date_to}: Revenue ${total_revenue}, Expenses ${total_expenses}, Profit ${profit}")

        return result

    except Exception as e:
        logger.error(f"Failed to get financial summary: {e}")
        raise


@mcp.tool()
def list_recent_invoices(limit: int = 10) -> List[Dict[str, Any]]:
    """
    List recent customer invoices.

    Args:
        limit: Maximum number of invoices to return (default 10)

    Returns:
        List of invoice dictionaries with id, number, customer, total, date, status
    """
    try:
        odoo = get_odoo()

        # Search for customer invoices, ordered by date descending
        invoice_ids = odoo.search(
            'account.move',
            [('move_type', '=', 'out_invoice')],
            limit=limit
        )

        invoices = odoo.read('account.move', invoice_ids, [
            'name', 'partner_id', 'amount_total', 'invoice_date', 'state'
        ])

        result = []
        for inv in invoices:
            result.append({
                'invoice_id': inv['id'],
                'invoice_number': inv['name'],
                'customer': inv['partner_id'][1] if inv['partner_id'] else 'Unknown',
                'total': inv['amount_total'],
                'date': inv['invoice_date'],
                'status': inv['state']
            })

        return result

    except Exception as e:
        logger.error(f"Failed to list invoices: {e}")
        raise


@mcp.tool()
def list_recent_bills(limit: int = 10) -> List[Dict[str, Any]]:
    """
    List recent vendor bills (expenses).

    Args:
        limit: Maximum number of bills to return (default 10)

    Returns:
        List of bill dictionaries with id, number, vendor, total, date, status
    """
    try:
        odoo = get_odoo()

        # Search for vendor bills, ordered by date descending
        bill_ids = odoo.search(
            'account.move',
            [('move_type', '=', 'in_invoice')],
            limit=limit
        )

        bills = odoo.read('account.move', bill_ids, [
            'name', 'partner_id', 'amount_total', 'invoice_date', 'state'
        ])

        result = []
        for bill in bills:
            result.append({
                'bill_id': bill['id'],
                'bill_number': bill['name'],
                'vendor': bill['partner_id'][1] if bill['partner_id'] else 'Unknown',
                'total': bill['amount_total'],
                'date': bill['invoice_date'],
                'status': bill['state']
            })

        return result

    except Exception as e:
        logger.error(f"Failed to list bills: {e}")
        raise


@mcp.tool()
def list_products(
    limit: int = 20, 
    domain: str = None
) -> List[Dict[str, Any]]:
    """
    List products from Odoo.

    Args:
        limit: Maximum number of products to return
        domain: Optional search domain (e.g. name of product)

    Returns:
        List of products with id, name, list_price, type
    """
    try:
        odoo = get_odoo()
        
        search_domain = []
        if domain:
            search_domain = [('name', 'ilike', domain)]
            
        product_ids = odoo.search('product.product', search_domain, limit=limit)
        products = odoo.read('product.product', product_ids, ['name', 'list_price', 'type', 'default_code'])
        
        result = []
        for p in products:
            result.append({
                'id': p['id'],
                'name': p['name'],
                'price': p['list_price'],
                'type': p['type'],
                'code': p['default_code'] or ''
            })
            
        return result
    except Exception as e:
        logger.error(f"Failed to list products: {e}")
        raise


@mcp.tool()
def get_partner_details(partner_name: str) -> Dict[str, Any]:
    """
    Get details of a partner (customer/vendor).

    Args:
        partner_name: Name of the partner to search for

    Returns:
        Dictionary with partner details
    """
    try:
        odoo = get_odoo()
        
        partner_ids = odoo.search('res.partner', [('name', 'ilike', partner_name)], limit=1)
        if not partner_ids:
            return {"error": "Partner not found"}
            
        partner = odoo.read('res.partner', partner_ids, ['name', 'email', 'phone', 'street', 'city', 'country_id'])[0]
        
        return {
            'id': partner['id'],
            'name': partner['name'],
            'email': partner['email'],
            'phone': partner['phone'],
            'address': f"{partner['street'] or ''}, {partner['city'] or ''}",
            'country': partner['country_id'][1] if partner['country_id'] else ''
        }
    except Exception as e:
        logger.error(f"Failed to get partner details: {e}")
        raise


@mcp.tool()
def check_connection() -> Dict[str, Any]:
    """
    Check connection to Odoo server.
    
    Returns:
        Dictionary with connection status and server version info
    """
    try:
        odoo = get_odoo()
        
        # Get server version info
        version_info = odoo.common.version()
        
        return {
            "status": "connected",
            "url": ODOO_URL,
            "database": ODOO_DB,
            "user_id": odoo.uid,
            "server_version": version_info.get("server_version"),
            "protocol_version": version_info.get("protocol_version")
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "url": ODOO_URL
        }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
