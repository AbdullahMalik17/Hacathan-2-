# Gold Tier Implementation Tasks

> **Project:** Digital FTE (Abdullah Junior)
> **Phase:** Gold Tier Implementation
> **Created:** 2026-01-18
> **Status:** Ready to Execute

---

## Task Legend

- 🔴 **High Priority** - Critical path, blocks other work
- 🟡 **Medium Priority** - Important but not blocking
- 🟢 **Low Priority** - Nice to have, can be deferred

**Status Values:**
- ⬜ Not Started
- 🔄 In Progress
- ✅ Complete
- ❌ Blocked
- ⏸️ On Hold

---

## Phase 1: Foundation (Week 1)

### T1.1: Enhanced Audit Logging System 🔴

**Status:** ⬜ Not Started
**Priority:** High
**Estimated Time:** 8 hours
**Dependencies:** None

#### Subtasks

- [ ] **T1.1.1:** Create audit logger module
  - File: `src/utils/audit_logger.py`
  - Implement `AuditLogger` class
  - JSONL format writing
  - Daily log rotation
  - Log level filtering

- [ ] **T1.1.2:** Define audit log schema
  ```python
  {
    "timestamp": "2026-01-18T10:30:00Z",
    "action": "domain.operation",
    "actor": "orchestrator|human|watcher",
    "domain": "personal|business|system",
    "resource": "resource_id",
    "status": "success|failure|pending",
    "details": {},
    "approval_required": bool,
    "approved_by": null | "human",
    "error": null | "error_message"
  }
  ```

- [ ] **T1.1.3:** Implement query interface
  - Query by date range
  - Query by action type
  - Query by status
  - Query by domain
  - Export filtered logs

- [ ] **T1.1.4:** Integrate into existing components
  - Update `src/orchestrator.py`
  - Update `src/mcp_servers/email_sender.py`
  - Update all watchers
  - Update `src/utils/file_manager.py`

#### Acceptance Criteria

- [ ] Audit logger writes JSONL format correctly
- [ ] Logs rotate daily (new file each day)
- [ ] Query interface returns correct filtered results
- [ ] All operations logged with complete metadata
- [ ] No performance degradation (< 5ms overhead per operation)

#### Test Cases

1. **Test:** Create 100 log entries
   - **Expected:** All written to JSONL file with correct format

2. **Test:** Query logs by date range
   - **Expected:** Only logs in range returned

3. **Test:** Query logs by action = "odoo.create_invoice"
   - **Expected:** Only invoice creation logs returned

4. **Test:** Trigger log rotation (next day)
   - **Expected:** New log file created, old file preserved

---

### T1.2: Error Recovery Framework 🔴

**Status:** ⬜ Not Started
**Priority:** High
**Estimated Time:** 16 hours
**Dependencies:** None

#### Subtasks

- [ ] **T1.2.1:** Create error recovery module
  - File: `src/utils/error_recovery.py`
  - Implement retry decorator
  - Exponential backoff algorithm
  - Max retry configuration
  - Success/failure callbacks

- [ ] **T1.2.2:** Implement circuit breaker
  - Circuit states: CLOSED, OPEN, HALF_OPEN
  - Failure threshold configuration
  - Reset timeout
  - State persistence
  - Health check integration

- [ ] **T1.2.3:** Create dead letter queue
  - File: `src/utils/dead_letter_queue.py`
  - Queue failed tasks
  - Metadata: failure reason, retry count, last attempt
  - Retry from queue (manual or scheduled)
  - Queue inspection and management

- [ ] **T1.2.4:** Implement error notifications
  - Console logging
  - Audit log integration
  - Email notification for critical errors (optional)
  - Error summary in health dashboard

- [ ] **T1.2.5:** Integrate into all API calls
  - Wrap Odoo API calls
  - Wrap social media API calls
  - Wrap Gmail API calls
  - Wrap file operations

#### Acceptance Criteria

- [ ] Retry decorator retries 3 times with exponential backoff
- [ ] Circuit breaker opens after 5 consecutive failures
- [ ] Circuit breaker half-opens after 60 seconds
- [ ] Failed tasks queued to DLQ with complete metadata
- [ ] Critical errors logged and alerted
- [ ] System continues operating when one service fails

#### Test Cases

1. **Test:** API call fails 2 times, succeeds on 3rd
   - **Expected:** Retry succeeds, no DLQ entry

2. **Test:** API call fails 5 times consecutively
   - **Expected:** Circuit breaker opens, subsequent calls fail fast

3. **Test:** Circuit breaker open, wait 60 seconds
   - **Expected:** Circuit breaker half-opens, allows retry

4. **Test:** Task fails max retries
   - **Expected:** Task queued to DLQ with failure metadata

5. **Test:** Service A fails, Service B operational
   - **Expected:** System continues using Service B, Service A degraded

---

### T1.3: Health Monitoring System 🟡

**Status:** ⬜ Not Started
**Priority:** Medium
**Estimated Time:** 12 hours
**Dependencies:** T1.2 (uses circuit breaker status)

#### Subtasks

- [ ] **T1.3.1:** Create health monitor module
  - File: `src/monitoring/health_monitor.py`
  - Service health check registry
  - Health check execution (every 5 minutes)
  - Status aggregation
  - Metric collection

- [ ] **T1.3.2:** Define health checks
  - **Odoo:** Can connect and query
  - **Gmail API:** Can authenticate
  - **Social APIs:** Can authenticate
  - **File System:** Can read/write vault
  - **Watchers:** Process running
  - **Orchestrator:** Process running

- [ ] **T1.3.3:** Collect performance metrics
  - Task processing time (avg, p95, p99)
  - MCP server response time
  - API call latency
  - Error rate (by service)
  - Resource usage (CPU, memory, disk)

