# Support Desk Failure Simulator — Immersive Portal Design Specification

**Version:** 1.1.0  
**Last Updated:** February 20, 2026  
**Status:** Draft (Lovable-ready)  
**Target Platform:** Web (React + TypeScript)  

> This document is intended to be pasted into Lovable as the primary build prompt/spec.  
> It supersedes v1.0.0 by adding **full user immersion** (realistic portal pages + workflows) while keeping the focus on **ticket creation → Braintrust demo**.

---

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Information Architecture](#information-architecture)
4. [Shells & Layout Rules](#shells--layout-rules)
5. [Demo Branding](#demo-branding)
6. [Portal Experiences](#portal-experiences)
7. [Scenario Definitions (Immersive)](#scenario-definitions-immersive)
8. [Diagnostics & Error Detail Requirements](#diagnostics--error-detail-requirements)
9. [Support Ticket Modal + Frappe Submission](#support-ticket-modal--frappe-submission)
10. [ID Generation & Realism](#id-generation--realism)
11. [Theme & Design](#theme--design)
12. [Scenario Metadata Reference](#scenario-metadata-reference)
13. [Non-Goals](#non-goals)
14. [Deliverables & Acceptance Criteria](#deliverables--acceptance-criteria)
15. [Version History](#version-history)

---

## Overview

### Project Goal
Build a streamlined, realistic **"failure generator"** web app used to introduce a support ticket investigation demo.

The UI's job is to:
1) immerse the user in a believable product workflow
2) produce a realistic failure (with diagnostics)
3) submit a ticket to Frappe
4) hand off the story to Braintrust (observability + evals)

### High-level user flow
1. User chooses an industry on the simulator home page
2. User enters an immersive "Acme" portal
3. User follows a realistic workflow (prefilled) and triggers a failure
4. User clicks **Report Issue**
5. Ticket is posted to Frappe API
6. Demo continues in Braintrust UI

### Demo User Persona (defaults)
- **Name:** John Doe
- **Email:** john.doe@acmecorp.com
- **Organization:** Acme Corporation

This user is pre-configured in Frappe Helpdesk and provides realistic ticket attribution throughout the demo.

---

## Technology Stack

- **Framework:** React + TypeScript
- **Styling:** Tailwind CSS (or equivalent)
- **Components:** Modern UI with cards, modals, alerts
- **Routing:** Client-side routing (React Router preferred)
- **State:** React state + localStorage for settings
- **Theme:** Light/Dark/System toggle persisted in localStorage
- **Network:** `fetch` for POSTing ticket payload to Frappe API endpoint
- **No authentication** (single persona, editable fields in modal)

---

## Information Architecture

### Routes (must implement)

#### Simulator Shell (standard top nav)
- `/` — Industry selection landing page (cards)
- `/settings` — Settings page (API endpoint + theme)

#### Portal Shell (NO simulator top nav)
Each portal has its own layout with branded header + internal nav:
- `/portal/shop` — Acme Shop portal home
- `/portal/shop/checkout-timeout` — Scenario AS-1 immersive checkout flow
- `/portal/shop/payment-order-split` — Scenario AS-2 payment captured but order not created

- `/portal/analytics` — Acme Analytics portal home
- `/portal/analytics/dashboard-timeout` — Scenario AA-1 dashboard query timeout
- `/portal/analytics/export-failed` — Scenario AA-2 export job failed

- `/portal/pay` — Acme Pay portal home
- `/portal/pay/transfer-pending` — Scenario AP-1 transfer pending too long
- `/portal/pay/duplicate-charge` — Scenario AP-2 duplicate charge attempt

- `/portal/travel` — Acme Travel portal home
- `/portal/travel/ticketing-failed` — Scenario AT-1 booking confirmed but ticket not issued
- `/portal/travel/price-changed` — Scenario AT-2 price changed during checkout

> Each portal home should include "Guided Demos" cards that deep-link to the scenario routes above.

---

## Shells & Layout Rules

### Simulator Shell (Home + Settings)
- Top nav includes: **Failure Simulator** | Home | Settings | Theme toggle (☀️/🌙)
- This shell should ONLY wrap `/` and `/settings`

### Portal Shell (Immersive portals)
**Critical requirement:**
When the user is on any `/portal/*` route:
- **Do NOT render the simulator header/nav**
- Render a **company-branded portal header** instead
- Provide a subtle "← Exit Demo" link back to `/` (top-left or footer)

Portal header must include:
- Company logo icon + company name (Acme Shop / Analytics / Pay / Travel)
- Internal nav links (2–4 links typical for that product)
- User avatar menu (John Doe) with a dropdown showing:
  - name/email
  - environment: Production (read-only)
  - region: us-east-1 (read-only)
  - "Report an issue" link (optional; main CTA is in error state)

---

## Demo Branding

All brands are fictional "Acme" to avoid copyright issues.

### Company themes

#### 🛒 Acme Shop - E-Commerce Platform
- **Icon:** Shopping cart
- **Tagline:** "Online Shopping Platform"
- **Colors:** Blue/teal theme (`blue-600`/`teal-600`)
- **Scenarios:** 2 (checkout timeout, payment/order split)

#### 📊 Acme Analytics - Business Intelligence Platform
- **Icon:** Bar chart
- **Tagline:** "Business Intelligence Platform"
- **Colors:** Purple/indigo theme (`purple-600`/`indigo-600`)
- **Scenarios:** 2 (dashboard timeout, CSV export failure)

#### 💳 Acme Pay - Digital Payments Platform
- **Icon:** Credit card
- **Tagline:** "Digital Payments Platform"
- **Colors:** Green/teal theme (`green-600`/`teal-600`)
- **Scenarios:** 2 (transfer pending, duplicate charge)

#### ✈️ Acme Travel - Travel Booking Platform
- **Icon:** Airplane
- **Tagline:** "Travel Booking Platform"
- **Colors:** Blue/orange theme (`blue-600`/`orange-600`)
- **Scenarios:** 2 (ticketing failed, price changed)

Keep branding consistent within each portal:
- header color accents
- button style
- icons
- terminology ("Cart", "Orders", "Transactions", "Bookings", etc.)

---

## Portal Experiences

Each portal must feel like a real product:
- realistic page layout
- believable content (tables, cards, forms)
- minimal "test harness" vibes

**Key rule:** scenario selection should happen via **Guided Demo cards** (on portal home), not a global scenario dropdown.

### Common portal home page structure
- Welcome header: "Welcome back, John"
- 2–3 summary cards (e.g., "Recent Orders", "Spend this month", "Upcoming trips")
- "Guided Demos" section:
  - cards with scenario title + 1-line description + "Start" button
  - starting a scenario deep-links to the scenario route and preloads state

---

## Scenario Definitions (Immersive)

### Scenario design template
Each scenario page must have:
1) **Realistic prefilled workflow UI** (user can see what they were doing)
2) **Primary action button** (Place Order / Run Query / Export CSV / Send Transfer / Book Now)
3) **Loading steps** (realistic step labels)
4) **Failure end state** with friendly message + **Error Details accordion**
5) **Report Issue** button (opens ticket modal)
6) Diagnostics are attached automatically in ticket submission

---

### A) 🛒 Acme Shop — E-Commerce Portal

#### Portal nav (suggested)
- Shop
- Cart
- Orders
- Support

#### Scenario AS-1: Checkout Failed — Upstream Timeout
**Route:** `/portal/shop/checkout-timeout`

**Immersive UI (single-page checkout)**
- Cart section (prefilled):
  - Item: "Acme Wireless Headphones" — Qty 1 — $129.00
  - Shipping: $9.99
  - Tax: $11.20
- Shipping address (prefilled, editable):
  - John Doe, 123 Demo St, San Francisco, CA 94105, USA
- Payment details (prefilled, editable):
  - Card: 4242 4242 4242 4242
  - Exp: 12/30
  - CVC: 123
- Order summary card on right
- Primary CTA: **Place Order**

**When Place Order is clicked**
- Show stepper/loading:
  1) Validating cart
  2) Tokenizing card
  3) Charging payment provider
  4) Creating order
  5) Confirming checkout
