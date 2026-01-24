# Odoo Community Edition Setup Guide

## Quick Start

### 1. Start Odoo with Docker Compose

```bash
# From project root
docker-compose -f docker-compose.odoo.yml up -d

# Check status
docker-compose -f docker-compose.odoo.yml ps

# View logs
docker-compose -f docker-compose.odoo.yml logs -f odoo
```

### 2. Access Odoo Web Interface

- **URL**: http://localhost:8069
- **First-time setup**:
  - Database name: `digital_fte`
  - Email: `admin@digitalfte.local`
  - Password: `Admin@2026!` (change after first login)
  - Demo data: **No** (unchecked)
  - Language: English
  - Country: Your country

### 3. Configure Odoo for MCP Server

After initial setup, configure the following:

#### Install Required Modules

1. Go to **Apps** menu
2. Remove **Apps** filter to show all
3. Install:
   - **Accounting** (account) - Core financial module
   - **Contacts** (contacts) - Customer/vendor management
   - **Invoicing** (account_invoicing) - Invoice creation

#### Configure Company Settings

1. Go to **Settings** → **General Settings**
2. Set up company information:
   - Company name
   - Currency
   - Timezone

3. Go to **Accounting** → **Configuration** → **Settings**
4. Configure:
   - Chart of Accounts (select your country)
   - Fiscal year
   - Tax configuration

### 4. Configure Environment Variables

Update your `.env` file:

```bash
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=digital_fte
ODOO_USERNAME=admin
ODOO_PASSWORD=Admin@2026!
```

⚠️ **Security Note**: Change the password after setup and store securely.

### 5. Test MCP Server Connection

```bash
# From project root
python src/mcp_servers/odoo_server.py
```

In another terminal, test with Claude Code or MCP Inspector:

```bash
# Test connection
mcp test odoo check_connection

# Create a test invoice
mcp test odoo create_customer_invoice \
  --customer_name "Test Customer" \
  --invoice_lines '[{"product_name": "Consulting", "quantity": 1, "unit_price": 100}]'

# Get financial summary
mcp test odoo get_financial_summary
```

## Configuration in Claude Code

Add to `.claude/mcp_settings.json`:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "python",
      "args": ["src/mcp_servers/odoo_server.py"],
      "cwd": "D:\\Hacathan_2",
      "env": {
        "PYTHONPATH": "D:\\Hacathan_2\\src",
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "digital_fte",
        "ODOO_USERNAME": "admin"
      }
    }
  }
}
```

## Troubleshooting

### Odoo Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose.odoo.yml logs odoo

# Restart services
docker-compose -f docker-compose.odoo.yml restart

# Clean restart
docker-compose -f docker-compose.odoo.yml down
docker-compose -f docker-compose.odoo.yml up -d
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker ps | grep odoo_postgres

# Check database exists
docker exec -it odoo_postgres psql -U odoo -l
```

### MCP Server Connection Errors

1. Verify Odoo is accessible: http://localhost:8069
2. Check credentials in `.env`
3. Verify database name matches
4. Check firewall isn't blocking port 8069

### XML-RPC Authentication Failed

- Ensure you've completed first-time setup in web interface
- Verify username/password are correct
- Check database name matches exactly

## Data Backup

```bash
# Backup database
docker exec -it odoo_postgres pg_dump -U odoo digital_fte > backup_$(date +%Y%m%d).sql

# Restore database
docker exec -i odoo_postgres psql -U odoo digital_fte < backup_20260122.sql
```

## Stopping Odoo

```bash
# Stop services
docker-compose -f docker-compose.odoo.yml stop

# Stop and remove containers
docker-compose -f docker-compose.odoo.yml down

# Stop and remove everything including volumes (CAUTION: deletes data)
docker-compose -f docker-compose.odoo.yml down -v
```

## Production Considerations

For production deployment:

1. **Change all default passwords**
2. **Use environment variables for secrets**
3. **Enable HTTPS with reverse proxy**
4. **Configure regular database backups**
5. **Set up log rotation**
6. **Monitor resource usage**
7. **Configure firewall rules**

## MCP Tools Available

Once configured, the following tools are available to Claude Code:

- `create_customer_invoice` - Create invoices for customers
- `record_expense` - Record vendor bills/expenses
- `get_financial_summary` - Get revenue, expenses, profit for date range
- `list_recent_invoices` - List recent customer invoices
- `list_recent_bills` - List recent vendor bills
- `list_products` - List products/services
- `get_partner_details` - Get customer/vendor details
- `check_connection` - Test Odoo connection

## Integration with Digital FTE

The Odoo MCP server integrates with:

- **Gmail Watcher** - Auto-create expenses from vendor emails
- **CEO Briefing** - Financial metrics in weekly reports
- **Approval Workflow** - Human approval for large invoices
- **Audit Logger** - All transactions logged for compliance

## Next Steps

1. ✅ Start Odoo containers
2. ✅ Complete web setup
3. ✅ Install required modules
4. ✅ Configure environment variables
5. ✅ Test MCP connection
6. ✅ Add to Claude Code MCP settings
7. ✅ Test with sample invoice/expense
8. ✅ Integrate with watchers

---

**Status**: Ready for Gold Tier validation
**Last Updated**: 2026-01-22