- [ ] **T1.3.4:** Create health dashboard data
  - File: `Vault/Dashboard_Data.json`
  - Real-time service status
  - Current metrics
  - Recent errors
  - Uptime statistics

- [ ] **T1.3.5:** Update Dashboard.md
  - Display service status
  - Show key metrics
  - List recent errors
  - Uptime percentage

#### Acceptance Criteria

- [ ] All services have health checks
- [ ] Health checks run every 5 minutes
- [ ] Dashboard_Data.json updates in real-time
- [ ] Dashboard.md shows current system health
- [ ] Unhealthy services clearly identified
- [ ] Metrics accurate and up-to-date

#### Test Cases

1. **Test:** All services healthy
   - **Expected:** Dashboard shows all green

2. **Test:** Stop Odoo container
   - **Expected:** Dashboard shows Odoo unhealthy within 5 minutes

3. **Test:** Restart Odoo
   - **Expected:** Dashboard shows Odoo healthy within 5 minutes

4. **Test:** Check performance metrics
   - **Expected:** Metrics show realistic values

---

### T1.4: Cross-Domain Data Model 🟡

**Status:** ⬜ Not Started
**Priority:** Medium
**Estimated Time:** 8 hours
**Dependencies:** None

#### Subtasks

- [ ] **T1.4.1:** Create task model
  - File: `src/models/task.py`
  - Define `Task` class with domain field
  - Domain values: personal, business, both
  - Task dependencies
  - Task metadata

- [ ] **T1.4.2:** Create business metric model
  - File: `src/models/business_metric.py`
  - Financial metrics (revenue, expenses, profit)
  - Social metrics (engagement, followers)
  - Operational metrics (tasks, uptime)

- [ ] **T1.4.3:** Update orchestrator
  - Domain-aware task routing
  - Cross-domain dependency tracking
  - Business context in personal tasks
  - Personal context in business tasks

- [ ] **T1.4.4:** Create domain classifier
  - Keywords for personal vs. business
  - Email domain detection
  - Context-based classification
  - Manual override capability

#### Acceptance Criteria

- [ ] Tasks correctly classified as personal/business/both
- [ ] Cross-domain dependencies tracked
- [ ] Business metrics integrated into personal dashboard
- [ ] Orchestrator routes based on domain
- [ ] Domain override works for edge cases

#### Test Cases

1. **Test:** Email from work domain
   - **Expected:** Classified as business

2. **Test:** Email from personal domain
   - **Expected:** Classified as personal

3. **Test:** Task with business and personal implications
   - **Expected:** Classified as both

4. **Test:** Business task blocks personal task
   - **Expected:** Dependency tracked and enforced

---

## Phase 2: Odoo Integration (Week 2)

### T2.1: Odoo Installation & Setup 🔴

**Status:** ⬜ Not Started
**Priority:** High
**Estimated Time:** 4 hours
**Dependencies:** None (Docker Desktop prerequisite)

#### Subtasks

- [ ] **T2.1.1:** Install Docker Desktop
  - Download from docker.com
  - Install for Windows
  - Verify installation: `docker --version`

- [ ] **T2.1.2:** Pull Odoo 19 Docker image
  - Command: `docker pull odoo:19`
  - Verify image: `docker images | grep odoo`

- [ ] **T2.1.3:** Run Odoo container
  - Command: `docker run -d -p 8069:8069 --name odoo odoo:19`
  - Access at http://localhost:8069
  - Verify Odoo loads

- [ ] **T2.1.4:** Complete Odoo setup wizard
  - Create database: "digital_fte"
  - Set admin password (store in .env)
  - Select language and country
  - Install accounting module

- [ ] **T2.1.5:** Configure chart of accounts
  - Select appropriate chart (US GAAP or similar)
  - Set up account types
  - Configure tax settings

- [ ] **T2.1.6:** Create test data
  - Add 2 test customers
  - Add 3 test products/services
  - Create 1 test invoice
  - Record 1 test expense

- [ ] **T2.1.7:** Document setup process
  - File: `docs/setup/odoo-installation.md`
  - Step-by-step instructions
  - Screenshots
  - Troubleshooting section

#### Acceptance Criteria

- [ ] Odoo accessible at http://localhost:8069
- [ ] Can log in with admin credentials
- [ ] Accounting module installed
- [ ] Chart of accounts configured
- [ ] Test data created successfully
- [ ] Setup guide complete and tested

#### Test Cases

1. **Test:** Access Odoo web interface
   - **Expected:** Login page loads

2. **Test:** Log in with admin credentials
   - **Expected:** Dashboard loads

3. **Test:** Navigate to Accounting module
   - **Expected:** Accounting menu accessible

4. **Test:** View test invoice
   - **Expected:** Invoice displays correctly

5. **Test:** Generate test financial report
   - **Expected:** Report shows test data

---

### T2.2: Odoo MCP Server Development 🔴

**Status:** ⬜ Not Started
**Priority:** High
**Estimated Time:** 24 hours
**Dependencies:** T2.1 (Odoo must be running)

#### Subtasks

- [ ] **T2.2.1:** Create Odoo connector module
  - File: `src/mcp_servers/odoo_connector.py`
  - Initialize FastMCP
  - Create configuration (URL, DB, username, password)

- [ ] **T2.2.2:** Implement JSON-RPC client
  ```python
  class OdooClient:
      def __init__(self, url, db, username, password)
      def authenticate(self) -> int  # Returns uid
      def call(self, model, method, args, kwargs)
  ```

