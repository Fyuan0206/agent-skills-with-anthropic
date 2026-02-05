---
name: analyzing-time-series
description: Comprehensive diagnostic analysis of time series data. Use when users provide CSV time series data and want to understand its characteristics before forecasting - stationarity, seasonality, trend, forecastability, and transform recommendations.
---

# Time Series Diagnostics

Comprehensive diagnostic toolkit to analyze time series data characteristics before forecasting.

## Input Format

The input CSV file should have two columns:
- **Date column** - Timestamps or dates (e.g., `date`, `timestamp`, `time`)
- **Value column** - Numeric values to analyze (e.g., `value`, `sales`, `temperature`)


## Workflow

**Step 1: Run diagnostics**

```bash
python scripts/diagnose.py data.csv --output-dir results/
```

This runs all statistical tests and analyses. Outputs `diagnostics.json` with all metrics and `summary.txt` with human-readable findings. Column names are auto-detected, or can be specified with `--date-col` and `--value-col` options.

**Step 2: Generate plots (optional)**

```bash
python scripts/visualize.py data.csv --output-dir results/
```

Creates diagnostic plots in `results/plots/` for visual inspection. Run after `diagnose.py` to ensure ACF/PACF plots are synchronized with stationarity results. Column names are auto-detected, or can be specified with `--date-col` and `--value-col` options.

**Step 3: Report to user**

Summarize findings from `summary.txt` and present relevant plots. See `references/interpretation.md` for guidance on:
- Is the data forecastable?
- Is it stationary? How much differencing is needed?
- Is there seasonality? What period?
- Is there a trend? What direction?
- Is a transform needed?

## Script Options

Both scripts accept:
- `--date-col NAME` - Date column (auto-detected if omitted)
- `--value-col NAME` - Value column (auto-detected if omitted)
- `--output-dir PATH` - Output directory (default: `diagnostics/`)
- `--seasonal-period N` - Seasonal period (auto-detected if omitted)

## Output Files

```
results/
├── diagnostics.json       # All test results and statistics
├── summary.txt            # Human-readable findings
├── diagnostics_state.json # Internal state for plot synchronization
└── plots/
    ├── timeseries.png
    ├── histogram.png
    ├── rolling_stats.png
    ├── box_by_dayofweek.png  # By day of week (if applicable)
    ├── box_by_month.png      # By month (if applicable)
    ├── box_by_quarter.png    # By quarter (if applicable)
    ├── acf_pacf.png
    ├── decomposition.png
    └── lag_scatter.png
```

## References

See `references/interpretation.md` for:
- Statistical test thresholds and interpretation
- Seasonal period guidelines by data frequency
- Transform recommendations

## Dependencies

`pandas`, `numpy`, `matplotlib`, `statsmodels`, `scipy`