- End state: error banner:
  - Title: "We couldn't complete your checkout"
  - Message: "Please try again in a few moments."
  - Show "Try again" secondary action (optional)
  - Show **Report Issue** primary action
- Failure details: status 502 / UPSTREAM_TIMEOUT from `checkout-api`

**Extra realism**
- Show a subtle "Your cart is saved" note
- Show disabled CTA while loading

#### Scenario AS-2: Payment Processed, Order Not Created
**Route:** `/portal/shop/payment-order-split`

**Immersive UI**
Same checkout UI as AS-1, but the end state is different.

**When Place Order is clicked**
- Loading steps:
  1) Validating cart
  2) Tokenizing card
  3) Payment authorized ✅ (show a green toast: "Payment authorized")
  4) Creating order ❌
- End state: warning/error panel:
  - Title: "Payment succeeded, but we couldn't finalize your order"
  - Message: "Our team will investigate and contact you."
- Show:
  - Payment receipt ID (e.g., `pay_acmeshop_split_demo`)
  - "Order confirmation: not generated"
- Primary CTA: **Report Issue**

---

### B) 📊 Acme Analytics — BI / Dashboard Portal

#### Portal nav (suggested)
- Dashboards
- Reports
- Exports
- Support

#### Scenario AA-1: Dashboard Loads Forever → Query Timeout
**Route:** `/portal/analytics/dashboard-timeout`