- [ ] **T2.2.3:** Implement MCP tools

  **Tool 1: create_invoice**
  ```python
  @mcp.tool()
  def create_invoice(
      customer_name: str,
      items: List[Dict[str, Any]],  # [{product, qty, price}]
      due_date: str,
      requires_approval: bool = True
  ) -> Dict
  ```

  **Tool 2: record_expense**
  ```python
  @mcp.tool()
  def record_expense(
      category: str,
      amount: float,
      description: str,
      date: str,
      vendor: str = None,
      requires_approval: bool = True
  ) -> Dict
  ```

  **Tool 3: get_financial_summary**
  ```python
  @mcp.tool()
  def get_financial_summary(
      period: str  # "current_month", "last_month", "ytd"
  ) -> Dict  # {revenue, expenses, profit, margin}
  ```

  **Tool 4: create_customer**
  ```python
  @mcp.tool()
  def create_customer(
      name: str,
      email: str,
      phone: str = None,
      address: str = None
  ) -> Dict
  ```

  **Tool 5: create_product**
  ```python
  @mcp.tool()
  def create_product(
      name: str,
      price: float,
      category: str,
      description: str = None
  ) -> Dict
  ```

  **Tool 6: get_accounts_receivable**
  ```python
  @mcp.tool()
  def get_accounts_receivable() -> List[Dict]
  # Returns outstanding invoices
  ```

  **Tool 7: get_accounts_payable**
  ```python
  @mcp.tool()
  def get_accounts_payable() -> List[Dict]
  # Returns unpaid bills
  ```

  **Tool 8: record_payment**
  ```python
  @mcp.tool()
  def record_payment(
      invoice_id: int,
      amount: float,
      payment_method: str,
      date: str
  ) -> Dict
  ```

  **Tool 9: generate_financial_report**
  ```python
  @mcp.tool()
  def generate_financial_report(
      report_type: str,  # "profit_loss", "balance_sheet", "cash_flow"
      date_range: str    # "2026-01-01 to 2026-01-31"
  ) -> Dict
  ```

- [ ] **T2.2.4:** Implement approval workflow
  - Transactions >$1000 → Pending_Approval
  - Create approval file with transaction details
  - Wait for human approval
  - Execute only after approval

- [ ] **T2.2.5:** Integrate error recovery
  - Wrap all Odoo calls with retry decorator
  - Handle connection errors
  - Handle authentication errors
  - Handle data validation errors

- [ ] **T2.2.6:** Integrate audit logging
  - Log all Odoo operations
  - Include transaction details
  - Log approvals
  - Log errors

- [ ] **T2.2.7:** Add configuration management
  - File: `config/odoo_config.json`
  - Store connection details (not password)
  - Password in `.env` file
  - Rate limit settings

#### Acceptance Criteria

- [ ] All 9 tools implemented and functional
- [ ] Can connect to Odoo via JSON-RPC
- [ ] Can create invoices, customers, products
- [ ] Can record expenses and payments
- [ ] Can generate financial reports
- [ ] Approval workflow triggers for >$1000
- [ ] Error recovery handles failures gracefully
- [ ] All operations logged in audit trail

#### Test Cases

1. **Test:** create_invoice with $500 invoice
   - **Expected:** Invoice created in Odoo, no approval required

2. **Test:** create_invoice with $1500 invoice
   - **Expected:** Approval request created, invoice pending

3. **Test:** record_expense with valid data
   - **Expected:** Expense recorded in Odoo

4. **Test:** get_financial_summary for current month
   - **Expected:** Returns accurate revenue, expenses, profit

5. **Test:** create_customer with all fields
   - **Expected:** Customer created in Odoo

6. **Test:** Odoo unavailable (stop container)
   - **Expected:** Error recovery retries, then DLQ

7. **Test:** Invalid authentication
   - **Expected:** Error logged, operation fails gracefully

---

### T2.3: Gmail-Odoo Integration 🟡

**Status:** ⬜ Not Started
**Priority:** Medium
**Estimated Time:** 8 hours
**Dependencies:** T2.2 (Odoo MCP server must be functional)

#### Subtasks

- [ ] **T2.3.1:** Update Gmail watcher
  - File: `src/watchers/gmail_watcher.py`
  - Add receipt/invoice detection
  - Keywords: "invoice", "receipt", "payment", "bill"
  - Extract amount, vendor, date from email

- [ ] **T2.3.2:** Create expense extractor
  - File: `src/utils/expense_extractor.py`
  - Parse email body for financial info
  - Regex patterns for amounts ($XXX.XX)
  - Date extraction
  - Vendor name extraction

- [ ] **T2.3.3:** Integrate with orchestrator
  - Detect "expense" task type
  - Route to Odoo MCP server
  - Call record_expense tool
  - Handle approval if needed

- [ ] **T2.3.4:** Test end-to-end flow
  - Send test email with receipt
  - Verify expense detection
  - Verify Odoo expense creation
  - Verify audit log

#### Acceptance Criteria

- [ ] Gmail watcher detects receipt emails
- [ ] Amount extracted correctly
- [ ] Vendor extracted correctly
- [ ] Date extracted correctly
- [ ] Expense created in Odoo
- [ ] Approval workflow works for large amounts
- [ ] Audit trail complete

#### Test Cases

1. **Test:** Email with receipt for $45.99 from "Amazon"
   - **Expected:** Expense created in Odoo with correct details

2. **Test:** Email with invoice for $1200 from "Supplier XYZ"
   - **Expected:** Approval request created, expense pending

3. **Test:** Email without financial info
   - **Expected:** Not classified as expense, normal task creation

---

### T2.4: Agent Skill Creation 🟢

**Status:** ⬜ Not Started
**Priority:** Low
**Estimated Time:** 4 hours
**Dependencies:** T2.2 (Odoo MCP server)

#### Subtasks

- [ ] **T2.4.1:** Create skill directory
  - Path: `.claude/skills/managing-odoo-accounting/`

- [ ] **T2.4.2:** Create SKILL.md
  - Skill description
  - Usage examples
  - Configuration
  - Troubleshooting

- [ ] **T2.4.3:** Create run.py
  - CLI for Odoo operations
  - Commands: create-invoice, record-expense, get-summary
  - Interactive prompts
  - Output formatting

