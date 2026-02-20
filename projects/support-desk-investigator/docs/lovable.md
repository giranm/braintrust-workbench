# Support Desk Failure Simulator - Design Specification

**Version:** 1.0.0  
**Last Updated:** February 20, 2026  
**Status:** Draft  
**Target Platform:** Web (React + TypeScript)  

---

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Information Architecture](#information-architecture)
4. [Demo Company Branding](#demo-company-branding)
5. [Scenario Definitions](#scenario-definitions)
6. [ID Generation & Realism](#id-generation--realism)
7. [Theme & Design](#theme--design)
8. [Non-Goals](#non-goals)
9. [Deliverables](#deliverables)

---

## Overview

### Project Goal

Build a streamlined **"failure generator"** web application used to introduce a support ticket investigation demo.

The app simulates realistic user-facing product workflows that fail and produces structured diagnostic details. The focus is on quickly demonstrating realistic failures and submitting tickets to Frappe - **the main story happens in the Braintrust UI afterward**.

### User Flow

1. User experiences a simulated failure in one of the Acme company portals
2. User sees a simplified error view with error details
3. User clicks **"Report Issue"** to open a pre-filled ticket form
4. User submits ticket directly to the Frappe API
5. Story continues in Braintrust UI (investigation, evals, observability)

**No local ticket management is needed** - all tickets are handled by Frappe.

### Demo User Persona

The simulator uses a realistic customer user configured in the Frappe system:

- **Name:** John Doe
- **Email:** john.doe@acmecorp.com
- **Organization:** Acme Corporation

This user is pre-configured in Frappe Helpdesk and provides realistic ticket attribution throughout the demo.

---

## Technology Stack

- **Framework:** React + TypeScript
- **Styling:** Tailwind CSS (or equivalent)
- **Components:** Modern UI with cards, modals, alerts
- **Routing:** Client-side routing (React Router or Next.js routes)
- **Theme:** Light and dark mode with theme toggle (persisted in localStorage)
- **Storage:** localStorage for settings (API endpoint, theme preference)
- **Authentication:** None (single business user persona)

---

## Information Architecture

### 1. Home Page - Company Selection

**Route:** `/`

**Layout:**
- Hero header: **"Support Desk Failure Simulator"**
- Tagline: *"Experience realistic product failures and submit support tickets. This introduction feeds into an AI-powered investigation demo in Braintrust."*
- Grid of 4 demo company cards
- Top navigation: Home | Settings | Theme Toggle (☀️/🌙 icon)

**Company Cards:**

| Company | Icon | Tagline | Button |
|---------|------|---------|--------|
| 🛒 Acme Shop | Shopping cart | Online Shopping Platform | Try Portal |
| 📊 Acme Analytics | Bar chart | Business Intelligence Platform | Try Portal |
| 💳 Acme Pay | Credit card | Digital Payments Platform | Try Portal |
| ✈️ Acme Travel | Airplane | Travel Booking Platform | Try Portal |

Each card displays:
- Company name + logo icon
- Brief tagline
- 2 example scenarios
- "Try Portal" button

---

### 2. Company Portal - Workflow Simulator

**Route:** `/company/:companyId`

**Layout:**
- Branded header with company logo + name (e.g., "🛒 Acme Shop")
- Portal description (1-2 lines, e.g., "Online Shopping Platform - Customer Portal")
- **"Test Workflow"** panel with:
  - Scenario selector dropdown (2 scenarios per company)
  - "Run Workflow" button

**When Scenario Runs:**

1. **Loading State:** Show realistic workflow steps
   - Example: "Validating session", "Processing checkout", "Confirming payment"

2. **Outcome:** ALWAYS an ERROR (deterministic for demo purposes)
   - Red error alert with user-friendly error message
   - **"Report Issue"** button (primary CTA)

3. **Error Details Section** (collapsed by default, expandable):
   - `request_id` (deterministic based on scenario)
   - `session_id` (deterministic)
   - `user_id` (deterministic)
   - `timestamp` (current time, ISO format)
   - `service` (e.g., checkout-api)
   - `endpoint` (e.g., POST /api/checkout)
   - `status_code`
   - `error_code`
   - Brief, user-friendly description

**Primary Action:**
- **"Report Issue"** button opens ticket modal

---

### 3. Ticket Creation Modal

**Triggered by:** "Report Issue" button

**Modal Title:** "Submit Support Ticket"

**Form Fields (Pre-filled from scenario):**

| Field | Type | Default | Editable |
|-------|------|---------|----------|
| Subject | Text | Auto-filled | Yes |
| Description | Textarea | Auto-filled | Yes |
| Impact | Dropdown | High | Yes |
| Reporter Name | Text | "John Doe" | Yes |
| Reporter Email | Email | "john.doe@acmecorp.com" | Yes |

**Note:** All error context is automatically attached (not visible in form, but included in submission)

**User Details:** The form defaults to **John Doe** (`john.doe@acmecorp.com`) from **Acme Corporation** - this matches the configured customer user in the Frappe system for realistic demo flow.

**Actions:**
- **"Submit Ticket"** (primary) → POST to Frappe API
- **"Cancel"** (secondary) → Close modal

**On Submit:**
1. Show loading spinner
2. POST ticket payload to Frappe API
3. **On success:** Show success message with ticket ID + "View in Braintrust" CTA
4. **On failure:** Show error message with retry option

**Ticket Payload Structure:**

```json
{
  "subject": "Acme Shop - Checkout failed with error",
  "description": "I was trying to complete my checkout on Acme Shop...",
  "reporter_name": "John Doe",
  "reporter_email": "john.doe@acmecorp.com",
  "impact": "high",
  "company": "Acme Shop",
  "scenario_id": "acme-shop-checkout-timeout",
  "context": {
    "request_id": "acmeshop_chk_502_timeout",
    "session_id": "acmeshop_sess_001",
    "user_id": "acmeshop_user_12345",
    "timestamp": "2026-02-20T14:30:00Z",
    "service": "checkout-api",
    "endpoint": "POST /api/checkout",
    "status_code": 502,
    "error_code": "UPSTREAM_TIMEOUT"
  }
}
```

---

### 4. Settings Page

**Route:** `/settings`

**Sections:**

#### API Configuration
- **Frappe API Endpoint** (required)
  - Input field with placeholder: `http://localhost:8000/webhooks/frappe`
  - **Test Connection** button (validates endpoint is reachable)
- Validation: Warn if API endpoint is not set

#### Appearance
- **Theme Selector:** Light / Dark / System
  - **Light:** Traditional light theme
  - **Dark:** Dark theme for low-light environments
  - **System:** Follows OS preference (prefers-color-scheme)

**Storage:** All settings persisted in localStorage

**Note:** No ticket management pages needed - all tickets are managed in Frappe/Braintrust

---

## Demo Company Branding

To avoid copyright infringement, all companies are **fictional "Acme" branded entities**.

### A) 🛒 Acme Shop - E-Commerce Platform

- **Icon:** Shopping cart
- **Tagline:** "Online Shopping Platform"
- **Colors:** Blue/green theme
- **Scenarios:** 2 (checkout timeout, payment/order split)

### B) 📊 Acme Analytics - Business Intelligence Platform

- **Icon:** Bar chart
- **Tagline:** "Business Intelligence Platform"
- **Colors:** Purple/blue theme
- **Scenarios:** 2 (dashboard timeout, CSV export failure)

### C) 💳 Acme Pay - Digital Payments Platform

- **Icon:** Credit card
- **Tagline:** "Digital Payments Platform"
- **Colors:** Green/teal theme
- **Scenarios:** 2 (transfer pending, duplicate charge)

### D) ✈️ Acme Travel - Travel Booking Platform

- **Icon:** Airplane
- **Tagline:** "Travel Booking Platform"
- **Colors:** Blue/orange theme
- **Scenarios:** 2 (ticketing failed, price changed)

---

## Scenario Definitions

Each scenario is **DETERMINISTIC** and always produces the same IDs and error for consistency in the demo pipeline.

### Scenario Structure

Each scenario includes:
- `scenario_id` (unique identifier)
- `company` (Acme branded)
- `service`, `endpoint`, `status_code`, `error_code`
- `user_message` (friendly error shown to user)
- `workflow_steps` (shown during loading)
- `request_id`, `session_id`, `user_id` (deterministic)
- `subject`, `description` (default ticket content)

---

### A) ACME SHOP - E-Commerce Platform

#### Scenario AS-1: Checkout Failed - Upstream Timeout

```yaml
scenario_id: acme-shop-checkout-timeout
company: Acme Shop
service: checkout-api
endpoint: POST /api/checkout
status_code: 502
error_code: UPSTREAM_TIMEOUT
user_message: "We couldn't complete your checkout. Please try again in a few moments."
workflow_steps:
  - Validating cart
  - Processing payment
  - Creating order
  - Confirming checkout
request_id: acmeshop_chk_502_timeout
session_id: acmeshop_sess_001
user_id: acmeshop_user_12345
subject: "Acme Shop - Checkout failed with error"
description: "I was trying to complete my checkout on Acme Shop, but the page showed an error saying the system couldn't process my order. My cart had items ready and my payment method was valid."
```

#### Scenario AS-2: Payment Successful but Order Not Created

```yaml
scenario_id: acme-shop-payment-order-split
company: Acme Shop
service: orders-api
endpoint: POST /api/orders
status_code: 500
error_code: ORDER_CREATE_FAILED_AFTER_PAYMENT
user_message: "Your payment was processed, but we encountered an issue creating your order. Our team will investigate and contact you."
workflow_steps:
  - Validating cart
  - Processing payment
  - Creating order
  - Confirming checkout
request_id: acmeshop_ord_500_split
session_id: acmeshop_sess_002
user_id: acmeshop_user_12345
subject: "Acme Shop - Payment charged but no order confirmation"
description: "My credit card was charged successfully on Acme Shop, but I didn't receive an order confirmation. The checkout page showed an error after payment processing."
```

---

### B) ACME ANALYTICS - Business Intelligence Platform

#### Scenario AA-1: Dashboard Query Timeout

```yaml
scenario_id: acme-analytics-dashboard-timeout
company: Acme Analytics
service: analytics-api
endpoint: POST /api/query
status_code: 504
error_code: QUERY_TIMEOUT
user_message: "Your dashboard is taking too long to load. Try refreshing or selecting a smaller date range."
workflow_steps:
  - Loading dashboard
  - Fetching data
  - Running analytics
  - Rendering charts
request_id: acmeanalytics_qry_504_timeout
session_id: acmeanalytics_sess_001
user_id: acmeanalytics_user_12345
subject: "Acme Analytics - Dashboard won't load due to timeout"
description: "I tried to load my Acme Analytics dashboard but it just spins forever and eventually shows a timeout error. This happens consistently when I select the last 90 days of data."
```

#### Scenario AA-2: CSV Export Failed

```yaml
scenario_id: acme-analytics-export-failed
company: Acme Analytics
service: export-worker
endpoint: POST /api/export
status_code: 500
error_code: EXPORT_JOB_FAILED
user_message: "We couldn't generate your CSV export. Please try again."
workflow_steps:
  - Preparing data
  - Generating CSV
  - Finalizing export
request_id: acmeanalytics_exp_500_failed
session_id: acmeanalytics_sess_002
user_id: acmeanalytics_user_12345
subject: "Acme Analytics - CSV export failing repeatedly"
description: "I'm trying to export my data from Acme Analytics to CSV, but every attempt fails with an error. The export button seems to work but then shows an error after processing."
```

---

### C) ACME PAY - Digital Payments Platform

#### Scenario AP-1: Transfer Stuck in Pending

```yaml
scenario_id: acme-pay-transfer-pending
company: Acme Pay
service: payments-api
endpoint: POST /api/transfers
status_code: 202
error_code: TRANSFER_PENDING_TOO_LONG
user_message: "Your transfer is still processing. This is taking longer than expected."
workflow_steps:
  - Validating accounts
  - Initiating transfer
  - Processing payment
  - Confirming transfer
request_id: acmepay_txf_202_pending
session_id: acmepay_sess_001
user_id: acmepay_user_12345
subject: "Acme Pay - Bank transfer stuck in pending status"
description: "I initiated a transfer through Acme Pay to my external bank account 3 hours ago. The status still shows 'Pending' with no updates. Normally transfers complete within minutes."
```

#### Scenario AP-2: Duplicate Charge Attempt Blocked

```yaml
scenario_id: acme-pay-duplicate-charge
company: Acme Pay
service: billing-api
endpoint: POST /api/charge
status_code: 409
error_code: DUPLICATE_CHARGE
user_message: "We detected a duplicate charge attempt. Your original payment is being processed."
workflow_steps:
  - Validating payment
  - Checking duplicates
  - Processing charge
request_id: acmepay_chg_409_duplicate
session_id: acmepay_sess_002
user_id: acmepay_user_12345
subject: "Acme Pay - Duplicate charge warning, payment status unclear"
description: "I tried to make a payment through Acme Pay and got an error about a duplicate charge. I'm not sure if my original payment went through or if I need to try again."
```

---

### D) ACME TRAVEL - Travel Booking Platform

#### Scenario AT-1: Booking Confirmed but Ticket Not Issued

```yaml
scenario_id: acme-travel-ticketing-failed
company: Acme Travel
service: booking-api
endpoint: POST /api/book
status_code: 200
error_code: TICKETING_FAILED
user_message: "Your booking is confirmed, but we're having trouble issuing your ticket. Our team is working on it."
workflow_steps:
  - Checking availability
  - Processing payment
  - Confirming booking
  - Issuing ticket
request_id: acmetravel_bkg_200_noticket
session_id: acmetravel_sess_001
user_id: acmetravel_user_12345
subject: "Acme Travel - Flight booked but ticket not received"
description: "I completed my flight booking and payment through Acme Travel, received a booking confirmation number, but haven't received my e-ticket. The booking shows as confirmed in my account."
```

#### Scenario AT-2: Price Changed During Checkout

```yaml
scenario_id: acme-travel-price-changed
company: Acme Travel
service: pricing-api
endpoint: GET /api/price
status_code: 412
error_code: PRICE_CHANGED
user_message: "The price changed while you were checking out. Please review and try again."
workflow_steps:
  - Checking availability
  - Fetching price
  - Processing payment
request_id: acmetravel_prc_412_changed
session_id: acmetravel_sess_002
user_id: acmetravel_user_12345
subject: "Acme Travel - Price increased during checkout"
description: "I was in the middle of booking a flight on Acme Travel when the price suddenly increased by $200. I had already entered my payment details when this happened."
```

---

## ID Generation & Realism

### Deterministic IDs

All IDs are **DETERMINISTIC** per scenario for automation consistency:

- Same scenario always generates same IDs
- IDs follow pattern: `{companyprefix}_{type}_{status}_{descriptor}`
- Examples:
  - Acme Shop checkout timeout → `acmeshop_chk_502_timeout`
  - Acme Pay transfer pending → `acmepay_txf_202_pending`
  - Acme Analytics query timeout → `acmeanalytics_qry_504_timeout`

### ID Pattern Reference

```
request_id:  {company}_{type}_{status}_{descriptor}
session_id:  {company}_sess_{number}
user_id:     {company}_user_12345
```

### Dynamic Elements

- **Timestamps:** Current time (ISO format) when scenario runs
- **All other fields:** Static and deterministic

### UI Patterns

- Loading spinners with realistic workflow steps
- Error alerts (red, user-friendly)
- Clean cards and modals
- Maintain Acme branding throughout (logos, colors, consistent visual identity)
- Simple and polished - this is a quick intro, not a full application

---

## Theme & Design

### Theme Implementation

- **Light and dark mode** with smooth transitions
- **Theme toggle** in top nav (☀️/🌙 icon) and Settings page
- **Store preference** in localStorage
- **Support "System" option** that follows OS preference (`prefers-color-scheme`)
- Use **Tailwind `dark:` variant** or CSS variables for theme-aware colors

### Light Mode

- Clean white/light gray backgrounds
- Dark text on light backgrounds
- Subtle shadows and borders
- Error alerts: Red background with dark red text

### Dark Mode

- Dark gray/black backgrounds
- Light text on dark backgrounds
- Reduced shadows, subtle borders
- Error alerts: Dark red background with light red text

### Design Principles (Both Modes)

- ✅ High contrast for readability
- ✅ Consistent spacing and layout
- ✅ Clear visual hierarchy
- ✅ Accessible color combinations (**WCAG AA compliant**)

---

## Non-Goals

This project explicitly **does NOT include:**

- ❌ Real authentication
- ❌ Actual payment processing
- ❌ Real logs backend (all errors are simulated)
- ❌ Local ticket management (Frappe handles all ticketing)
- ❌ Real company integrations (all companies are fictional "Acme" branded entities)

---

## Deliverables

### Required Features

- ✅ Home page with 4 Acme-branded company cards (Shop, Analytics, Pay, Travel)
- ✅ Each company has consistent branding: logo icon, name, colors, tagline
- ✅ Each company portal with scenario selector and runner
- ✅ Scenarios always produce deterministic errors with realistic workflow simulation
- ✅ Error details shown in a simple, collapsible section
- ✅ "Report Issue" modal with pre-filled ticket form
- ✅ Ticket submission POSTs to Frappe API endpoint (configured in Settings)
- ✅ Settings page with API endpoint configuration and theme selector
- ✅ Light and dark mode support with theme toggle (navbar + settings)
- ✅ Theme preference persisted in localStorage
- ✅ App is clean, modern, and serves as a quick 2-3 minute intro to the demo
- ✅ No local ticket management (all tickets live in Frappe)
- ✅ All branding uses fictional "Acme" companies to avoid copyright infringement

### Acceptance Criteria

1. **Functional:** All 8 scenarios (2 per company) work deterministically
2. **UI/UX:** Smooth, polished, demo-ready interface
3. **Theme:** Both light and dark modes work seamlessly
4. **Integration:** Successfully POSTs tickets to Frappe API
5. **Performance:** Fast loading, responsive on all devices
6. **Accessibility:** WCAG AA compliant, keyboard navigable

### Scope Notes

- This is a **SIMPLIFIED demo introduction** - most of the story happens in Braintrust UI
- No developer diagnostics, telemetry tabs, or complex configuration
- Single user persona (business user)
- All scenarios are deterministic for automation reliability
- **Focus:** Get to ticket submission quickly, then move to Braintrust

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-20 | Initial specification with Acme branding and theme support |

---

**Document Owner:** Giran Moodley    
**Project:** Support Desk Investigator  
**Repository:** `braintrust-workbench/projects/support-desk-investigator`  
