# Budget Reallocation Rules

## Table of Contents
- [Rule 0: Minimum Data Eligibility](#rule-0-minimum-data-eligibility)
- [Rule 1: Channel Classification](#rule-1-channel-classification)
- [Rule 2: Calculate Budget Changes](#rule-2-calculate-budget-changes)
- [Multi-Week Adjustments](#multi-week-adjustments)
- [Decision Matrix](#decision-matrix)
- [Required Output Format](#required-output-format)

---

## Rule 0: Minimum Data Eligibility

A channel is eligible for budget changes only if it has **>=50 conversions** in the analysis period.

Channels below threshold: classify as **INSUFFICIENT_DATA -> MAINTAIN**.

---

## Rule 1: Channel Classification

Classify each channel into exactly one category. Apply rules **in order** (first match wins):

### PAUSE (100% decrease)
Any condition triggers:
- User states channel has been negative for 3+ consecutive weeks
- User states no improvement after optimization efforts for 3+ weeks

### DECREASE_HEAVY (45% decrease)
Any condition triggers:
- ROAS < 50% of target AND Net Profit <= 0
- CPA > 150% of max AND Net Profit <= 0
- All three fail: ROAS < 100% AND CPA > 100% AND Net Profit <= 0
- User states channel has been negative for 2 consecutive weeks

### INCREASE (use user-specified cap, default 15%)
All conditions must be met:
- ROAS >= 115% of target
- CPA <= 80% of max
- Net Profit > 0

### DECREASE_LIGHT (25% decrease)
Any condition triggers (if not already classified):
- ROAS < 80% of target
- CPA > 120% of max

### MAINTAIN (0% change)
Does not meet any above criteria.

---

## Rule 2: Calculate Budget Changes

### Step 1: Calculate Decreases (apply in full)
```
DECREASE_HEAVY: decrease = current_spend * 0.45
DECREASE_LIGHT: decrease = current_spend * 0.25
```

### Step 2: Calculate Freed Budget
```
freed_budget = sum(all decreases)
```

### Step 3: Allocate to INCREASE Channels
Distribute proportionally by Net Profit:
```
weight = channel_net_profit / sum(net_profit of all INCREASE channels)
proposed_increase = freed_budget * weight
```

### Step 4: Apply Caps

**Per-channel cap:** Use user-specified value if provided, otherwise default to 15%.
```
max_increase = current_spend * increase_cap
final_increase = min(proposed_increase, max_increase)
```

**User reallocation limit** (if specified):
- Applies to **increases only**, not decreases
- If sum(proposed_increases) > user_limit: scale increases proportionally
```
scale_factor = user_limit / sum(proposed_increases)
final_increase = proposed_increase * scale_factor
```

### Step 5: Calculate Unallocated Savings
```
unallocated = freed_budget - sum(final_increases)
```
Report as "available for reserve."

---

## Multi-Week Adjustments

If user provides historical context, adjust the classification:

| User Says | Adjustment |
|-----------|------------|
| "Channel X has been negative for 2+ weeks" | Upgrade to DECREASE_HEAVY or PAUSE |
| "Channel X has been negative for 3+ weeks" | PAUSE (set budget to $0) |
| "We changed Channel X's budget last week" | Override to MAINTAIN (allow 5-7 days to stabilize) |
| "Channel X improved from last week" | Can upgrade DECREASE_LIGHT to MAINTAIN |

Without historical context, use single-week classification only.

---

## Decision Matrix

| Condition | Classification | Change |
|-----------|----------------|--------|
| Negative 3+ weeks (user-stated) | PAUSE | -100% |
| No improvement 3+ weeks (user-stated) | PAUSE | -100% |
| Negative 2 weeks (user-stated) | DECREASE_HEAVY | -45% |
| ROAS < 50% AND Net Profit <= 0 | DECREASE_HEAVY | -45% |
| CPA > 150% AND Net Profit <= 0 | DECREASE_HEAVY | -45% |
| ROAS < 100% AND CPA > 100% AND Net Profit <= 0 | DECREASE_HEAVY | -45% |
| ROAS >= 115% AND CPA <= 80% AND Net Profit > 0 | INCREASE | +15% cap |
| ROAS < 80% | DECREASE_LIGHT | -25% |
| CPA > 120% | DECREASE_LIGHT | -25% |
| All other cases | MAINTAIN | 0% |

---

## Required Output Format

### 1. Classification Table
| Channel | ROAS | % of Target | CPA | % of Max | Net Profit | Classification |

### 2. Calculation Steps
Show: freed budget, allocation weights, proposed vs. capped increases, unallocated savings.

### 3. Final Reallocation Table
| Channel | Current | Change | New Budget | Classification |

Include "Reserve" row if unallocated > 0.

