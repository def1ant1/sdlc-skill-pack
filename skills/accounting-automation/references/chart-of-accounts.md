# Chart of Accounts

## GL Account Structure

Accounts follow the format: `[Class][Department][Sub]` — e.g., `6100-ENG-001`

### Account Classes

| Class | Range | Type |
|---|---|---|
| 1xxx | 1000–1999 | Assets |
| 2xxx | 2000–2999 | Liabilities |
| 3xxx | 3000–3999 | Equity |
| 4xxx | 4000–4999 | Revenue |
| 5xxx | 5000–5999 | Cost of Goods Sold |
| 6xxx | 6000–6999 | Operating Expenses |
| 7xxx | 7000–7999 | Other Income/Expense |

---

## Revenue Accounts (4xxx)

| Code | Description | Notes |
|---|---|---|
| 4100 | Subscription Revenue — Monthly | MRR |
| 4110 | Subscription Revenue — Annual | Amortized monthly |
| 4200 | Professional Services | Implementation, consulting |
| 4300 | Usage-Based Revenue | API calls, compute |
| 4400 | Partner Revenue | Reseller, referral |
| 4900 | Other Revenue | Misc; requires memo |

---

## Cost of Goods Sold (5xxx)

| Code | Description | Notes |
|---|---|---|
| 5100 | Cloud Infrastructure | AWS, GCP, Azure |
| 5110 | AI Compute (API) | Anthropic, OpenAI API costs |
| 5120 | AI Compute (Local) | DGX Spark amortization |
| 5200 | Third-party Software (COGS) | Tools directly serving customers |
| 5300 | Professional Services Delivery | Contractor costs for delivery |

---

## Operating Expenses (6xxx)

### Personnel (61xx)

| Code | Description |
|---|---|
| 6100 | Salaries — Engineering |
| 6110 | Salaries — Product |
| 6120 | Salaries — Sales & Marketing |
| 6130 | Salaries — G&A |
| 6150 | Benefits (all departments) |
| 6160 | Equity Compensation (non-cash) |
| 6170 | Contractors and Consultants |
| 6180 | Recruiting |

### Technology (62xx)

| Code | Description |
|---|---|
| 6200 | SaaS — Engineering Tools |
| 6210 | SaaS — Business Tools |
| 6220 | SaaS — Security & Compliance |
| 6230 | Hardware & Equipment |

### Marketing (63xx)

| Code | Description |
|---|---|
| 6300 | Digital Advertising |
| 6310 | Content & Events |
| 6320 | Brand & Design |

### G&A (64xx)

| Code | Description |
|---|---|
| 6400 | Legal & Professional Services |
| 6410 | Accounting & Finance |
| 6420 | Office & Facilities |
| 6430 | Travel & Entertainment |
| 6440 | Insurance |
| 6450 | D&O Insurance |

---

## Categorization Rules

| Vendor Type | Default GL Code | Override Condition |
|---|---|---|
| Cloud provider (AWS, GCP) | 5100 | If for internal tools → 6200 |
| Anthropic / OpenAI API | 5110 | Always COGS |
| SaaS productivity tools | 6210 | If customer-facing → 5200 |
| Legal (external counsel) | 6400 | If for customer contract → 5300 |
| Contractor (engineering) | 6170 | If customer project → 5300 |
| Travel | 6430 | Must include business purpose |

---

## Ambiguous Category Handling

When AI categorization confidence < 80%:
1. Route to finance team for manual coding
2. Include vendor name, amount, and best candidate codes
3. Finance must respond within 2 business days
4. Log manual override in transaction record