- [ ] **T2.4.4:** Create verify.py
  - Test Odoo connection
  - Test each MCP tool
  - Verify approval workflow
  - Report results

- [ ] **T2.4.5:** Create references directory
  - Odoo API documentation
  - JSON-RPC examples
  - Troubleshooting guide

#### Acceptance Criteria

- [ ] Skill directory created
- [ ] SKILL.md comprehensive
- [ ] run.py functional with all commands
- [ ] verify.py passes all tests
- [ ] References helpful and accurate

#### Test Cases

1. **Test:** Run verify.py
   - **Expected:** All tests pass

2. **Test:** Run `python run.py create-invoice`
   - **Expected:** Interactive prompt, invoice created

3. **Test:** Run `python run.py get-summary`
   - **Expected:** Financial summary displayed

---

## Phase 3: Social Media Integration (Week 3)

### T3.1: Meta (Facebook & Instagram) Setup 🔴

**Status:** ⬜ Not Started
**Priority:** High
**Estimated Time:** 4 hours
**Dependencies:** None (Facebook/Instagram accounts prerequisite)

#### Subtasks

- [ ] **T3.1.1:** Create Meta Developer Account
  - Visit developers.facebook.com
  - Create developer account
  - Verify account

- [ ] **T3.1.2:** Create Meta App
  - App name: "Digital FTE Social Manager"
  - App type: Business
  - Add Facebook Login product
  - Add Instagram Basic Display product

- [ ] **T3.1.3:** Configure permissions
  - Facebook: pages_manage_posts, pages_read_engagement
  - Instagram: instagram_basic, instagram_content_publish

- [ ] **T3.1.4:** Get access tokens
  - Generate user access token
  - Exchange for long-lived token (60 days)
  - Store in config/social_media_tokens.json (gitignored)
  - Document token refresh process

- [ ] **T3.1.5:** Document setup process
  - File: `docs/setup/meta-api-setup.md`
  - Step-by-step instructions
  - Screenshots
  - Token management guide

#### Acceptance Criteria

- [ ] Meta developer account created
- [ ] App created and configured
- [ ] Permissions granted
- [ ] Access tokens obtained and stored securely
- [ ] Setup guide complete

#### Test Cases

1. **Test:** Access Meta Graph API Explorer
   - **Expected:** Can make test API calls

2. **Test:** Get Facebook Page details
   - **Expected:** Page info returned

3. **Test:** Get Instagram account details
   - **Expected:** Account info returned

---

### T3.2: Meta MCP Server Development 🔴

**Status:** ⬜ Not Started
**Priority:** High
**Estimated Time:** 20 hours
**Dependencies:** T3.1 (Meta API access)

#### Subtasks

- [ ] **T3.2.1:** Create Meta connector module
  - File: `src/mcp_servers/meta_social_connector.py`
  - Initialize FastMCP
  - Create configuration (tokens, page IDs)

- [ ] **T3.2.2:** Implement Facebook Graph API client
  ```python
  class FacebookClient:
      def __init__(self, access_token, page_id)
      def post(self, message, link=None, media_url=None)
      def get_insights(self, days=7)
  ```

- [ ] **T3.2.3:** Implement Instagram Graph API client
  ```python
  class InstagramClient:
      def __init__(self, access_token, account_id)
      def post(self, caption, image_url, hashtags)
      def upload_media(self, image_url)
      def get_insights(self, days=7)
  ```

- [ ] **T3.2.4:** Implement MCP tools

  **Tool 1: post_to_facebook**
  ```python
  @mcp.tool()
  def post_to_facebook(
      content: str,
      media_url: str = None,
      link: str = None,
      scheduled_time: str = None,
      requires_approval: bool = True
  ) -> Dict
  ```

  **Tool 2: post_to_instagram**
  ```python
  @mcp.tool()
  def post_to_instagram(
      caption: str,
      image_url: str,
      hashtags: List[str],
      requires_approval: bool = True
  ) -> Dict
  ```

  **Tool 3: upload_media**
  ```python
  @mcp.tool()
  def upload_media(
      file_path: str,
      platform: str  # "facebook" or "instagram"
  ) -> Dict  # Returns media_id or URL
  ```

  **Tool 4: get_facebook_insights**
  ```python
  @mcp.tool()
  def get_facebook_insights(
      days: int = 7
  ) -> Dict  # {posts, likes, comments, shares, reach, engagement_rate}
  ```

  **Tool 5: get_instagram_insights**
  ```python
  @mcp.tool()
  def get_instagram_insights(
      days: int = 7
  ) -> Dict  # {posts, likes, comments, followers, reach, engagement_rate}
  ```

  **Tool 6: generate_summary**
  ```python
  @mcp.tool()
  def generate_summary(
      platform: str,  # "facebook", "instagram", "both"
      period: str = "week"
  ) -> str  # Markdown summary
  ```

- [ ] **T3.2.5:** Implement approval workflow
  - All posts → Pending_Approval
  - Create approval file with post preview
  - Wait for human approval
  - Post only after approval

- [ ] **T3.2.6:** Implement media handling
  - Download media from URLs
  - Resize/optimize images
  - Upload to platform
  - Clean up temp files

- [ ] **T3.2.7:** Implement rate limiting
  - Facebook: respect API rate limits
  - Instagram: respect posting limits
  - Queue posts if limit reached
  - Retry after rate limit reset

- [ ] **T3.2.8:** Integrate error recovery & audit logging
  - Retry failed posts
  - Handle token expiration
  - Log all operations

#### Acceptance Criteria

- [ ] All 6 tools implemented and functional
- [ ] Can post to Facebook
- [ ] Can post to Instagram
- [ ] Can upload media
- [ ] Can get insights from both platforms
- [ ] Can generate summary reports
- [ ] Approval workflow works
- [ ] Rate limiting prevents API blocks
- [ ] Error recovery handles failures

