# Quick Reference: Interpreting Time Series Diagnostics

## Stationarity Tests

### ADF (Augmented Dickey-Fuller)

| p-value | Interpretation |
|---------|----------------|
| ≤ 0.01  | Strong evidence of stationarity |
| ≤ 0.05  | Stationary (reject null) |
| > 0.05  | Non-stationary (fail to reject) |

**Null hypothesis:** Series has a unit root (non-stationary)

### KPSS (Kwiatkowski-Phillips-Schmidt-Shin)

| p-value | Interpretation |
|---------|----------------|
| > 0.10  | Stationary (fail to reject) |
| > 0.05  | Likely stationary |
| ≤ 0.05  | Non-stationary (reject null) |

**Null hypothesis:** Series is stationary (opposite of ADF)

### Combined Interpretation

| ADF | KPSS | Conclusion |
|-----|------|------------|
| Stationary | Stationary | Confirmed stationary |
| Non-stationary | Non-stationary | Confirmed non-stationary |
| Stationary | Non-stationary | Trend-stationary (difference or detrend) |
| Non-stationary | Stationary | Difference-stationary (may need differencing) |

### Differencing (d)

| d value | Meaning | Common causes |
|---------|---------|---------------|
| 0 | Already stationary | Stationary process |
| 1 | First difference needed | Trend, random walk |
| 2 | Second difference needed | Quadratic trend, I(2) process |

**Warning:** If d=2 and still non-stationary, consider:
- Structural breaks in the data
- Non-linear trends
- Regime changes

---

## Seasonality

### Seasonal Strength

| Strength | Interpretation |
|----------|----------------|
| 0.0 - 0.1 | No meaningful seasonality |
| 0.1 - 0.3 | Weak seasonality |
| 0.3 - 0.6 | Moderate seasonality |
| 0.6 - 0.9 | Strong seasonality |
| > 0.9 | Very strong seasonality |

### Common Seasonal Periods

| Data Frequency | Typical Period | Meaning |
|----------------|----------------|---------|
| Hourly | 24 | Daily cycle |
| Hourly | 168 | Weekly cycle (24 × 7) |
| Daily | 7 | Weekly cycle |
| Daily | 365 | Yearly cycle |
| Weekly | 52 | Yearly cycle |
| Monthly | 12 | Yearly cycle |
| Quarterly | 4 | Yearly cycle |

---

## Trend

### Trend Strength

| Strength | Interpretation |
|----------|----------------|
| 0.0 - 0.1 | No meaningful trend |
| 0.1 - 0.3 | Weak trend |
| 0.3 - 0.6 | Moderate trend |
| 0.6 - 0.9 | Strong trend |
| > 0.9 | Dominant trend |

### Direction

| Direction | Meaning |
|-----------|---------|
| increasing | Upward long-term movement |
| decreasing | Downward long-term movement |
| flat | No significant directional movement |

---

## Forecastability (Ljung-Box Test)

### Interpretation

| p-value | Interpretation |
|---------|----------------|
| ≤ 0.01  | Strong autocorrelation - highly forecastable |
| ≤ 0.05  | Significant autocorrelation - forecastable |
| > 0.05  | No significant autocorrelation - may be white noise |
| > 0.10  | Likely white noise - not forecastable |

**Null hypothesis:** No autocorrelation (white noise)

### What This Means

- **Forecastable:** Past values contain information about future values
- **Not forecastable (white noise):** Future values are random, cannot be predicted from history

---

## Transform Recommendations

### Box-Cox Lambda Interpretation

| Lambda (λ) | Recommended Transform |
|------------|----------------------|
| λ ≈ -1 | Inverse (1/y) |
| λ ≈ -0.5 | Inverse square root (1/√y) |
| λ ≈ 0 | Log transform (log y) |
| λ ≈ 0.5 | Square root (√y) |
| λ ≈ 1 | No transform needed |
| λ ≈ 2 | Square (y²) |

### When to Transform

| Symptom | Likely Transform |
|---------|------------------|
| Variance increases with level | Log or sqrt |
| Right-skewed distribution | Log |
| Multiplicative seasonality | Log |
| Heteroscedastic residuals | Box-Cox |

### Requirements

- **Log transform:** All values must be positive (y > 0)
- **Box-Cox:** All values must be positive
- **Shift:** If data has zeros or negatives, add constant first

---

## ACF/PACF Interpretation

### Reading the Plots

| Pattern | ACF | PACF | Suggested Model |
|---------|-----|------|-----------------|
| AR(p) | Gradual decay | Cuts off after lag p | AR(p) |
| MA(q) | Cuts off after lag q | Gradual decay | MA(q) |
| ARMA | Gradual decay | Gradual decay | ARMA(p,q) |
| Seasonal | Spikes at seasonal lags | Spikes at seasonal lags | SARIMA |

### Confidence Bands

- Values outside the shaded bands are statistically significant
- Default bands are 95% confidence (±1.96/√n)
- Expect ~5% of lags to exceed bands by chance

### Common Patterns

**AR(1):** PACF spike at lag 1, ACF exponential decay
**MA(1):** ACF spike at lag 1, PACF exponential decay
**Seasonal (period=12):** Spikes at lags 12, 24, 36...

---

## Model Selection Guidelines

### Based on Diagnostics

| Condition | Recommended Approach |
|-----------|---------------------|
| Stationary, no seasonality | ARMA |
| Non-stationary, no seasonality | ARIMA(p,d,q) |
| Stationary, seasonal | SARIMA with D=0 |
| Non-stationary, seasonal | SARIMA(p,d,q)(P,D,Q)m |
| Strong trend, weak seasonality | Exponential smoothing (Holt) |
| Strong trend, strong seasonality | Holt-Winters or SARIMA |
| Not forecastable | Consider external regressors or accept limitations |

### Rule of Thumb for ARIMA Orders

- Start with d from stationarity tests
- Use PACF cutoff for p (AR order)
- Use ACF cutoff for q (MA order)
- Keep p + q ≤ 4 for parsimony
- Use AIC/BIC for final selection

---

## Data Quality Thresholds

| Metric | Good | Acceptable | Concerning |
|--------|------|------------|------------|
| Missing % | < 1% | 1-5% | > 5% |
| Min observations | > 100 | 50-100 | < 50 |
| Seasonal cycles | > 3 | 2-3 | < 2 |

---

## References

- Hyndman, R.J., & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice*, 3rd edition
- Box, G.E.P., Jenkins, G.M., Reinsel, G.C., & Ljung, G.M. (2015). *Time Series Analysis*, 5th edition
- Cleveland, R.B., et al. (1990). STL: A Seasonal-Trend Decomposition Procedure Based on Loess