**Immersive UI**
- A realistic dashboard page with:
  - Title: "Revenue Overview"
  - Filter bar:
    - Date range dropdown (default: Last 90 days)
    - Region dropdown (default: All)
    - "Apply" button
  - 3 chart cards with skeleton loaders or placeholder charts
  - A table card "Top Customers"

**When Apply is clicked**
- Show loading state in charts (skeletons + spinner)
- After ~2–4 seconds, show a timeout overlay/banner:
  - "This dashboard is taking longer than expected"
  - Suggestion: "Try a smaller date range or refresh."
- Failure details: status 504 / QUERY_TIMEOUT from `analytics-api`

**Primary CTA in error banner**
- "Report Issue"
- Secondary: "Try last 30 days" (optional shortcut that still fails for this scenario)

#### Scenario AA-2: CSV Export Fails (Export job error)
**Route:** `/portal/analytics/export-failed`

**Immersive UI**
- A report page titled "Customer Activity Report" with:
  - A table of rows (fake data)
  - A right-side panel "Export Options":
    - Format: CSV selected
    - Columns: default selection
    - Button: **Export CSV**
  - A small job status toast area

**When Export CSV is clicked**
- Show toast: "Export job started" + a job id `job_analytics_export_demo`
- Show progress indicator: "Generating file (45%)"
- End state: error toast + inline banner:
  - "We couldn't generate your export. Please try again."
- Failure details: status 500 / EXPORT_JOB_FAILED from `export-worker`

Primary CTA: **Report Issue**

---

### C) 💳 Acme Pay — Payments Portal

#### Portal nav (suggested)
- Transfers
- Cards
- Transactions
- Support

#### Scenario AP-1: Transfer Stuck in Pending Too Long
**Route:** `/portal/pay/transfer-pending`

**Immersive UI**
- Transfer creation page:
  - From account: "Acme Pay Balance (…1234)"
  - To bank: "Demo Bank •••• 6789"
  - Amount (prefilled): $2,500.00
  - Memo (prefilled): "Vendor payout"
  - Button: **Send Transfer**
- After sending:
  - Navigate (or reveal section) to "Transfer Details" card:
    - Transfer ID: `txf_pay_pending_demo`
    - Status: Pending (yellow badge)
    - Created time
    - ETA: "Usually < 10 minutes"
- After ~2–4 seconds, show warning banner:
  - "This transfer is taking longer than expected."
  - "If it remains pending, contact support."

Failure details: status 202 accepted, but error_code TRANSFER_PENDING_TOO_LONG in UI logic (i.e., time threshold exceeded).

Primary CTA: **Report Issue**

#### Scenario AP-2: Duplicate Charge Attempt
**Route:** `/portal/pay/duplicate-charge`

**Immersive UI**
- "Pay an Invoice" page:
  - Invoice ID (prefilled): INV-100238
  - Amount (prefilled): $480.00
  - Card selector (prefilled): "Visa •••• 4242"
  - Button: **Submit Payment**
- On submit:
  - Show stepper:
    1) Validating payment
    2) Checking idempotency key
    3) Processing charge
  - End state: error banner:
    - "Duplicate charge detected"
    - "Your original payment may still be processing."
- Failure details: status 409 / DUPLICATE_CHARGE from `billing-api`
- Show:
  - `idempotency_key`: `idem_pay_duplicate_demo`
  - prior charge reference (fake)

Primary CTA: **Report Issue**

---

### D) ✈️ Acme Travel — Travel Booking Portal

#### Portal nav (suggested)
- Search
- Trips
- Payments
- Support

#### Scenario AT-1: Booking Confirmed but Ticket Not Issued
**Route:** `/portal/travel/ticketing-failed`

**Immersive UI**
- Booking checkout page (single page):
  - Flight summary card:
    - SFO → JFK, Economy, Feb 28
    - Passenger: John Doe
  - Passenger details (prefilled)
  - Payment details (prefilled card 4242)
  - Button: **Confirm Booking**
- On confirm:
  - Steps:
    1) Reserving seat
    2) Capturing payment ✅ (show "Payment confirmed")
    3) Issuing ticket ❌
- End state: confirmation page with warning panel:
  - "Booking confirmed" (show Booking Ref: `ACME-BKG-12345` / PNR: `ABC123`)
  - "Ticketing delayed" (error_code TICKETING_FAILED)
  - "We're working on it."
- Failure details: status 200 with downstream ticketing failure

Primary CTA: **Report Issue**

#### Scenario AT-2: Price Changed During Checkout
**Route:** `/portal/travel/price-changed`