#### Test Cases

1. **Test:** post_to_facebook with text only
   - **Expected:** Approval request created, post pending

2. **Test:** Approve Facebook post
   - **Expected:** Post published to Facebook

3. **Test:** post_to_instagram with image
   - **Expected:** Approval request with image preview

4. **Test:** get_facebook_insights for 7 days
   - **Expected:** Returns accurate metrics

5. **Test:** generate_summary for "both" platforms
   - **Expected:** Markdown summary with both platforms

6. **Test:** Post when rate limit reached
   - **Expected:** Post queued, retried after limit resets

---

### T3.3: Twitter/X Setup 🔴

**Status:** ⬜ Not Started
**Priority:** High
**Estimated Time:** 4 hours
**Dependencies:** None (Twitter/X account prerequisite)

#### Subtasks

- [ ] **T3.3.1:** Create Twitter Developer Account
  - Visit developer.twitter.com
  - Apply for developer account
  - Wait for approval (can take days)

- [ ] **T3.3.2:** Create Twitter App
  - App name: "Digital FTE Twitter Manager"
  - App type: Automated bot
  - Enable OAuth 2.0

- [ ] **T3.3.3:** Configure permissions
  - Read and write tweets
  - Upload media
  - Read engagement metrics

- [ ] **T3.3.4:** Get API keys and tokens
  - API Key
  - API Secret Key
  - Access Token
  - Access Token Secret
  - Bearer Token
  - Store in config/twitter_tokens.json (gitignored)

- [ ] **T3.3.5:** Document setup process
  - File: `docs/setup/twitter-api-setup.md`

#### Acceptance Criteria

- [ ] Twitter developer account approved
- [ ] App created and configured
- [ ] API keys obtained
- [ ] Setup guide complete

#### Test Cases

1. **Test:** Authenticate with Twitter API
   - **Expected:** Authentication successful

2. **Test:** Get user timeline
   - **Expected:** Recent tweets returned

---

### T3.4: Twitter MCP Server Development 🔴

**Status:** ⬜ Not Started
**Priority:** High
**Estimated Time:** 16 hours
**Dependencies:** T3.3 (Twitter API access)

#### Subtasks

- [ ] **T3.4.1:** Install Tweepy library
  - `pip install tweepy`

- [ ] **T3.4.2:** Create Twitter connector module
  - File: `src/mcp_servers/twitter_connector.py`
  - Initialize FastMCP
  - Create configuration

- [ ] **T3.4.3:** Implement Twitter API v2 client
  ```python
  class TwitterClient:
      def __init__(self, api_key, api_secret, access_token, access_secret)
      def authenticate(self)
      def post_tweet(self, text, media_ids=None, reply_to=None)
      def upload_media(self, file_path)
      def get_timeline_insights(self, days=7)
  ```

- [ ] **T3.4.4:** Implement MCP tools

  **Tool 1: post_tweet**
  ```python
  @mcp.tool()
  def post_tweet(
      content: str,
      media_ids: List[str] = None,
      reply_to_tweet_id: str = None,
      requires_approval: bool = True
  ) -> Dict
  ```

  **Tool 2: upload_media**
  ```python
  @mcp.tool()
  def upload_media(
      file_path: str
  ) -> Dict  # Returns media_id
  ```

  **Tool 3: create_thread**
  ```python
  @mcp.tool()
  def create_thread(
      tweets: List[str],
      media_ids: List[List[str]] = None,
      requires_approval: bool = True
  ) -> Dict
  ```

  **Tool 4: get_timeline_insights**
  ```python
  @mcp.tool()
  def get_timeline_insights(
      days: int = 7
  ) -> Dict  # {tweets, likes, retweets, replies, impressions}
  ```

  **Tool 5: search_mentions**
  ```python
  @mcp.tool()
  def search_mentions(
      query: str,
      max_results: int = 10
  ) -> List[Dict]
  ```

  **Tool 6: generate_summary**
  ```python
  @mcp.tool()
  def generate_summary(
      period: str = "week"
  ) -> str  # Markdown summary
  ```

- [ ] **T3.4.5:** Implement approval workflow
- [ ] **T3.4.6:** Implement rate limiting
- [ ] **T3.4.7:** Integrate error recovery & audit logging

#### Acceptance Criteria

- [ ] All 6 tools functional
- [ ] Can post tweets
- [ ] Can upload media
- [ ] Can create threads
- [ ] Can get insights
- [ ] Can search mentions
- [ ] Approval workflow works
- [ ] Rate limiting prevents blocks

#### Test Cases

1. **Test:** post_tweet with text only
   - **Expected:** Approval request created

2. **Test:** Approve tweet
   - **Expected:** Tweet published

3. **Test:** post_tweet with media
   - **Expected:** Media uploaded, tweet with media

4. **Test:** create_thread with 3 tweets
   - **Expected:** Thread created as replies

5. **Test:** get_timeline_insights
   - **Expected:** Accurate metrics returned

---

### T3.5: Social Content Generator 🟡

**Status:** ⬜ Not Started
**Priority:** Medium
**Estimated Time:** 12 hours
**Dependencies:** T3.2, T3.4 (MCP servers)

#### Subtasks

- [ ] **T3.5.1:** Create content generator module
  - File: `src/content/social_content_generator.py`

- [ ] **T3.5.2:** Implement content strategies
  ```python
  def generate_business_update(source_data: Dict) -> Dict
  # Returns content for each platform

  def generate_industry_tip() -> Dict

  def generate_engagement_post() -> Dict
  ```

- [ ] **T3.5.3:** Implement platform-specific formatting
  - Facebook: 200-300 words, link previews
  - Instagram: Visual focus, 10-15 hashtags, emoji
  - Twitter: 280 chars, threading for longer content
  - LinkedIn: Professional, longer form

