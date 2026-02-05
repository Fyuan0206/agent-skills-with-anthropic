#!/usr/bin/env python3
"""
Time Series Utilities

Shared functions for time series diagnostic analysis.
Used by diagnose.py and visualize.py.
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import acf, adfuller, kpss


def load_data(filepath, date_col=None, value_col=None):
    """
    Load and prepare time series data from CSV.
    
    Parameters
    ----------
    filepath : str
        Path to CSV file
    date_col : str, optional
        Name of date column (auto-detected if None)
    value_col : str, optional
        Name of value column (auto-detected if None)
    
    Returns
    -------
    series : pd.Series
        Time series with datetime index
    date_col : str
        Detected/used date column name
    value_col : str
        Detected/used value column name
    """
    df = pd.read_csv(filepath)
    
    # Auto-detect date column
    if date_col is None:
        date_cols = df.select_dtypes(include=['object', 'datetime']).columns
        if len(date_cols) == 0:
            raise ValueError("No date column found. Specify with --date-col")
        date_col = date_cols[0]
    
    # Auto-detect value column
    if value_col is None:
        value_cols = df.select_dtypes(include=[np.number]).columns
        if len(value_cols) == 0:
            raise ValueError("No numeric column found. Specify with --value-col")
        value_col = value_cols[0]
    
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    series = df[value_col].dropna()
    
    if len(series) < 10:
        raise ValueError(f"Too few observations ({len(series)}). Need at least 10.")
    
    return series, date_col, value_col


def detect_frequency(series):
    """
    Detect the frequency of the time series.
    
    Parameters
    ----------
    series : pd.Series
        Time series with datetime index
    
    Returns
    -------
    str
        Frequency label: 'hourly', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly', or 'unknown'
    """
    if len(series) < 2:
        return "unknown"
    
    diffs = pd.Series(series.index).diff().dropna()
    if len(diffs) == 0:
        return "unknown"
    
    median_diff = diffs.median()
    
    if median_diff <= pd.Timedelta(hours=2):
        return "hourly"
    elif median_diff <= pd.Timedelta(days=1.5):
        return "daily"
    elif median_diff <= pd.Timedelta(days=8):
        return "weekly"
    elif median_diff <= pd.Timedelta(days=35):
        return "monthly"
    elif median_diff <= pd.Timedelta(days=100):
        return "quarterly"
    else:
        return "yearly"


def test_stationarity(series):
    """
    Run ADF and KPSS tests for stationarity with verified differencing.
    
    Uses both tests for robustness:
    - ADF: null = non-stationary (reject if p <= 0.05)
    - KPSS: null = stationary (reject if p <= 0.05)
    
    Parameters
    ----------
    series : pd.Series
        Time series to test
    
    Returns
    -------
    dict
        Test results including:
        - adf_statistic, adf_p_value, adf_stationary
        - kpss_statistic, kpss_p_value, kpss_stationary
        - differencing_needed (0, 1, or 2)
        - differencing_verified (bool)
        - series_used_for_acf ('original', 'differenced_d1', 'differenced_d2')
    """
    clean_series = series.dropna()
    
    # ADF test
    adf_result = adfuller(clean_series, autolag='AIC')
    adf_stationary = adf_result[1] <= 0.05
    
    # KPSS test
    try:
        kpss_result = kpss(clean_series, regression='c', nlags='auto')
        kpss_stationary = kpss_result[1] > 0.05
        kpss_stat = round(float(kpss_result[0]), 4)
        kpss_p = round(float(kpss_result[1]), 4)
    except Exception:
        kpss_stationary = None
        kpss_stat = None
        kpss_p = None
    
    # Determine differencing needed with verification
    if adf_stationary:
        d = 0
        series_for_acf = "original"
        verified = True
    else:
        # Try first difference
        diff1 = series.diff().dropna()
        adf_diff1 = adfuller(diff1, autolag='AIC')
        
        if adf_diff1[1] <= 0.05:
            d = 1
            series_for_acf = "differenced_d1"
            verified = True
        else:
            # Try second difference and verify
            diff2 = diff1.diff().dropna()
            adf_diff2 = adfuller(diff2, autolag='AIC')
            d = 2
            series_for_acf = "differenced_d2"
            verified = adf_diff2[1] <= 0.05
    
    return {
        'adf_statistic': round(float(adf_result[0]), 4),
        'adf_p_value': round(float(adf_result[1]), 4),
        'adf_stationary': bool(adf_stationary),
        'kpss_statistic': kpss_stat,
        'kpss_p_value': kpss_p,
        'kpss_stationary': bool(kpss_stationary) if kpss_stationary is not None else None,
        'differencing_needed': int(d),
        'differencing_verified': bool(verified),
        'series_used_for_acf': series_for_acf
    }


def get_stationary_series(series, d):
    """
    Return the differenced version of the series.
    
    Parameters
    ----------
    series : pd.Series
        Original time series
    d : int
        Order of differencing (0, 1, or 2)
    
    Returns
    -------
    pd.Series
        Differenced series
    """
    if d == 0:
        return series
    elif d == 1:
        return series.diff().dropna()
    else:
        return series.diff().diff().dropna()


def detect_seasonal_period(series, d=None, freq=None, max_period=None):
    """
    Detect seasonal period from ACF on a stationarized series.

    Key behavior:
    - Uses get_stationary_series(series, d) with proper differencing order
    - Uses frequency-aware candidate periods
    - Only considers positive ACF peaks (negative values aren't seasonal)
    - Snaps to common periods when a strong peak is nearby

    Parameters
    ----------
    series : pd.Series
        Time series to analyze
    d : int or None
        Differencing order (0/1/2). If None, inferred via test_stationarity()
    freq : str or None
        Frequency label: 'hourly', 'daily', 'weekly', 'monthly',
        'quarterly', 'yearly', or 'unknown'. If None, auto-detected.
    max_period : int, optional
        Maximum period to search (default: min(365, n/3))

    Returns
    -------
    int or None
        Detected seasonal period, or None if no reliable seasonality found
    """
    clean_series = series.dropna()
    n = len(clean_series)
    if n < 12:
        return None

    # Infer differencing order if not provided
    if d is None:
        stat = test_stationarity(clean_series)
        d = stat.get("differencing_needed", 0)

    # Stationarize using the correct differencing order
    s = get_stationary_series(clean_series, d).dropna()
    n_s = len(s)
    if n_s < 12:
        return None

    # Infer frequency if not provided
    if freq is None:
        freq = detect_frequency(clean_series)

    # Default max_period based on stationarized length
    if max_period is None:
        max_period = min(365, n_s // 3)
    if max_period < 4:
        return None

    # Frequency-aware common candidates
    candidates_by_freq = {
        "hourly":    [24, 168],              # daily, weekly cycles
        "daily":     [5, 7, 30, 365],        # business-week, week, month, year
        "weekly":    [52],                   # year
        "monthly":   [12],                   # year
        "quarterly": [4],                    # year
        "yearly":    [],                     # usually none
        "unknown":   [4, 5, 7, 12, 24, 30, 52, 60, 90, 168, 365],
    }
    common_periods = candidates_by_freq.get(freq, candidates_by_freq["unknown"])

    acf_vals = acf(s, nlags=max_period, fft=True)

    # 95% confidence bound for ACF under white noise
    conf = 1.96 / np.sqrt(n_s)

    # Require stronger peaks to avoid weak-but-significant detections
    # Floor at 0.15 prevents false positives when n is very large
    strong_threshold = max(conf * 2.0, 0.15)

    # Find positive, significant local maxima
    # Only positive peaks indicate seasonal correlation
    peaks = []
    start_lag = 3
    for i in range(start_lag, len(acf_vals) - 1):
        v = acf_vals[i]
        if v <= 0:
            continue
        is_peak = v > acf_vals[i - 1] and v > acf_vals[i + 1]
        is_significant = v > conf
        if is_peak and is_significant:
            peaks.append((i, v))

    if not peaks:
        return None

    # Snap to common periods if a strong peak is within ±1 lag
    for period in common_periods:
        if period < start_lag or period > max_period:
            continue
        best_near = None
        for lag, v in peaks:
            if abs(lag - period) <= 1 and v >= strong_threshold:
                if best_near is None or v > best_near[1]:
                    best_near = (lag, v)
        if best_near is not None:
            return int(period)

    # Otherwise return strongest peak if strong enough
    best_lag, best_v = max(peaks, key=lambda x: x[1])
    if best_v < strong_threshold:
        return None

    return int(best_lag)


def check_transform_recommendation(series):
    """
    Check if a variance-stabilizing transform is needed using Box-Cox analysis.
    
    Analyzes optimal Box-Cox lambda:
    - λ ≈ 0: recommend log transform
    - λ ≈ 0.5: recommend sqrt transform
    - λ ≈ 1: no transform needed
    
    Parameters
    ----------
    series : pd.Series
        Time series to analyze
    
    Returns
    -------
    dict
        Transform recommendation including:
        - variance_stable (bool)
        - recommendation ('none', 'log', 'sqrt', 'boxcox')
        - boxcox_lambda (float or None)
        - note (str, if applicable)
    """
    clean_series = series.dropna()
    
    # Check for positive values (required for Box-Cox)
    min_val = clean_series.min()
    
    if min_val <= 0:
        # Can't use Box-Cox, fall back to variance ratio heuristic
        return _check_variance_heuristic(clean_series, min_val)
    
    try:
        from scipy.stats import boxcox_normmax
        
        # Find optimal lambda
        lambda_opt = boxcox_normmax(clean_series, method='mle')
        lambda_opt = round(float(lambda_opt), 4)
        
        # Interpret lambda
        if abs(lambda_opt) < 0.1:
            # λ ≈ 0 suggests log transform
            return {
                'variance_stable': False,
                'recommendation': 'log',
                'boxcox_lambda': lambda_opt,
                'note': 'Box-Cox λ ≈ 0 suggests log transform'
            }
        elif abs(lambda_opt - 0.5) < 0.15:
            # λ ≈ 0.5 suggests sqrt transform
            return {
                'variance_stable': False,
                'recommendation': 'sqrt',
                'boxcox_lambda': lambda_opt,
                'note': 'Box-Cox λ ≈ 0.5 suggests sqrt transform'
            }
        elif abs(lambda_opt - 1) < 0.2:
            # λ ≈ 1 means no transform needed
            return {
                'variance_stable': True,
                'recommendation': 'none',
                'boxcox_lambda': lambda_opt,
                'note': 'Box-Cox λ ≈ 1, no transform needed'
            }
        else:
            # Other lambda values
            return {
                'variance_stable': False,
                'recommendation': 'boxcox',
                'boxcox_lambda': lambda_opt,
                'note': f'Box-Cox transform with λ={lambda_opt} recommended'
            }
    
    except Exception as e:
        return {
            'variance_stable': True,
            'recommendation': 'none',
            'boxcox_lambda': None,
            'note': f'Box-Cox analysis failed: {str(e)}'
        }


def _check_variance_heuristic(series, min_val):
    """
    Fallback variance check when Box-Cox cannot be applied.
    Uses mean-variance correlation across chunks.
    """
    n_chunks = min(10, len(series) // 10)
    
    if n_chunks < 3:
        return {
            'variance_stable': True,
            'recommendation': 'none',
            'boxcox_lambda': None,
            'note': 'Insufficient data for variance analysis'
        }
    
    chunk_size = len(series) // n_chunks
    means = []
    variances = []
    
    for i in range(n_chunks):
        chunk = series.iloc[i * chunk_size:(i + 1) * chunk_size]
        means.append(chunk.mean())
        variances.append(chunk.var())
    
    corr, p_value = stats.pearsonr(means, variances)
    
    if corr > 0.5 and p_value < 0.1:
        if min_val <= 0:
            return {
                'variance_stable': False,
                'recommendation': 'shift_then_log',
                'boxcox_lambda': None,
                'mean_var_correlation': round(float(corr), 4),
                'note': f'Data has non-positive values (min={min_val:.2f}). Shift before log transform.'
            }
        else:
            return {
                'variance_stable': False,
                'recommendation': 'log',
                'boxcox_lambda': None,
                'mean_var_correlation': round(float(corr), 4)
            }
    
    return {
        'variance_stable': True,
        'recommendation': 'none',
        'boxcox_lambda': None,
        'mean_var_correlation': round(float(corr), 4)
    }