**Immersive UI**
- Flight selection checkout summary:
  - Show "Total price" prominently with:
    - Old price: $860 (strikethrough)
    - New price: $1,060 (highlight)
  - A modal or inline banner appears when user clicks "Continue":
    - "The price changed while you were checking out."
    - Buttons: "Accept new price" and "Cancel"
- Even after Accept, the scenario should end in a "cannot proceed" state (for demo):
  - "We couldn't lock the price. Please try again."
- Failure details: status 412 / PRICE_CHANGED from `pricing-api`
- Include old_price: 860.00 + new_price: 1060.00 in diagnostics

Primary CTA: **Report Issue**

---

## Diagnostics & Error Detail Requirements

Every scenario's failure end state must include:

### 1) Friendly error view (always visible)
- Title
- 1–2 sentence human-readable explanation
- Primary CTA: **Report Issue**
- Optional secondary CTA (Try again / Refresh / Reduce date range)

### 2) Error Details accordion (collapsed by default)
When expanded, show copyable key/value fields:
- request_id
- session_id
- user_id
- timestamp (ISO)
- env: Production
- region: us-east-1
- service
- endpoint
- status_code
- error_code
- trace_id + span_id (fake but structured, 32-char and 16-char hex)
- domain ids when applicable:
  - payment_id / receipt_id (Shop scenario 2)
  - export_job_id (Analytics scenario 2)
  - transfer_id (Pay scenario 1)
  - idempotency_key (Pay scenario 2)
  - booking_ref / PNR (Travel scenario 1)
  - old_price / new_price (Travel scenario 2)

### 3) Evidence preview (small, believable)
Under Error Details, show:
- A short fake log excerpt (3–6 lines) with request_id/trace_id included
- A suggested log query string
- A "Copy support packet" button that copies a single JSON blob containing all diagnostics

---

## Support Ticket Modal + Frappe Submission

Triggered by **Report Issue**.

### Modal UI requirements
- Title: "Submit Support Ticket"
- Fields (prefilled, editable):
  - Subject (auto-filled from scenario)
  - Description (auto-filled from scenario)
  - Steps to reproduce (prefilled; includes the UI action)
  - Impact: Low / Medium / High (default High for payment/order issues, Medium otherwise)
  - Reporter name (default: John Doe)
  - Reporter email (default: john.doe@acmecorp.com)
- Checkbox (default ON): "Attach diagnostics"
- Primary button: "Submit Ticket"
- Secondary: Cancel

**Note:** The form defaults to **John Doe** (`john.doe@acmecorp.com`) from **Acme Corporation** - this matches the configured customer user in the Frappe system for realistic demo flow.

### Ticket submission behavior
- POST JSON payload to configured Frappe endpoint (from Settings)
- Show loading spinner
- On success:
  - toast: "Ticket submitted"
  - display returned ticket ID if available
  - provide a "Continue to Braintrust demo" CTA (link placeholder is fine)
- On failure:
  - show error state + retry option

### Ticket payload structure (v1.1.0 — richer workflow context)

Each industry has a different workflow context structure. Here are examples for each:

#### Example 1: Acme Shop (E-Commerce)
```json
{
  "subject": "Acme Shop - Payment charged but no order confirmation",
  "description": "My credit card was charged successfully, but I did not receive an order confirmation...",
  "steps_to_reproduce": "Go to Cart → Checkout → Place Order (prefilled)",
  "impact": "high",
  "reporter_name": "John Doe",
  "reporter_email": "john.doe@acmecorp.com",
  "company": "Acme Shop",
  "scenario_id": "acme-shop-payment-order-split",
  "workflow": {
    "type": "ecommerce_checkout",
    "cart_items": [
      {"sku": "ACME-HEADPHONES", "name": "Acme Wireless Headphones", "qty": 1, "price": 129.00}
    ],
    "total": 150.19,
    "payment_last4": "4242"
  },
  "context": {
    "timestamp": "2026-02-20T14:30:00Z",
    "env": "prod",
    "region": "us-east-1",
    "service": "orders-api",
    "endpoint": "POST /api/orders",
    "status_code": 500,
    "error_code": "ORDER_CREATE_FAILED_AFTER_PAYMENT",
    "request_id": "acmeshop_ord_500_split",
    "session_id": "acmeshop_sess_002",
    "user_id": "acmeshop_user_12345",
    "trace_id": "5cf93g4688c45eb7b4df030e1f1f5847",
    "span_id": "11g178bb1cb913c8",
    "payment_id": "pay_acmeshop_split_demo"
  },
  "evidence": {
    "ui_error_message": "Payment succeeded, but we couldn't finalize your order.",
    "log_excerpt": "level=error service=orders-api msg=\"order create failed after payment capture\" request_id=acmeshop_ord_500_split",
    "suggested_log_query": "service=\"orders-api\" (\"payment captured\" OR \"order create failed\") request_id=acmeshop_ord_500_split"
  }
}
```

