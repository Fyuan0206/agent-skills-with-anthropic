#!/usr/bin/env python3
"""
Time Series Diagnostic Analysis

Runs comprehensive statistical tests and analysis on time series data.
Output: diagnostics.json, summary.txt, diagnostics_state.json
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.seasonal import STL

from ts_utils import (
    load_data,
    detect_frequency,
    test_stationarity,
    get_stationary_series,
    detect_seasonal_period,
    check_transform_recommendation
)


def analyze_data_quality(series):
    """Analyze data quality metrics."""
    freq = detect_frequency(series)
    
    # Map frequency to pandas offset
    freq_map = {
        'hourly': 'H',
        'daily': 'D',
        'weekly': 'W',
        'monthly': 'MS',
        'quarterly': 'QS',
        'yearly': 'YS'
    }
    
    try:
        offset = freq_map.get(freq, 'D')
        expected_range = pd.date_range(series.index.min(), series.index.max(), freq=offset)
        total_expected = len(expected_range)
        missing = max(0, total_expected - len(series))
        missing_pct = round(missing / total_expected * 100, 2) if total_expected > 0 else 0.0
    except Exception:
        missing = 0
        missing_pct = 0.0
    
    return {
        'n_observations': int(len(series)),
        'date_start': str(series.index.min().date()),
        'date_end': str(series.index.max().date()),
        'frequency': freq,
        'missing_values': int(missing),
        'missing_pct': missing_pct
    }


def analyze_distribution(series):
    """Analyze distribution statistics."""
    return {
        'mean': round(float(series.mean()), 4),
        'median': round(float(series.median()), 4),
        'std': round(float(series.std()), 4),
        'min': round(float(series.min()), 4),
        'max': round(float(series.max()), 4),
        'skewness': round(float(series.skew()), 4),
        'kurtosis': round(float(series.kurtosis()), 4)
    }


def analyze_seasonality(series, seasonal_period=None, d=None, freq=None):
    """Analyze seasonality using STL decomposition."""
    if seasonal_period is None:
        seasonal_period = detect_seasonal_period(series, d=d, freq=freq)
    
    if seasonal_period is None or seasonal_period < 2:
        return {
            'is_seasonal': False,
            'period': None,
            'strength': 0.0
        }
    
    # Need at least 2 full periods for STL
    if len(series) < seasonal_period * 2:
        return {
            'is_seasonal': False,
            'period': int(seasonal_period),
            'strength': 0.0,
            'note': 'Insufficient data for STL decomposition'
        }
    
    try:
        stl = STL(series, period=seasonal_period, robust=True)
        result = stl.fit()
        
        # Seasonal strength: 1 - Var(residual) / Var(seasonal + residual)
        # Equivalent to: 1 - Var(residual) / Var(detrended)
        var_resid = np.var(result.resid)
        var_detrended = np.var(result.seasonal + result.resid)
        
        if var_detrended > 0:
            strength = max(0, 1 - var_resid / var_detrended)
        else:
            strength = 0.0
        
        is_seasonal = strength > 0.1
        
        return {
            'is_seasonal': bool(is_seasonal),
            'period': int(seasonal_period),
            'strength': round(float(strength), 4)
        }
    except Exception as e:
        return {
            'is_seasonal': False,
            'period': int(seasonal_period) if seasonal_period else None,
            'strength': 0.0,
            'error': str(e)
        }


def analyze_trend(series, seasonal_period=None, d=None, freq=None):
    """Analyze trend using STL decomposition with corrected threshold."""
    if seasonal_period is None:
        seasonal_period = detect_seasonal_period(series, d=d, freq=freq)
    
    if seasonal_period is None:
        seasonal_period = max(2, len(series) // 10)
    
    if len(series) < seasonal_period * 2:
        # Fallback: simple linear regression
        x = np.arange(len(series))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, series.values)
        
        # Normalize slope by series std (per-step change)
        normalized_slope = slope / series.std() if series.std() > 0 else 0
        
        if normalized_slope > 0.01:
            direction = "increasing"
        elif normalized_slope < -0.01:
            direction = "decreasing"
        else:
            direction = "flat"
        
        return {
            'has_trend': abs(r_value) > 0.3,
            'direction': direction,
            'strength': round(float(r_value ** 2), 4),
            'slope_normalized': round(float(normalized_slope), 6)
        }
    
    try:
        stl = STL(series, period=seasonal_period, robust=True)
        result = stl.fit()
        
        # Trend strength: 1 - Var(residual) / Var(trend + residual)
        var_resid = np.var(result.resid)
        var_deseasonalized = np.var(result.trend + result.resid)
        
        if var_deseasonalized > 0:
            strength = max(0, 1 - var_resid / var_deseasonalized)
        else:
            strength = 0.0
        
        # Determine direction using normalized slope
        trend_vals = result.trend.values
        x = np.arange(len(trend_vals))
        slope, _, _, _, _ = stats.linregress(x, trend_vals)
        
        # Normalize by series std (per-step change)
        normalized_slope = slope / series.std() if series.std() > 0 else 0
        
        if normalized_slope > 0.005:
            direction = "increasing"
        elif normalized_slope < -0.005:
            direction = "decreasing"
        else:
            direction = "flat"
        
        return {
            'has_trend': bool(strength > 0.1),
            'direction': direction,
            'strength': round(float(strength), 4),
            'slope_normalized': round(float(normalized_slope), 6)
        }
    except Exception as e:
        return {
            'has_trend': False,
            'direction': 'unknown',
            'strength': 0.0,
            'error': str(e)
        }


def analyze_autocorrelation(series, d=0):
    """Analyze ACF and PACF on stationary series."""
    stationary_series = get_stationary_series(series, d)
    
    max_lags = min(40, len(stationary_series) // 2 - 1)
    if max_lags < 2:
        return {
            'significant_acf_lags': [],
            'significant_pacf_lags': [],
            'note': 'Insufficient data for autocorrelation analysis'
        }
    
    acf_vals = acf(stationary_series, nlags=max_lags, fft=False)
    pacf_vals = pacf(stationary_series, nlags=max_lags)
    conf = 1.96 / np.sqrt(len(stationary_series))
    
    # Find significant lags (excluding lag 0)
    sig_acf = [int(i) for i in range(1, len(acf_vals)) if abs(acf_vals[i]) > conf]
    sig_pacf = [int(i) for i in range(1, len(pacf_vals)) if abs(pacf_vals[i]) > conf]
    
    return {
        'significant_acf_lags': sig_acf[:10],
        'significant_pacf_lags': sig_pacf[:10],
        'confidence_threshold': round(float(conf), 4)
    }


def test_forecastability(series, d=0):
    """
    Test if series is white noise using Ljung-Box at multiple lags.
    
    Tests at lags 10, 20, and n/5 for robustness.
    """
    stationary_series = get_stationary_series(series, d)
    n = len(stationary_series)
    
    if n < 20:
        return {
            'ljung_box_results': None,
            'is_white_noise': True,
            'forecastable': False,
            'note': 'Insufficient data for Ljung-Box test'
        }
    
    # Test at multiple lags
    test_lags = sorted(set([
        min(10, n // 2 - 1),
        min(20, n // 2 - 1),
        min(n // 5, n // 2 - 1)
    ]))
    test_lags = [lag for lag in test_lags if lag >= 1]
    
    if not test_lags:
        return {
            'ljung_box_results': None,
            'is_white_noise': True,
            'forecastable': False,
            'note': 'Insufficient data for Ljung-Box test'
        }
    
    try:
        lb_test = acorr_ljungbox(stationary_series, lags=test_lags, return_df=True)
        
        results = {}
        min_p = 1.0
        
        for lag in test_lags:
            p_val = lb_test.loc[lag, 'lb_pvalue']
            results[f'lag_{lag}'] = {
                'statistic': round(float(lb_test.loc[lag, 'lb_stat']), 4),
                'p_value': round(float(p_val), 4)
            }
            min_p = min(min_p, p_val)
        
        # Series is forecastable if ANY lag shows significant autocorrelation
        is_white_noise = min_p > 0.05
        
        return {
            'ljung_box_results': results,
            'min_p_value': round(float(min_p), 4),
            'is_white_noise': bool(is_white_noise),
            'forecastable': not bool(is_white_noise)
        }
    
    except Exception as e:
        return {
            'ljung_box_results': None,
            'is_white_noise': True,
            'forecastable': False,
            'error': str(e)
        }


def generate_summary(diagnostics, output_path):
    """Generate human-readable summary file."""
    d = diagnostics
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("TIME SERIES DIAGNOSTICS SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        
        # Data Quality
        dq = d['data_quality']
        f.write("DATA QUALITY\n")
        f.write("-" * 60 + "\n")
        f.write(f"Observations: {dq['n_observations']}\n")
        f.write(f"Date range: {dq['date_start']} to {dq['date_end']}\n")
        f.write(f"Frequency: {dq['frequency']}\n")
        f.write(f"Missing values: {dq['missing_values']} ({dq['missing_pct']}%)\n\n")
        
        # Distribution
        dist = d['distribution']
        f.write("DISTRIBUTION\n")
        f.write("-" * 60 + "\n")
        f.write(f"Mean: {dist['mean']:.4f}    Median: {dist['median']:.4f}\n")
        f.write(f"Std:  {dist['std']:.4f}    Min: {dist['min']:.4f}    Max: {dist['max']:.4f}\n")
        f.write(f"Skewness: {dist['skewness']:.4f}    Kurtosis: {dist['kurtosis']:.4f}\n\n")
        
        # Stationarity
        stat = d['stationarity']
        f.write("STATIONARITY\n")
        f.write("-" * 60 + "\n")
        adf_interp = "Stationary" if stat['adf_stationary'] else "Non-stationary"
        f.write(f"ADF test: statistic={stat['adf_statistic']:.4f}, p={stat['adf_p_value']:.4f} -> {adf_interp}\n")
        
        if stat['kpss_p_value'] is not None:
            kpss_interp = "Stationary" if stat['kpss_stationary'] else "Non-stationary"
            f.write(f"KPSS test: statistic={stat['kpss_statistic']:.4f}, p={stat['kpss_p_value']:.4f} -> {kpss_interp}\n")
        
        f.write(f"Differencing needed: d={stat['differencing_needed']}\n")
        
        if not stat.get('differencing_verified', True):
            f.write("WARNING: Differencing may be insufficient - series may still be non-stationary\n")
        
        f.write(f"Series used for ACF/PACF: {stat['series_used_for_acf']}\n\n")
        
        # Seasonality
        seas = d['seasonality']
        f.write("SEASONALITY\n")
        f.write("-" * 60 + "\n")
        f.write(f"Seasonal: {'Yes' if seas['is_seasonal'] else 'No'}\n")
        
        if seas.get('period'):
            f.write(f"Period: {seas['period']}\n")
        
        strength = seas.get('strength', 0)
        strength_label = "strong" if strength > 0.6 else "moderate" if strength > 0.3 else "weak"
        f.write(f"Strength: {strength:.4f} ({strength_label})\n")
        
        if seas.get('note'):
            f.write(f"Note: {seas['note']}\n")
        f.write("\n")
        
        # Trend
        trend = d['trend']
        f.write("TREND\n")
        f.write("-" * 60 + "\n")
        f.write(f"Has trend: {'Yes' if trend['has_trend'] else 'No'}\n")
        f.write(f"Direction: {trend['direction']}\n")
        
        t_strength = trend.get('strength', 0)
        t_strength_label = "strong" if t_strength > 0.6 else "moderate" if t_strength > 0.3 else "weak"
        f.write(f"Strength: {t_strength:.4f} ({t_strength_label})\n\n")
        
        # Autocorrelation
        ac = d['autocorrelation']
        f.write("AUTOCORRELATION\n")
        f.write("-" * 60 + "\n")
        f.write(f"Significant ACF lags: {ac['significant_acf_lags']}\n")
        f.write(f"Significant PACF lags: {ac['significant_pacf_lags']}\n\n")
        
        # Forecastability
        fc = d['forecastability']
        f.write("FORECASTABILITY\n")
        f.write("-" * 60 + "\n")
        
        if fc.get('ljung_box_results'):
            for lag_key, result in fc['ljung_box_results'].items():
                f.write(f"Ljung-Box {lag_key}: statistic={result['statistic']:.2f}, p={result['p_value']:.4f}\n")
            
            wn_interp = "White noise (random)" if fc['is_white_noise'] else "Predictable structure"
            f.write(f"Conclusion: {wn_interp}\n")
        
        f.write(f"Forecastable: {'Yes' if fc['forecastable'] else 'No'}\n\n")
        
        # Transform
        tf = d['transform']
        f.write("TRANSFORM RECOMMENDATION\n")
        f.write("-" * 60 + "\n")
        f.write(f"Variance stable: {'Yes' if tf['variance_stable'] else 'No'}\n")
        
        if tf.get('boxcox_lambda') is not None:
            f.write(f"Box-Cox optimal lambda: {tf['boxcox_lambda']:.4f}\n")
        
        if tf['recommendation'] == 'none':
            f.write("Recommendation: No transform needed\n")
        else:
            f.write(f"Recommendation: Apply {tf['recommendation']} transform\n")
        
        if tf.get('note'):
            f.write(f"Note: {tf['note']}\n")
        
        # Final Summary
        f.write("\n" + "=" * 60 + "\n")
        f.write("QUICK SUMMARY\n")
        f.write("=" * 60 + "\n")
        f.write(f"Forecastable: {'YES' if fc['forecastable'] else 'NO'}\n")
        f.write(f"Stationary: {'YES' if stat['adf_stationary'] else 'NO (d=' + str(stat['differencing_needed']) + ')'}\n")
        f.write(f"Seasonal: {'YES (period=' + str(seas.get('period', '?')) + ')' if seas['is_seasonal'] else 'NO'}\n")
        f.write(f"Trend: {trend['direction'].upper()}\n")
        
        if tf['recommendation'] != 'none':
            f.write(f"Transform: {tf['recommendation'].upper()} recommended\n")


def run_diagnostics(filepath, output_dir, date_col=None, value_col=None, seasonal_period=None):
    """Run complete diagnostic pipeline."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("TIME SERIES DIAGNOSTICS")
    print("=" * 60 + "\n")
    
    # Load data
    series, detected_date_col, detected_value_col = load_data(filepath, date_col, value_col)
    print(f"Loaded {len(series)} observations ({series.index.min().date()} to {series.index.max().date()})")
    
    # Run all analyses
    print("\nRunning analyses...")
    
    print("  [1/8] Data quality")
    data_quality = analyze_data_quality(series)
    
    print("  [2/8] Distribution")
    distribution = analyze_distribution(series)
    
    print("  [3/8] Stationarity tests (ADF, KPSS)")
    stationarity = test_stationarity(series)
    d = stationarity['differencing_needed']
    freq = data_quality['frequency']
    
    if not stationarity.get('differencing_verified', True):
        print("        WARNING: d=2 may be insufficient")
    
    print("  [4/8] Seasonality (STL decomposition)")
    seasonality = analyze_seasonality(series, seasonal_period, d=d, freq=freq)
    
    print("  [5/8] Trend analysis")
    trend = analyze_trend(series, seasonality.get('period'), d=d, freq=freq)
    
    print("  [6/8] Autocorrelation (ACF, PACF)")
    autocorrelation = analyze_autocorrelation(series, d)
    
    print("  [7/8] Forecastability (Ljung-Box)")
    forecastability = test_forecastability(series, d)
    
    print("  [8/8] Transform recommendation (Box-Cox)")
    transform = check_transform_recommendation(series)
    
    # Compile results
    diagnostics = {
        'data_quality': data_quality,
        'distribution': distribution,
        'stationarity': stationarity,
        'seasonality': seasonality,
        'trend': trend,
        'autocorrelation': autocorrelation,
        'forecastability': forecastability,
        'transform': transform
    }
    
    # Save diagnostics.json
    with open(output_dir / 'diagnostics.json', 'w') as f:
        json.dump(diagnostics, f, indent=2)
    
    # Generate summary.txt
    generate_summary(diagnostics, output_dir / 'summary.txt')
    
    # Save diagnostic state for visualize.py
    diagnostic_state = {
        'date_col': detected_date_col,
        'value_col': detected_value_col,
        'd': stationarity['differencing_needed'],
        'series_used_for_acf': stationarity['series_used_for_acf'],
        'seasonal_period': seasonality.get('period'),
        'frequency': data_quality['frequency']
    }
    with open(output_dir / 'diagnostics_state.json', 'w') as f:
        json.dump(diagnostic_state, f, indent=2)
    
    print(f"\nOutput saved to {output_dir}/")
    print(f"  - diagnostics.json")
    print(f"  - summary.txt")
    print(f"  - diagnostics_state.json")
    
    # Print quick summary
    print("\n" + "=" * 60)
    print("QUICK SUMMARY")
    print("=" * 60)
    print(f"Forecastable: {'Yes' if forecastability['forecastable'] else 'No'}")
    print(f"Stationary: {'Yes' if stationarity['adf_stationary'] else 'No (d=' + str(d) + ')'}")
    
    if not stationarity.get('differencing_verified', True):
        print("  WARNING: Differencing may be insufficient")
    
    seasonal_str = f"Yes (period={seasonality['period']})" if seasonality['is_seasonal'] else "No"
    print(f"Seasonal: {seasonal_str}")
    print(f"Trend: {trend['direction']}")
    
    if transform['recommendation'] != 'none':
        print(f"Transform: {transform['recommendation']} recommended")
    
    return diagnostics


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Time Series Diagnostics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python diagnose.py data.csv
  python diagnose.py data.csv --output-dir results/
  python diagnose.py data.csv --date-col timestamp --value-col sales
  python diagnose.py data.csv --seasonal-period 12
        """
    )
    parser.add_argument('input_file', help='Path to CSV file')
    parser.add_argument('--output-dir', default='diagnostics', help='Output directory (default: diagnostics)')
    parser.add_argument('--date-col', help='Date column name (auto-detected if omitted)')
    parser.add_argument('--value-col', help='Value column name (auto-detected if omitted)')
    parser.add_argument('--seasonal-period', type=int, help='Seasonal period (auto-detected if omitted)')
    
    args = parser.parse_args()
    
    run_diagnostics(args.input_file, args.output_dir, args.date_col, args.value_col, args.seasonal_period)
