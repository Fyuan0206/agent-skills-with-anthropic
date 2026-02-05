#!/usr/bin/env python3
"""
Time Series Visualization

Generates comprehensive diagnostic plots for visual inspection.
Output: plots/ directory with PNG files

Run diagnose.py first to ensure plots are synchronized with diagnostic results.
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import STL

from ts_utils import (
    load_data,
    detect_frequency,
    test_stationarity,
    get_stationary_series,
    detect_seasonal_period
)


def load_diagnostic_state(output_dir):
    """Load diagnostic state from diagnose.py if available."""
    state_file = Path(output_dir) / 'diagnostics_state.json'
    if state_file.exists():
        with open(state_file, 'r') as f:
            return json.load(f)
    return None


def plot_timeseries(series, output_dir):
    """Create time series line plot."""
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(series.index, series.values, linewidth=0.8, color='#1f77b4')
    ax.set_title('Time Series Plot', fontsize=12, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'timeseries.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Created: timeseries.png")


def plot_histogram(series, output_dir):
    """Create histogram with distribution statistics."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    n, bins, patches = ax.hist(series.values, bins=30, edgecolor='black', alpha=0.7, color='#1f77b4')
    
    # Add statistics
    mean_val = series.mean()
    median_val = series.median()
    std_val = series.std()
    
    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
    ax.axvline(median_val, color='orange', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')
    
    # Add std range
    ax.axvspan(mean_val - std_val, mean_val + std_val, alpha=0.1, color='red', label=f'±1 Std: {std_val:.2f}')
    
    ax.set_title('Distribution (Histogram)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'histogram.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Created: histogram.png")


def plot_rolling_stats(series, output_dir):
    """Create rolling statistics plot to visualize stationarity."""
    window = max(2, min(12, len(series) // 10))
    
    rolling_mean = series.rolling(window).mean()
    rolling_std = series.rolling(window).std()
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    
    # Plot 1: Series with rolling mean
    axes[0].plot(series.index, series.values, label='Original', alpha=0.5, linewidth=0.8)
    axes[0].plot(series.index, rolling_mean, label=f'Rolling Mean (w={window})', 
                 color='red', linewidth=2)
    axes[0].set_title('Rolling Mean', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Value')
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Rolling std
    axes[1].plot(series.index, rolling_std, label=f'Rolling Std (w={window})', 
                 color='#2ca02c', linewidth=2)
    axes[1].axhline(series.std(), color='gray', linestyle='--', alpha=0.7, label='Overall Std')
    axes[1].set_title('Rolling Standard Deviation', fontsize=11, fontweight='bold')
    axes[1].set_xlabel('Date')
    axes[1].set_ylabel('Std Dev')
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'rolling_stats.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Created: rolling_stats.png")


def plot_box_by_interval(series, frequency, output_dir):
    """Create box plots by time intervals based on data frequency."""
    plots_created = []
    
    # Determine which box plots to create based on frequency
    interval_configs = {
        'hourly': [('hour', 'Hour of Day'), ('dayofweek', 'Day of Week')],
        'daily': [('dayofweek', 'Day of Week'), ('month', 'Month')],
        'weekly': [('month', 'Month'), ('quarter', 'Quarter')],
        'monthly': [('month', 'Month'), ('quarter', 'Quarter')],
        'quarterly': [('quarter', 'Quarter')],
        'yearly': [('month', 'Month')]
    }
    
    intervals = interval_configs.get(frequency, [('month', 'Month')])
    
    for interval_type, interval_label in intervals:
        try:
            # Extract the grouping variable
            if interval_type == 'hour':
                groups = series.index.hour
                order = list(range(24))
                labels = [str(i) for i in range(24)]
            elif interval_type == 'dayofweek':
                groups = series.index.dayofweek
                order = list(range(7))
                labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            elif interval_type == 'month':
                groups = series.index.month
                order = list(range(1, 13))
                labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            elif interval_type == 'quarter':
                groups = series.index.quarter
                order = list(range(1, 5))
                labels = ['Q1', 'Q2', 'Q3', 'Q4']
            else:
                continue
            
            # Group data
            grouped_data = []
            valid_labels = []
            for i, label in zip(order, labels):
                mask = groups == i
                if mask.sum() > 0:
                    grouped_data.append(series[mask].values)
                    valid_labels.append(label)
            
            if len(grouped_data) < 2:
                continue
            
            # Create box plot
            fig, ax = plt.subplots(figsize=(10, 5))
            bp = ax.boxplot(grouped_data, patch_artist=True)
            ax.set_xticklabels(valid_labels)
            
            # Style the boxes
            colors = plt.cm.Blues(np.linspace(0.3, 0.7, len(bp['boxes'])))
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            ax.set_title(f'Distribution by {interval_label}', fontsize=12, fontweight='bold')
            ax.set_xlabel(interval_label)
            ax.set_ylabel('Value')
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            filename = f'box_by_{interval_type}.png'
            plt.savefig(output_dir / filename, dpi=150, bbox_inches='tight')
            plt.close()
            print(f"  Created: {filename}")
            plots_created.append(filename)
            
        except Exception as e:
            print(f"  Skipped: box_by_{interval_type}.png ({e})")
    
    return plots_created


def plot_acf_pacf(series, d, output_dir):
    """Create ACF and PACF plots on stationary series."""
    stationary_series = get_stationary_series(series, d)
    
    max_lags = min(40, len(stationary_series) // 2 - 1)
    if max_lags < 2:
        print("  Skipped: acf_pacf.png (insufficient data)")
        return
    
    # Determine label
    if d == 0:
        diff_label = "Original (Stationary)"
    elif d == 1:
        diff_label = "First Difference (d=1)"
    else:
        diff_label = f"Differenced (d={d})"
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # ACF plot
    plot_acf(stationary_series, lags=max_lags, ax=axes[0], alpha=0.05)
    axes[0].set_title(f'Autocorrelation Function (ACF) - {diff_label}', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Lag')
    axes[0].set_ylabel('ACF')
    
    # PACF plot
    plot_pacf(stationary_series, lags=max_lags, ax=axes[1], alpha=0.05)
    axes[1].set_title(f'Partial Autocorrelation Function (PACF) - {diff_label}', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Lag')
    axes[1].set_ylabel('PACF')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'acf_pacf.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Created: acf_pacf.png ({diff_label.lower()})")


def plot_decomposition(series, seasonal_period, output_dir, d=None, freq=None):
    """Create STL decomposition plot."""
    if seasonal_period is None:
        seasonal_period = detect_seasonal_period(series, d=d, freq=freq)
    
    if seasonal_period is None or seasonal_period < 2:
        print("  Skipped: decomposition.png (no seasonal period detected)")
        return
    
    if len(series) < seasonal_period * 2:
        print(f"  Skipped: decomposition.png (need {seasonal_period * 2}+ observations)")
        return
    
    try:
        stl = STL(series, period=seasonal_period, robust=True)
        result = stl.fit()
        
        fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
        
        components = [
            (series.values, 'Original', '#1f77b4'),
            (result.trend, 'Trend', '#d62728'),
            (result.seasonal, f'Seasonal (period={seasonal_period})', '#2ca02c'),
            (result.resid, 'Residual', '#7f7f7f')
        ]
        
        for ax, (data, title, color) in zip(axes, components):
            ax.plot(series.index, data, color=color, linewidth=0.8)
            ax.set_title(title, fontsize=10, fontweight='bold', loc='left')
            ax.grid(True, alpha=0.3)
            ax.set_ylabel('Value')
        
        axes[-1].set_xlabel('Date')
        
        plt.suptitle('STL Decomposition', fontsize=12, fontweight='bold', y=1.01)
        plt.tight_layout()
        plt.savefig(output_dir / 'decomposition.png', dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Created: decomposition.png (period={seasonal_period})")
        
    except Exception as e:
        print(f"  Skipped: decomposition.png ({e})")


def plot_lag_scatter(series, output_dir, lags=[1, 7, 12]):
    """Create lag scatter plots for visual autocorrelation inspection."""
    available_lags = [lag for lag in lags if lag < len(series)]
    
    if len(available_lags) == 0:
        print("  Skipped: lag_scatter.png (insufficient data)")
        return
    
    n_plots = len(available_lags)
    fig, axes = plt.subplots(1, n_plots, figsize=(4 * n_plots, 4))
    
    if n_plots == 1:
        axes = [axes]
    
    for ax, lag in zip(axes, available_lags):
        x = series.iloc[:-lag].values
        y = series.iloc[lag:].values
        
        ax.scatter(x, y, alpha=0.5, s=10)
        ax.set_xlabel(f'y(t)')
        ax.set_ylabel(f'y(t+{lag})')
        ax.set_title(f'Lag {lag}', fontsize=10, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add correlation coefficient
        corr = np.corrcoef(x, y)[0, 1]
        ax.text(0.05, 0.95, f'r = {corr:.3f}', transform=ax.transAxes, 
                fontsize=9, verticalalignment='top', 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.suptitle('Lag Scatter Plots', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'lag_scatter.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Created: lag_scatter.png")


def generate_plots(filepath, output_dir, date_col=None, value_col=None, seasonal_period=None):
    """Generate all diagnostic visualizations."""
    output_dir = Path(output_dir)
    plots_dir = output_dir / 'plots'
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    # Try to load diagnostic state from diagnose.py
    diag_state = load_diagnostic_state(output_dir)
    
    if diag_state:
        print("Found diagnostics_state.json - synchronizing with diagnose.py results")
        if date_col is None:
            date_col = diag_state.get('date_col')
        if value_col is None:
            value_col = diag_state.get('value_col')
        d = diag_state.get('d', 0)
        if seasonal_period is None:
            seasonal_period = diag_state.get('seasonal_period')
        frequency = diag_state.get('frequency', 'unknown')
    else:
        print("Warning: diagnostics_state.json not found.")
        print("  Run diagnose.py first for synchronized results.")
        print("  Performing independent analysis...\n")
        d = None
        frequency = None
    
    # Load data
    series, _, _ = load_data(filepath, date_col, value_col)
    print(f"\nGenerating plots for {len(series)} observations...")
    
    # Detect frequency if not loaded
    if frequency is None or frequency == 'unknown':
        frequency = detect_frequency(series)
    
    # Determine d if not loaded
    if d is None:
        stationarity = test_stationarity(series)
        d = stationarity['differencing_needed']
        print(f"  Determined differencing: d={d}")
    
    # Generate all plots
    print("\nPlots:")
    
    plot_timeseries(series, plots_dir)
    plot_histogram(series, plots_dir)
    plot_rolling_stats(series, plots_dir)
    plot_box_by_interval(series, frequency, plots_dir)
    plot_acf_pacf(series, d, plots_dir)
    plot_decomposition(series, seasonal_period, plots_dir, d=d, freq=frequency)
    plot_lag_scatter(series, plots_dir)
    
    print(f"\nAll plots saved to: {plots_dir}/")
    
    if diag_state:
        print("[OK] Plots synchronized with diagnose.py results")
    else:
        print("[!] Plots generated independently - run diagnose.py first for full sync")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Time Series Visualization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python visualize.py data.csv
  python visualize.py data.csv --output-dir results/
  python visualize.py data.csv --date-col timestamp --value-col sales
  python visualize.py data.csv --seasonal-period 12

Note: Run diagnose.py first for synchronized ACF/PACF plots.
        """
    )
    parser.add_argument('input_file', help='Path to CSV file')
    parser.add_argument('--output-dir', default='diagnostics', help='Output directory (default: diagnostics)')
    parser.add_argument('--date-col', help='Date column name (auto-detected if omitted)')
    parser.add_argument('--value-col', help='Value column name (auto-detected if omitted)')
    parser.add_argument('--seasonal-period', type=int, help='Seasonal period (auto-detected if omitted)')
    
    args = parser.parse_args()
    
    generate_plots(args.input_file, args.output_dir, args.date_col, args.value_col, args.seasonal_period)
