"""
NVIDIA Revenue Forecasting - Comprehensive Analysis
Main script to run all analyses and generate reports
"""

import pandas as pd
import numpy as np
from datetime import datetime
from data_loader import NVIDIADataLoader
from forecast_models import RevenueForecaster
from scenario_analysis import ScenarioAnalyzer
from visualizations import ForecastVisualizer


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")


def run_complete_analysis():
    """Run comprehensive revenue forecasting analysis"""
    
    print_header("NVIDIA REVENUE FORECASTING SYSTEM")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Author: Financial Analyst Portfolio Project")
    
    # 1. Load Data
    print_header("1. DATA LOADING")
    
    loader = NVIDIADataLoader(
        '../NVDA-IncomeStatement.csv',
        '../NVDA-BalanceSheet.csv',
        '../NVDA-CashFlow.csv'
    )
    
    revenue_df = loader.prepare_revenue_data()
    full_df = loader.prepare_full_dataset()
    stats = loader.get_summary_stats()
    
    print(f"✓ Loaded financial data for {len(revenue_df)} years")
    print(f"  Period: {revenue_df['Year'].min()} - {revenue_df['Year'].max()}")
    print(f"  Revenue range: ${revenue_df['Revenue'].min():.2f}B to ${revenue_df['Revenue'].max():.2f}B")
    
    print("\nKey Statistics:")
    print(f"  Revenue CAGR: {stats['Revenue_CAGR']:.2f}%")
    print(f"  Total Growth: {stats['Total_Growth']:.2f}%")
    print(f"  Avg Gross Margin: {stats['Avg_Gross_Margin']:.2f}%")
    print(f"  Avg Operating Margin: {stats['Avg_Operating_Margin']:.2f}%")
    print(f"  Avg Net Margin: {stats['Avg_Net_Margin']:.2f}%")
    
    # 2. Forecasting Models
    print_header("2. FORECASTING MODELS")
    
    forecaster = RevenueForecaster(revenue_df)
    forecaster.run_all_models(years_ahead=5)
    
    print("\nAll Forecasts Summary (2026-2030):")
    forecasts = forecaster.get_all_forecasts()
    print(forecasts.to_string(index=False))
    
    print("\nModel Performance (Training Data):")
    metrics = forecaster.get_metrics_summary()
    print(metrics[['MAPE', 'RMSE', 'R²']].to_string())
    
    # Highlight best model
    best_model = metrics.index[0]
    best_mape = metrics['MAPE'].iloc[0]
    print(f"\n🏆 Best Performing Model: {best_model} (MAPE: {best_mape:.2f}%)")
    
    # 3. Scenario Analysis
    print_header("3. SCENARIO ANALYSIS")
    
    analyzer = ScenarioAnalyzer(revenue_df, forecaster)
    scenarios = analyzer.generate_scenarios(years_ahead=5)
    
    print("Scenario Forecasts for 2030:")
    for scenario_name, scenario_data in scenarios.items():
        final_revenue = scenario_data['forecast'][-1]
        growth_rate = scenario_data['growth_rate'] * 100
        print(f"  {scenario_name:12s}: ${final_revenue:,.2f}B  (CAGR: {growth_rate:5.1f}%)  - {scenario_data['description']}")
    
    # 4. Monte Carlo Simulation
    print_header("4. MONTE CARLO SIMULATION")
    
    mc_results = analyzer.monte_carlo_simulation(years_ahead=5, n_simulations=1000)
    
    print("Probabilistic Revenue Forecasts (1,000 simulations):")
    print("\nYear    P10 (Pessimistic)    P50 (Median)    P90 (Optimistic)")
    print("-" * 65)
    for i, year in enumerate(mc_results['years']):
        print(f"{year}    ${mc_results['p10'][i]:>8.2f}B         ${mc_results['median'][i]:>8.2f}B        ${mc_results['p90'][i]:>8.2f}B")
    
    # 5. Key Insights
    print_header("5. KEY INSIGHTS & RECOMMENDATIONS")
    
    print("Growth Trajectory:")
    latest_revenue = revenue_df['Revenue'].iloc[-1]
    median_2030 = mc_results['median'][-1]
    growth_potential = ((median_2030 / latest_revenue) - 1) * 100
    
    print(f"  • Current Revenue (2025): ${latest_revenue:.2f}B")
    print(f"  • Median Forecast (2030): ${median_2030:.2f}B")
    print(f"  • Growth Potential: {growth_potential:.1f}% over 5 years")
    
    print("\nMarket Positioning:")
    print("  • NVIDIA is experiencing unprecedented growth driven by AI/ML demand")
    print("  • Historical CAGR of 38.5% is exceptional for a company of this scale")
    print("  • Recent acceleration (2024-2025) suggests new growth paradigm")
    
    print("\nRisk Factors:")
    print("  • Market saturation in AI accelerators")
    print("  • Increased competition from AMD, Intel, and custom chips")
    print("  • Cyclical nature of semiconductor industry")
    print("  • Geopolitical risks affecting supply chain")
    
    print("\nOpportunities:")
    print("  • Expanding AI adoption across industries")
    print("  • Growth in edge computing and autonomous vehicles")
    print("  • Data center modernization cycle")
    print("  • Software and services revenue expansion")
    
    # 6. Generate Visualizations
    print_header("6. GENERATING VISUALIZATIONS")
    
    viz = ForecastVisualizer(revenue_df, forecaster, analyzer)
    
    viz.plot_historical_and_forecasts('outputs/forecast_comparison.png')
    print("  ✓ Forecast comparison chart")
    
    viz.plot_scenarios('outputs/scenarios.png')
    print("  ✓ Scenario analysis chart")
    
    viz.plot_monte_carlo(mc_results, 'outputs/monte_carlo.png')
    print("  ✓ Monte Carlo simulation chart")
    
    viz.plot_growth_analysis('outputs/growth_analysis.png')
    print("  ✓ Growth analysis chart")
    
    viz.create_interactive_dashboard(mc_results, '../project_pages/revenue_forecast_dashboard.html')
    print("  ✓ Interactive dashboard (HTML)")
    
    # 7. Export Results
    print_header("7. EXPORTING RESULTS")
    
    # Export forecasts to CSV
    forecasts.to_csv('outputs/revenue_forecasts_2026_2030.csv', index=False)
    print("  ✓ Forecasts exported to CSV")
    
    # Export scenarios
    scenario_df = analyzer.get_summary()
    scenario_df.to_csv('outputs/scenario_analysis.csv', index=False)
    print("  ✓ Scenarios exported to CSV")
    
    # Export model performance
    metrics.to_csv('outputs/model_performance.csv')
    print("  ✓ Model metrics exported to CSV")
    
    print_header("ANALYSIS COMPLETE")
    print("All results saved to 'outputs/' directory")
    print("Interactive dashboard: project_pages/revenue_forecast_dashboard.html")
    print("\n")


if __name__ == "__main__":
    import os
    
    # Create outputs directory
    os.makedirs('outputs', exist_ok=True)
    
    # Run analysis
    run_complete_analysis()

