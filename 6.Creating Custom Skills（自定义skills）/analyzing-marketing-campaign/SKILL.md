---
name: analyzing-marketing-campaign
description: Analyze weekly marketing campaign performance data across channels. Use when analyzing multi-channel digital marketing data to calculate funnel metrics (CTR, CVR) and compare to benchmarks, compute cost and revenue efficiency metrics (ROAS, CPA, Net Profit), or get budget reallocation recommendations  based on performance rules. 
---


# Marketing Campaign Analysis

Automated analysis of multi-channel marketing campaign data.

## Input Requirements

Expects campaign data in CSV format with these columns:

- **date**: Campaign date 
- **campaign_name**: Campaign identifier
- **channel**: Marketing channel
- **segment**: Customer segment
- **impressions**: Ad impressions (empty for Email channel)
- **clicks**: Number of clicks
- **conversions**: Number of conversions
- **spend**: Marketing spend in dollars
- **revenue**: Revenue generated in dollars
- **orders**: Number of orders

## Data Quality Check

1. Check for missing values and empty cells (Email channel won't have impressions)
2. Verify no negative values in numeric columns
3. Flag anomalies (e.g., conversions without clicks)

## Funnel Analysis

Calculate per channel:

- **Click Through Rate (CTR)** = clicks / impressions × 100
- **Conversion Rate (CVR)** = conversions / clicks × 100

Compare to user-provided benchmarks, report difference in percentage points and provide brief interpretation for each channel. If benchmarks are not provided, use these historical values:

| Channel | CTR | CVR |
|---------|-----|-----|
| Facebook_Ads | 2.5% | 3.8% |
| Google_Ads | 5.0% | 4.5% |
| TikTok_Ads | 2.0% | 0.9% |
| Email | 15.0% | 2.1% |

## Efficiency Analysis

Calculate per channel:

- **Return On Ad Spend (ROAS)** = revenue / spend
- **Cost Per Acquisition (CPA)** = spend / conversions
- **Net Profit** = revenue - Total Costs
  - Total Costs = spend + (orders × Shipping Cost) + (revenue × Product Cost %)
  - Unless user specifies different values, use:
    - **Shipping Cost**: $8 per order
    - **Product Cost**: 35% of revenue

Compare to user-provided targets. If not provided, use these defaults:

- **Target ROAS**: 4.0x minimum
- **Max CPA**: $50

## Output Format

Present results as tables with status indicators:

**Funnel Analysis Table:**
| Channel | CTR Actual | CTR Benchmark | CTR Diff | CVR Actual | CVR Benchmark | CVR Diff |

**Efficiency Analysis Table:**
| Channel | ROAS | Status | CPA | Status | Net Profit | Status |

Status indicators:

- ROAS: "[OK] Above" if >= target, "[X] Below" if < target
- CPA: "[OK] Below" if <= max, "[X] Above" if > max
- Net Profit: "[OK] Positive" if > 0, "[X] Negative" if <= 0

Follow each table with brief channel-by-channel interpretation highlighting key insights and recommended actions.

## Budget Reallocation

If user asks about budget reallocation, read `references/budget_reallocation_rules.md` for the complete decision framework including eligibility rules, performance-based actions, and constraints.