- [ ] **T3.5.4:** Implement hashtag optimization
  - Research trending hashtags
  - Industry-specific tags
  - Avoid over-tagging

- [ ] **T3.5.5:** Implement posting time optimization
  - Analyze best performing post times
  - Suggest optimal posting schedule
  - Default to business hours

#### Acceptance Criteria

- [ ] Content generated for all platforms
- [ ] Platform-specific formatting correct
- [ ] Hashtags relevant and optimized
- [ ] Posting times suggested
- [ ] Content quality high

#### Test Cases

1. **Test:** Generate business update from CEO briefing
   - **Expected:** Content for FB, IG, Twitter, LinkedIn

2. **Test:** Verify Instagram hashtags
   - **Expected:** 10-15 relevant hashtags

3. **Test:** Verify Twitter length
   - **Expected:** <= 280 characters

---

### T3.6: Social Media Agent Skills 🟢

**Status:** ⬜ Not Started
**Priority:** Low
**Estimated Time:** 8 hours
**Dependencies:** T3.2, T3.4 (MCP servers)

#### Subtasks

- [ ] **T3.6.1:** Create posting-facebook skill
  - Path: `.claude/skills/posting-facebook/`
  - SKILL.md, run.py, verify.py, references/

- [ ] **T3.6.2:** Create posting-instagram skill
  - Path: `.claude/skills/posting-instagram/`

- [ ] **T3.6.3:** Create posting-twitter skill
  - Path: `.claude/skills/posting-twitter/`

- [ ] **T3.6.4:** Create managing-social-media skill
  - Path: `.claude/skills/managing-social-media/`
  - Cross-platform management
  - Analytics aggregation
  - Content scheduling

#### Acceptance Criteria

- [ ] All 4 skills created
- [ ] All verify.py pass
- [ ] All documentation complete

---

## Phase 4: Intelligence & Reporting (Week 4)

### T4.1: Enhanced Ralph Wiggum Loop 🔴

**Status:** ⬜ Not Started
**Priority:** High
**Estimated Time:** 20 hours
**Dependencies:** T2.2, T3.2, T3.4 (MCP servers for multi-step tasks)

#### Subtasks

- [ ] **T4.1.1:** Design multi-step planning algorithm
  - File: `src/planning/task_planner.py`
  - Analyze task complexity
  - Break into atomic sub-tasks
  - Identify dependencies
  - Determine execution order (parallel vs sequential)

- [ ] **T4.1.2:** Implement dependency graph
  ```python
  class DependencyGraph:
      def add_task(self, task_id, dependencies=[])
      def get_executable_tasks(self) -> List[str]
      def mark_complete(self, task_id)
      def is_complete(self) -> bool
  ```

- [ ] **T4.1.3:** Implement plan execution engine
  ```python
  class PlanExecutor:
      def execute_plan(self, plan: Plan) -> ExecutionResult
      def execute_step(self, step: Step) -> StepResult
      def rollback(self, plan: Plan, failed_step: Step)
      def report_progress(self, plan: Plan)
  ```

- [ ] **T4.1.4:** Implement learning mechanism
  - File: `src/learning/outcome_learner.py`
  - Track task outcomes (success, failure, duration)
  - Update complexity heuristics
  - Improve decision trees
  - Store learned patterns

- [ ] **T4.1.5:** Implement autonomous execution modes
  - **Low Risk:** Execute without approval
  - **Medium Risk:** Request approval at key milestones
  - **High Risk:** Request approval for each step

- [ ] **T4.1.6:** Update orchestrator
  - Integrate task planner
  - Integrate plan executor
  - Integrate learner
  - Add risk assessment

#### Acceptance Criteria

- [ ] Multi-step tasks broken down correctly
- [ ] Dependencies tracked accurately
- [ ] Parallel tasks execute simultaneously
- [ ] Sequential tasks execute in order
- [ ] Rollback works on failure
- [ ] Learning improves decisions over time
- [ ] Autonomous execution works for low-risk
- [ ] Approval requested for high-risk

#### Test Cases

1. **Test:** Simple multi-step task (3 sequential steps)
   - **Expected:** Steps execute in order, all complete

2. **Test:** Complex task with parallel and sequential steps
   - **Expected:** Parallel steps run together, sequential after

3. **Test:** Task with step failure
   - **Expected:** Rollback triggered, state restored

4. **Test:** Low-risk task (< $100 expense)
   - **Expected:** Executes without approval

5. **Test:** High-risk task (> $1000 invoice)
   - **Expected:** Approval requested

6. **Test:** Same task type repeated 10 times
   - **Expected:** Execution improves (faster, fewer errors)

---

### T4.2: Business Audit Generator 🔴

**Status:** ⬜ Not Started
**Priority:** High
**Estimated Time:** 16 hours
**Dependencies:** T2.2 (Odoo), T3.2 (Meta), T3.4 (Twitter)

#### Subtasks

- [ ] **T4.2.1:** Create business audit module
  - File: `src/reports/business_audit_generator.py`

- [ ] **T4.2.2:** Implement data collection

  **Financial Data:**
  - Revenue (Odoo invoices)
  - Expenses (Odoo expenses)
  - Profit/Loss
  - Outstanding invoices
  - Bills due
  - Cash flow trend

  **Social Media Data:**
  - Posts published (all platforms)
  - Engagement metrics (likes, comments, shares)
  - Follower growth
  - Best performing content
  - Reach and impressions

  **Operational Data:**
  - Tasks completed vs pending
  - Watcher performance (uptime, tasks created)
  - System uptime
  - Error rates (by service)
  - Response times

  **Personal Productivity:**
  - Emails processed
  - Important tasks completed
  - Response times
  - Auto-replies sent