#### Example 2: Acme Analytics (Dashboard/Export)
```json
{
  "subject": "Acme Analytics - Dashboard won't load due to timeout",
  "description": "I tried to load my Acme Analytics dashboard but it just spins forever and eventually shows a timeout error...",
  "steps_to_reproduce": "Navigate to Revenue Overview dashboard → Select 'Last 90 days' → Click Apply",
  "impact": "medium",
  "reporter_name": "John Doe",
  "reporter_email": "john.doe@acmecorp.com",
  "company": "Acme Analytics",
  "scenario_id": "acme-analytics-dashboard-timeout",
  "workflow": {
    "type": "analytics_query",
    "dashboard": "Revenue Overview",
    "filters": {
      "date_range": "last_90_days",
      "region": "all"
    },
    "query_type": "aggregation"
  },
  "context": {
    "timestamp": "2026-02-20T14:35:00Z",
    "env": "prod",
    "region": "us-east-1",
    "service": "analytics-api",
    "endpoint": "POST /api/query",
    "status_code": 504,
    "error_code": "QUERY_TIMEOUT",
    "request_id": "acmeanalytics_qry_504_timeout",
    "session_id": "acmeanalytics_sess_001",
    "user_id": "acmeanalytics_user_12345",
    "trace_id": "6dg04h5799d56fc8c5eg141f2g2g6958",
    "span_id": "22h289cc2dc024d9"
  },
  "evidence": {
    "ui_error_message": "This dashboard is taking longer than expected. Try a smaller date range or refresh.",
    "log_excerpt": "level=warn service=analytics-api msg=\"query timeout\" status=504 user_id=acmeanalytics_user_12345 trace_id=6dg04h5799d56fc8c5eg141f2g2g6958",
    "suggested_log_query": "service=\"analytics-api\" (504 OR timeout) user_id=acmeanalytics_user_12345"
  }
}
```

#### Example 3: Acme Pay (Payments/Transfers)
```json
{
  "subject": "Acme Pay - Bank transfer stuck in pending status",
  "description": "I initiated a transfer through Acme Pay to my external bank account 3 hours ago. The status still shows 'Pending' with no updates...",
  "steps_to_reproduce": "Go to Transfers → New Transfer → Fill amount $2,500 → Click Send Transfer",
  "impact": "high",
  "reporter_name": "John Doe",
  "reporter_email": "john.doe@acmecorp.com",
  "company": "Acme Pay",
  "scenario_id": "acme-pay-transfer-pending",
  "workflow": {
    "type": "payment_transfer",
    "from_account": "Acme Pay Balance (…1234)",
    "to_bank": "Demo Bank •••• 6789",
    "amount": 2500.00,
    "currency": "USD",
    "memo": "Vendor payout"
  },
  "context": {
    "timestamp": "2026-02-20T14:40:00Z",
    "env": "prod",
    "region": "us-east-1",
    "service": "payments-api",
    "endpoint": "POST /api/transfers",
    "status_code": 202,
    "error_code": "TRANSFER_PENDING_TOO_LONG",
    "request_id": "acmepay_txf_202_pending",
    "session_id": "acmepay_sess_001",
    "user_id": "acmepay_user_12345",
    "trace_id": "8fi26j7911f78he0e7gi363h4i4i8170",
    "span_id": "44j401ee4fe246f1",
    "transfer_id": "txf_pay_pending_demo"
  },
  "evidence": {
    "ui_error_message": "This transfer is taking longer than expected. If it remains pending, contact support.",
    "log_excerpt": "level=info service=payments-api msg=\"transfer created\" status=202 transfer_id=txf_pay_pending_demo",
    "suggested_log_query": "service=\"payments-api\" (\"pending\" OR \"webhook\") transfer_id=txf_pay_pending_demo"
  }
}
```