- [ ] **T4.2.3:** Implement report generation
  ```python
  def generate_business_audit(date_range: str) -> str:
      # Returns markdown report
  ```

  **Report Sections:**
  1. Executive Summary
  2. Financial Performance
  3. Social Media Performance
  4. Operational Metrics
  5. Personal Productivity
  6. Key Wins & Challenges
  7. Action Items for Next Week
  8. Strategic Recommendations

- [ ] **T4.2.4:** Enhance CEO briefing integration
  - Update `src/reports/ceo_briefing_generator.py`
  - Include financial section
  - Include social media section
  - Include cross-platform analytics

- [ ] **T4.2.5:** Implement PDF export
  - Install reportlab: `pip install reportlab`
  - Convert markdown to PDF
  - Include charts/graphs
  - Professional formatting

- [ ] **T4.2.6:** Implement scheduling
  - Weekly generation (Sunday night)
  - Save to Vault/Reports/
  - Email delivery option
  - LinkedIn post draft creation

#### Acceptance Criteria

- [ ] Weekly audit generates automatically
- [ ] All data sections present and accurate
- [ ] Financial data from Odoo included
- [ ] Social media metrics from all platforms
- [ ] Operational metrics from logs
- [ ] PDF export works
- [ ] CEO briefing enhanced
- [ ] Delivered via email (optional)

#### Test Cases

1. **Test:** Generate audit for current week
   - **Expected:** All sections populated

2. **Test:** Verify financial data
   - **Expected:** Matches Odoo reports

3. **Test:** Verify social media metrics
   - **Expected:** Matches platform analytics

4. **Test:** Export to PDF
   - **Expected:** Professional PDF generated

5. **Test:** Schedule weekly generation
   - **Expected:** Runs automatically on Sunday

---

### T4.3: Agent Skills for Intelligence 🟢

**Status:** ⬜ Not Started
**Priority:** Low
**Estimated Time:** 4 hours
**Dependencies:** T4.1, T4.2

#### Subtasks

- [ ] **T4.3.1:** Create generating-business-audit skill
  - Path: `.claude/skills/generating-business-audit/`

- [ ] **T4.3.2:** Create monitoring-system-health skill
  - Path: `.claude/skills/monitoring-system-health/`

- [ ] **T4.3.3:** Update SKILLS-INDEX.md
  - Add new skills to index
  - Update counts

#### Acceptance Criteria

- [ ] Skills created and verified
- [ ] Index updated

---

## Phase 5: Documentation & Testing (Week 5)

### T5.1: Architecture Documentation 🟡

**Status:** ⬜ Not Started
**Priority:** Medium
**Estimated Time:** 16 hours
**Dependencies:** All previous phases (need complete system)

#### Subtasks

- [ ] **T5.1.1:** Create docs directory structure
  ```
  docs/
  ├── architecture/
  │   ├── overview.md
  │   ├── mcp-servers.md
  │   ├── watchers.md
  │   ├── orchestrator.md
  │   └── ralph-wiggum-loop.md
  ├── setup/
  │   ├── environment-setup.md
  │   ├── odoo-installation.md
  │   ├── social-media-apis.md
  │   └── troubleshooting.md
  └── lessons-learned.md
  ```

- [ ] **T5.1.2:** Write overview.md
  - System purpose and goals
  - High-level architecture diagram
  - Component descriptions
  - Data flow diagram
  - Technology stack
  - Design principles

- [ ] **T5.1.3:** Write mcp-servers.md
  - Server responsibilities
  - API interfaces for each server
  - Authentication flows
  - Error handling patterns
  - Rate limiting strategies
  - Examples for each tool

- [ ] **T5.1.4:** Write watchers.md
  - Watcher types and purposes
  - Polling strategies
  - Task creation logic
  - Deduplication mechanisms
  - Configuration options

- [ ] **T5.1.5:** Write orchestrator.md
  - Decision logic flow
  - Task routing algorithm
  - Multi-agent fallback
  - Approval workflow
  - Configuration

- [ ] **T5.1.6:** Write ralph-wiggum-loop.md
  - Loop concept and origin
  - Multi-step planning
  - Dependency management
  - Execution strategies
  - Learning mechanism
  - Examples

- [ ] **T5.1.7:** Create diagrams
  - System architecture (components)
  - Data flow (input to output)
  - Deployment architecture
  - MCP server interactions
  - Ralph Wiggum loop flowchart

#### Acceptance Criteria

- [ ] All architecture docs complete
- [ ] Diagrams clear and accurate
- [ ] Technical details correct
- [ ] Examples helpful
- [ ] Readable by new team members

---

### T5.2: Setup Guides 🟡

**Status:** ⬜ Not Started
**Priority:** Medium
**Estimated Time:** 12 hours
**Dependencies:** All previous phases

#### Subtasks

- [ ] **T5.2.1:** Write environment-setup.md
  - Prerequisites (Python, Docker, etc.)
  - Repository setup
  - Python environment setup
  - Configuration files
  - Environment variables
  - Initial test

- [ ] **T5.2.2:** Write odoo-installation.md (expand from T2.1.7)
  - Docker installation
  - Odoo container setup
  - Database creation
  - Module installation
  - Chart of accounts setup
  - Test data creation
  - Troubleshooting

- [ ] **T5.2.3:** Write social-media-apis.md
  - Meta (Facebook & Instagram) setup
  - Twitter/X setup
  - API access tokens
  - Permission configuration
  - Token refresh process
  - Troubleshooting

- [ ] **T5.2.4:** Write troubleshooting.md
  - Common issues and solutions
  - Error messages and meanings
  - Debug mode
  - Logs location
  - Support contacts

#### Acceptance Criteria

- [ ] Setup guides complete
- [ ] Fresh install tested following guides
- [ ] All steps work
- [ ] Troubleshooting helpful

---

### T5.3: Lessons Learned 🟡