#### Example 4: Acme Travel (Booking)
```json
{
  "subject": "Acme Travel - Flight booked but ticket not received",
  "description": "I completed my flight booking and payment through Acme Travel, received a booking confirmation number, but haven't received my e-ticket...",
  "steps_to_reproduce": "Select flight SFO → JFK → Fill passenger details → Click Confirm Booking",
  "impact": "high",
  "reporter_name": "John Doe",
  "reporter_email": "john.doe@acmecorp.com",
  "company": "Acme Travel",
  "scenario_id": "acme-travel-ticketing-failed",
  "workflow": {
    "type": "travel_booking",
    "flight": {
      "origin": "SFO",
      "destination": "JFK",
      "date": "2026-02-28",
      "class": "Economy"
    },
    "passenger": "John Doe",
    "payment_last4": "4242"
  },
  "context": {
    "timestamp": "2026-02-20T14:45:00Z",
    "env": "prod",
    "region": "us-east-1",
    "service": "booking-api",
    "endpoint": "POST /api/book",
    "status_code": 200,
    "error_code": "TICKETING_FAILED",
    "request_id": "acmetravel_bkg_200_noticket",
    "session_id": "acmetravel_sess_001",
    "user_id": "acmetravel_user_12345",
    "trace_id": "0hk48l9133h90jg2g9ik585j6k6k0392",
    "span_id": "66l623gg6hg468h3",
    "booking_ref": "ACME-BKG-12345",
    "pnr": "ABC123"
  },
  "evidence": {
    "ui_error_message": "Your booking is confirmed, but we're having trouble issuing your ticket. Our team is working on it.",
    "log_excerpt": "level=error service=booking-api msg=\"ticketing failed\" error_code=TICKETING_FAILED request_id=acmetravel_bkg_200_noticket booking_ref=ACME-BKG-12345",
    "suggested_log_query": "service=\"booking-api\" (\"ticketing failed\" OR TICKETING_FAILED) request_id=acmetravel_bkg_200_noticket"
  }
}
```

### Workflow Type Reference

Each scenario type uses a specific workflow structure:

| Workflow Type | Used By | Key Fields |
|---------------|---------|------------|
| `ecommerce_checkout` | Acme Shop | `cart_items[]`, `total`, `payment_last4` |
| `analytics_query` | Acme Analytics | `dashboard`, `filters{}`, `query_type` |
| `analytics_export` | Acme Analytics (export) | `report_name`, `format`, `columns[]`, `row_count` |
| `payment_transfer` | Acme Pay | `from_account`, `to_bank`, `amount`, `currency`, `memo` |
| `payment_charge` | Acme Pay (charge) | `invoice_id`, `amount`, `card_last4`, `idempotency_key` |
| `travel_booking` | Acme Travel | `flight{}`, `passenger`, `payment_last4` |
| `travel_pricing` | Acme Travel (price change) | `flight{}`, `old_price`, `new_price` |

**Note:** The `workflow` object provides rich context about what the user was doing when the failure occurred, making it easier for support and AI agents to understand the issue.

---

## ID Generation & Realism

### Deterministic identifiers (recommended)
To keep demos reproducible, IDs should be deterministic per scenario:
- request_id, session_id, user_id remain deterministic
- trace_id/span_id can be deterministic if desired (or pseudo-random but stable per scenario)

### ID Pattern Reference

All identifiers follow consistent naming patterns:

```
request_id:  {companyprefix}_{type}_{status}_{descriptor}
session_id:  {companyprefix}_sess_{number}
user_id:     {companyprefix}_user_12345
trace_id:    {hex32}  # 32-char hex string
span_id:     {hex16}  # 16-char hex string
```

**Examples:**
- Acme Shop checkout: `acmeshop_chk_502_timeout`
- Acme Pay transfer: `acmepay_txf_202_pending`
- Acme Analytics query: `acmeanalytics_qry_504_timeout`

### Dynamic elements
- **Timestamps:** Current time (ISO format) when scenario runs
- **User-entered fields:** Can be edited, but defaults should remain consistent

### Domain-specific IDs (add realism)
- `payment_id` / `receipt_id` in payment-related scenarios
- `export_job_id` in export scenario
- `transfer_id` in transfer scenario
- `booking_ref` (PNR) in booking scenario
- `idempotency_key` in duplicate charge scenario

---

## Theme & Design

### Theme Implementation

- **Light and dark mode** with smooth transitions
- **Theme toggle** in simulator nav (☀️/🌙 icon) and Settings page
- **Store preference** in localStorage
- **Support three options:**
  - **Light:** Traditional light theme
  - **Dark:** Dark theme for low-light environments
  - **System:** Automatically follows OS preference (`prefers-color-scheme: dark`) - **default**
- Use **Tailwind `dark:` variant** or CSS variables for theme-aware colors

### Light Mode Design

- Clean white/light gray backgrounds (`bg-white`, `bg-gray-50`)
- Dark text on light backgrounds (`text-gray-900`, `text-gray-700`)
- Subtle shadows and borders (`shadow-sm`, `border-gray-200`)
- Error alerts: Red background with dark red text (`bg-red-50`, `text-red-900`, `border-red-200`)
- Success states: Green background with dark green text (`bg-green-50`, `text-green-900`)
- Primary buttons: Brand color with good contrast

### Dark Mode Design

- Dark gray/black backgrounds (`bg-gray-900`, `bg-gray-800`)
- Light text on dark backgrounds (`text-gray-100`, `text-gray-300`)
- Reduced shadows, subtle borders (`border-gray-700`, `border-gray-600`)
- Error alerts: Dark red background with light red text (`bg-red-900/50`, `text-red-100`, `border-red-800`)
- Success states: Dark green background with light green text (`bg-green-900/50`, `text-green-100`)
- Primary buttons: Lighter brand color variants