**Status:** ⬜ Not Started
**Priority:** Medium
**Estimated Time:** 8 hours
**Dependencies:** All previous phases

#### Subtasks

- [ ] **T5.3.1:** Create lessons-learned.md

- [ ] **T5.3.2:** Document what worked well
  - Successful patterns
  - Effective tools
  - Good decisions

- [ ] **T5.3.3:** Document what didn't work
  - Failed approaches
  - Wrong tools
  - Mistakes made

- [ ] **T5.3.4:** Document design decisions
  - Why we chose X over Y
  - Trade-offs considered
  - Rationale for key choices

- [ ] **T5.3.5:** Document what we'd change
  - If starting over
  - Known improvements
  - Future enhancements

- [ ] **T5.3.6:** Document best practices
  - Patterns to follow
  - Patterns to avoid
  - Recommendations

#### Acceptance Criteria

- [ ] Document complete
- [ ] Insights actionable
- [ ] Lessons valuable for future projects

---

### T5.4: Final Testing & Verification 🔴

**Status:** ⬜ Not Started
**Priority:** High
**Estimated Time:** 16 hours
**Dependencies:** All previous phases

#### Subtasks

- [ ] **T5.4.1:** Create Gold Tier verification checklist
  - File: `GOLD_TIER_VERIFICATION.md`
  - List all requirements
  - Verification steps for each
  - Evidence to collect

- [ ] **T5.4.2:** Test each Gold Tier requirement

  **Requirement 1: All Silver requirements**
  - [ ] All Silver features still working
  - [ ] No regressions

  **Requirement 2: Cross-domain integration**
  - [ ] Tasks classified by domain
  - [ ] Cross-domain dependencies work
  - [ ] Business metrics in personal dashboard

  **Requirement 3: Odoo integration**
  - [ ] Odoo running and accessible
  - [ ] All 9 MCP tools functional
  - [ ] Financial data accurate
  - [ ] Approval workflow works

  **Requirement 4: Facebook & Instagram**
  - [ ] Posts to Facebook
  - [ ] Posts to Instagram
  - [ ] Media uploads work
  - [ ] Analytics accurate
  - [ ] Summaries generated

  **Requirement 5: Twitter/X**
  - [ ] Posts tweets
  - [ ] Media uploads work
  - [ ] Threads work
  - [ ] Analytics accurate
  - [ ] Summaries generated

  **Requirement 6: Multiple MCP servers**
  - [ ] 4+ MCP servers operational
  - [ ] Each handles specific domain
  - [ ] Shared utilities work
  - [ ] Health monitoring works

  **Requirement 7: Weekly business audit**
  - [ ] Audit generates automatically
  - [ ] All sections complete
  - [ ] Data accurate
  - [ ] CEO briefing enhanced

  **Requirement 8: Error recovery**
  - [ ] Retry logic works
  - [ ] Circuit breakers work
  - [ ] DLQ captures failures
  - [ ] Graceful degradation works

  **Requirement 9: Audit logging**
  - [ ] All operations logged
  - [ ] Logs queryable
  - [ ] Format correct
  - [ ] Retention policy active

  **Requirement 10: Ralph Wiggum loop**
  - [ ] Multi-step execution works
  - [ ] Dependencies tracked
  - [ ] Learning improves over time
  - [ ] Risk-based approval works

  **Requirement 11: Documentation**
  - [ ] Architecture docs complete
  - [ ] Setup guides tested
  - [ ] Lessons learned documented

  **Requirement 12: Agent Skills**
  - [ ] All 7 new skills created
  - [ ] All verify.py pass
  - [ ] Index updated

- [ ] **T5.4.3:** Run 1-week stability test
  - Start all services
  - Run for 7 days continuously
  - Monitor for crashes
  - Monitor for errors
  - Measure uptime
  - Collect metrics

- [ ] **T5.4.4:** Fix any issues found
  - Document issues
  - Prioritize fixes
  - Implement fixes
  - Re-test

- [ ] **T5.4.5:** Create final verification report
  - File: `GOLD_TIER_COMPLETE.md`
  - Document all passing tests
  - Include evidence (screenshots, logs)
  - Note any limitations
  - Recommendations for future

#### Acceptance Criteria

- [ ] All Gold Tier requirements verified
- [ ] 99% uptime for 1 week
- [ ] No unhandled errors
- [ ] All tests passing
- [ ] Verification report complete

#### Test Cases

1. **Test:** End-to-end business workflow
   - Email receipt → Odoo expense → Weekly audit
   - **Expected:** Full workflow completes

2. **Test:** End-to-end social media workflow
   - CEO briefing → Content generation → Multi-platform posts
   - **Expected:** Posts on FB, IG, Twitter, LinkedIn

3. **Test:** Multi-step autonomous task
   - Create invoice for client X
   - **Expected:** Customer checked, invoice created, email sent

4. **Test:** Error recovery
   - Stop Odoo, trigger expense
   - **Expected:** Retry, then DLQ, continue other operations

5. **Test:** System under load
   - 100 tasks in Needs_Action
   - **Expected:** All processed, no crashes

---

## Summary

**Total Tasks:** 60+
**Estimated Time:** 250-300 hours (6-8 weeks part-time)
**Critical Path:** Foundation → Odoo → Social Media → Intelligence → Documentation
**Parallel Work:** Agent Skills can be created alongside feature development

### Priority Distribution
- 🔴 **High Priority:** 15 tasks (critical path)
- 🟡 **Medium Priority:** 10 tasks (important but not blocking)
- 🟢 **Low Priority:** 8 tasks (nice to have)

### Risk Mitigation
- Start with high-risk tasks first (Odoo setup, API access)
- Test each component before moving to next
- Maintain Silver Tier functionality throughout
- Document as we go (don't leave for end)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-18
**Next Review:** After Phase 1 completion