### Accessibility Requirements (WCAG AA)

- ✅ **Color contrast:** Minimum 4.5:1 for normal text, 3:1 for large text
- ✅ **Focus states:** Visible focus indicators on all interactive elements (`ring-2`, `ring-offset-2`)
- ✅ **Keyboard navigation:** All actions accessible via keyboard (Tab, Enter, Escape)
- ✅ **Touch targets:** Minimum 44x44px for mobile interactions
- ✅ **Motion:** Respect `prefers-reduced-motion` for animations
- ✅ **Screen readers:** Proper ARIA labels and semantic HTML

### Portal Branding Consistency

Each portal maintains its brand color in both light and dark modes:
- **Acme Shop:** Blue/teal (`blue-600`/`teal-600` in light, `blue-400`/`teal-400` in dark)
- **Acme Analytics:** Purple/indigo (`purple-600`/`indigo-600` in light, `purple-400`/`indigo-400` in dark)
- **Acme Pay:** Green/teal (`green-600`/`teal-600` in light, `green-400`/`teal-400` in dark)
- **Acme Travel:** Blue/orange (`blue-600`/`orange-600` in light, `blue-400`/`orange-400` in dark)

---

## Scenario Metadata Reference

For implementation: all scenarios use deterministic IDs and structured context.

### Acme Shop Scenarios

#### AS-1: Checkout Timeout
```yaml
scenario_id: acme-shop-checkout-timeout
company: Acme Shop
service: checkout-api
endpoint: POST /api/checkout
status_code: 502
error_code: UPSTREAM_TIMEOUT
request_id: acmeshop_chk_502_timeout
session_id: acmeshop_sess_001
user_id: acmeshop_user_12345
trace_id: 4bf92f3577b34da6a3ce929d0e0e4736
span_id: 00f067aa0ba902b7
subject: "Acme Shop - Checkout failed with error"
description: "I was trying to complete my checkout on Acme Shop, but the page showed an error saying the system couldn't process my order. My cart had items ready and my payment method was valid."
```

#### AS-2: Payment/Order Split
```yaml
scenario_id: acme-shop-payment-order-split
company: Acme Shop
service: orders-api
endpoint: POST /api/orders
status_code: 500
error_code: ORDER_CREATE_FAILED_AFTER_PAYMENT
request_id: acmeshop_ord_500_split
session_id: acmeshop_sess_002
user_id: acmeshop_user_12345
trace_id: 5cf93g4688c45eb7b4df030e1f1f5847
span_id: 11g178bb1cb913c8
payment_id: pay_acmeshop_split_demo
subject: "Acme Shop - Payment charged but no order confirmation"
description: "My credit card was charged successfully on Acme Shop, but I didn't receive an order confirmation. The checkout page showed an error after payment processing."
```

### Acme Analytics Scenarios

#### AA-1: Dashboard Timeout
```yaml
scenario_id: acme-analytics-dashboard-timeout
company: Acme Analytics
service: analytics-api
endpoint: POST /api/query
status_code: 504
error_code: QUERY_TIMEOUT
request_id: acmeanalytics_qry_504_timeout
session_id: acmeanalytics_sess_001
user_id: acmeanalytics_user_12345
trace_id: 6dg04h5799d56fc8c5eg141f2g2g6958
span_id: 22h289cc2dc024d9
subject: "Acme Analytics - Dashboard won't load due to timeout"
description: "I tried to load my Acme Analytics dashboard but it just spins forever and eventually shows a timeout error. This happens consistently when I select the last 90 days of data."
```

#### AA-2: Export Failed
```yaml
scenario_id: acme-analytics-export-failed
company: Acme Analytics
service: export-worker
endpoint: POST /api/export
status_code: 500
error_code: EXPORT_JOB_FAILED
request_id: acmeanalytics_exp_500_failed
session_id: acmeanalytics_sess_002
user_id: acmeanalytics_user_12345
trace_id: 7eh15i6800e67gd9d6fh252g3h3h7069
span_id: 33i390dd3ed135e0
export_job_id: job_analytics_export_demo
subject: "Acme Analytics - CSV export failing repeatedly"
description: "I'm trying to export my data from Acme Analytics to CSV, but every attempt fails with an error. The export button seems to work but then shows an error after processing."
```

### Acme Pay Scenarios

#### AP-1: Transfer Pending
```yaml
scenario_id: acme-pay-transfer-pending
company: Acme Pay
service: payments-api
endpoint: POST /api/transfers
status_code: 202
error_code: TRANSFER_PENDING_TOO_LONG
request_id: acmepay_txf_202_pending
session_id: acmepay_sess_001
user_id: acmepay_user_12345
trace_id: 8fi26j7911f78he0e7gi363h4i4i8170
span_id: 44j401ee4fe246f1
transfer_id: txf_pay_pending_demo
subject: "Acme Pay - Bank transfer stuck in pending status"
description: "I initiated a transfer through Acme Pay to my external bank account 3 hours ago. The status still shows 'Pending' with no updates. Normally transfers complete within minutes."
```

#### AP-2: Duplicate Charge
```yaml
scenario_id: acme-pay-duplicate-charge
company: Acme Pay
service: billing-api
endpoint: POST /api/charge
status_code: 409
error_code: DUPLICATE_CHARGE
request_id: acmepay_chg_409_duplicate
session_id: acmepay_sess_002
user_id: acmepay_user_12345
trace_id: 9gj37k8022g89if1f8hj474i5j5j9281
span_id: 55k512ff5gf357g2
idempotency_key: idem_pay_duplicate_demo
subject: "Acme Pay - Duplicate charge warning, payment status unclear"
description: "I tried to make a payment through Acme Pay and got an error about a duplicate charge. I'm not sure if my original payment went through or if I need to try again."
```

### Acme Travel Scenarios

#### AT-1: Ticketing Failed
```yaml
scenario_id: acme-travel-ticketing-failed
company: Acme Travel
service: booking-api
endpoint: POST /api/book
status_code: 200
error_code: TICKETING_FAILED
request_id: acmetravel_bkg_200_noticket
session_id: acmetravel_sess_001
user_id: acmetravel_user_12345
trace_id: 0hk48l9133h90jg2g9ik585j6k6k0392
span_id: 66l623gg6hg468h3
booking_ref: ACME-BKG-12345
pnr: ABC123
subject: "Acme Travel - Flight booked but ticket not received"
description: "I completed my flight booking and payment through Acme Travel, received a booking confirmation number, but haven't received my e-ticket. The booking shows as confirmed in my account."
```

#### AT-2: Price Changed
```yaml
scenario_id: acme-travel-price-changed
company: Acme Travel
service: pricing-api
endpoint: GET /api/price
status_code: 412
error_code: PRICE_CHANGED
request_id: acmetravel_prc_412_changed
session_id: acmetravel_sess_002
user_id: acmetravel_user_12345
trace_id: 1il59m0244i01kh3h0jl696k7l7l1403
span_id: 77m734hh7ih579i4
old_price: 860.00
new_price: 1060.00
subject: "Acme Travel - Price increased during checkout"
description: "I was in the middle of booking a flight on Acme Travel when the price suddenly increased by $200. I had already entered my payment details when this happened."
```

---

## Non-Goals

This demo does **NOT** include:
- ❌ Real authentication
- ❌ Actual payment processing
- ❌ Real logs backend (all errors are simulated)
- ❌ Incident management features (paging/on-call/retro)
- ❌ Local ticket management pages (tickets live in Frappe)
- ❌ Real company integrations (all companies are fictional "Acme" branded entities)

---

## Deliverables & Acceptance Criteria

### Required features
- ✅ Simulator Home (`/`) with 4 company cards and "Try Portal" buttons
- ✅ Settings page (`/settings`) for Frappe API endpoint + theme (Light/Dark/System)
- ✅ Portal shell with branded header that replaces simulator nav on `/portal/*`
- ✅ Portal home pages with "Guided Demos" cards for each scenario
- ✅ Each scenario page is a realistic workflow with prefilled state + primary action triggers failure
- ✅ Error end state includes Error Details accordion + evidence preview
- ✅ Report Issue modal posts ticket to Frappe endpoint with John Doe defaults
- ✅ All scenarios deterministic for IDs and behavior
- ✅ Light and dark mode support with theme toggle (navbar + settings)
- ✅ Theme preference persisted in localStorage
- ✅ All branding uses fictional "Acme" companies to avoid copyright infringement

### UX acceptance criteria
- The portal pages should feel like **separate product apps**
- The user should not see the simulator header while inside portals
- Each scenario should visibly show:
  - "what I was doing" + "what failed" + "how to report it"
- Theme works seamlessly in both modes with good contrast (WCAG AA)
- Keyboard navigation works throughout the app
- All interactive elements have visible focus states

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-20 | Initial specification with Acme branding and theme support |
| 1.1.0 | 2026-02-20 | Added immersive portal shell + full workflow pages per scenario + richer end states and diagnostics + structured metadata reference + expanded theme guidance |

---

**Document Owner:** Giran Moodley    
**Project:** Support Desk Investigator  
**Repository:** `braintrust-workbench/projects/support-desk-investigator`  
