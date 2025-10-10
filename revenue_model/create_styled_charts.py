"""
Create publication-quality charts with portfolio-consistent styling
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from data_loader import NVIDIADataLoader
from forecast_models import RevenueForecaster
from scenario_analysis import ScenarioAnalyzer

# Portfolio color scheme
plt.style.use('dark_background')
sns.set_palette("Set2")

COLORS = {
    'background': '#1a1a1a',
    'figure': '#2a2a2a',
    'text': '#E8E8E8',
    'grid': '#444444',
    'primary': '#C0C0C0',
    'historical': '#3498DB',
    'bull': '#27AE60',
    'base': '#3498DB',
    'bear': '#E74C3C',
    'median': '#E74C3C'
}

# Set global parameters
plt.rcParams['figure.facecolor'] = COLORS['background']
plt.rcParams['axes.facecolor'] = COLORS['figure']
plt.rcParams['text.color'] = COLORS['text']
plt.rcParams['axes.labelcolor'] = COLORS['text']
plt.rcParams['xtick.color'] = COLORS['text']
plt.rcParams['ytick.color'] = COLORS['text']
plt.rcParams['grid.color'] = COLORS['grid']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 13
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['figure.titlesize'] = 17

# Load data
loader = NVIDIADataLoader(
    '../NVDA-IncomeStatement.csv',
    '../NVDA-BalanceSheet.csv',
    '../NVDA-CashFlow.csv'
)

revenue_df = loader.prepare_revenue_data()

# Create models
forecaster = RevenueForecaster(revenue_df)
forecaster.run_all_models(years_ahead=5)

analyzer = ScenarioAnalyzer(revenue_df, forecaster)
analyzer.generate_scenarios(years_ahead=5)
mc_results = analyzer.monte_carlo_simulation(years_ahead=5, n_simulations=1000)

# 1. Scenarios Chart
fig, ax = plt.subplots(figsize=(16, 9))
fig.patch.set_facecolor(COLORS['background'])
ax.set_facecolor(COLORS['figure'])

# Historical
ax.plot(revenue_df['Year'], revenue_df['Revenue'],
       'o-', linewidth=4, markersize=12, label='Historical', 
       color=COLORS['historical'], markeredgecolor='white', markeredgewidth=2)

# Scenarios with annotations
scenarios = analyzer.scenarios
for scenario_name, scenario_data in scenarios.items():
    color = COLORS[scenario_name.lower()]
    line = ax.plot(scenario_data['years'], scenario_data['forecast'],
           'o-', linewidth=4, markersize=10, 
           label=f"{scenario_name} ({scenario_data['growth_rate']*100:.0f}% CAGR)",
           color=color, markeredgecolor='white', markeredgewidth=1.5)
    
    # Add annotation for final value
    final_revenue = scenario_data['forecast'][-1]
    ax.annotate(f'${final_revenue:.0f}B',
               xy=(scenario_data['years'][-1], final_revenue),
               xytext=(10, 0), textcoords='offset points',
               fontsize=12, fontweight='bold', color=color,
               bbox=dict(boxstyle='round,pad=0.5', facecolor=COLORS['figure'], 
                        edgecolor=color, linewidth=2, alpha=0.9))

ax.set_xlabel('Year', fontsize=14, fontweight='bold', color=COLORS['text'])
ax.set_ylabel('Revenue (Billions USD)', fontsize=14, fontweight='bold', color=COLORS['text'])
ax.set_title('NVIDIA Revenue Scenarios: Bull, Base, and Bear Cases\n' + 
            'Conservative: AI Diminishing Returns | Aggressive: Quantum Computing Breakthrough',
            fontsize=16, fontweight='bold', pad=20, color=COLORS['text'])
ax.legend(loc='upper left', fontsize=12, framealpha=0.95, facecolor=COLORS['figure'],
         edgecolor=COLORS['primary'])
ax.grid(True, alpha=0.2, color=COLORS['grid'])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color(COLORS['grid'])
ax.spines['left'].set_color(COLORS['grid'])

plt.tight_layout()
plt.savefig('outputs/scenarios_styled.png', dpi=300, bbox_inches='tight', 
           facecolor=COLORS['background'])
print("✓ Scenarios chart created")
plt.close()

# 2. Monte Carlo Chart
fig, ax = plt.subplots(figsize=(16, 9))
fig.patch.set_facecolor(COLORS['background'])
ax.set_facecolor(COLORS['figure'])

# Historical
ax.plot(revenue_df['Year'], revenue_df['Revenue'],
       'o-', linewidth=4, markersize=12, label='Historical', 
       color=COLORS['historical'], markeredgecolor='white', markeredgewidth=2)

# Monte Carlo bands
years = mc_results['years']
ax.fill_between(years, mc_results['p10'], mc_results['p90'],
               alpha=0.25, color=COLORS['base'], label='80% Confidence (P10-P90)')
ax.fill_between(years, mc_results['p25'], mc_results['p75'],
               alpha=0.35, color=COLORS['base'], label='50% Confidence (P25-P75)')

# Median
ax.plot(years, mc_results['median'],
       'o-', linewidth=4, markersize=10, label='Median Forecast', 
       color=COLORS['median'], markeredgecolor='white', markeredgewidth=1.5)

# Add annotation for 2030
final_median = mc_results['median'][-1]
final_p10 = mc_results['p10'][-1]
final_p90 = mc_results['p90'][-1]

ax.annotate(f'2030 Median:\n${final_median:.0f}B',
           xy=(years[-1], final_median),
           xytext=(-150, 50), textcoords='offset points',
           fontsize=13, fontweight='bold', color=COLORS['median'],
           bbox=dict(boxstyle='round,pad=0.7', facecolor=COLORS['figure'], 
                    edgecolor=COLORS['median'], linewidth=2, alpha=0.95),
           arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['median']))

ax.set_xlabel('Year', fontsize=14, fontweight='bold', color=COLORS['text'])
ax.set_ylabel('Revenue (Billions USD)', fontsize=14, fontweight='bold', color=COLORS['text'])
ax.set_title('NVIDIA Revenue Forecast: Monte Carlo Simulation\n' + 
            '1,000 Iterations | Probabilistic Confidence Intervals',
            fontsize=16, fontweight='bold', pad=20, color=COLORS['text'])
ax.legend(loc='upper left', fontsize=12, framealpha=0.95, facecolor=COLORS['figure'],
         edgecolor=COLORS['primary'])
ax.grid(True, alpha=0.2, color=COLORS['grid'])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color(COLORS['grid'])
ax.spines['left'].set_color(COLORS['grid'])

plt.tight_layout()
plt.savefig('outputs/monte_carlo_styled.png', dpi=300, bbox_inches='tight',
           facecolor=COLORS['background'])
print("✓ Monte Carlo chart created")
plt.close()

# 3. Growth Analysis
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor(COLORS['background'])

# YoY Growth Rate
ax1.set_facecolor(COLORS['figure'])
growth_rates = revenue_df['Revenue'].pct_change() * 100

bars = ax1.bar(revenue_df['Year'][1:], growth_rates[1:], 
              color=COLORS['primary'], alpha=0.8, edgecolor='white', linewidth=1.5)

# Color code bars
for i, bar in enumerate(bars):
    if growth_rates[i+1] > 50:
        bar.set_color(COLORS['bull'])
    elif growth_rates[i+1] < 0:
        bar.set_color(COLORS['bear'])

ax1.axhline(y=0, color='white', linestyle='-', linewidth=1)
ax1.axhline(y=growth_rates.mean(), color=COLORS['median'], linestyle='--', 
           linewidth=3, label=f'Avg: {growth_rates.mean():.0f}%')
ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('YoY Growth Rate (%)', fontsize=12, fontweight='bold')
ax1.set_title('Year-over-Year Revenue Growth', fontsize=14, fontweight='bold', pad=15)
ax1.legend(fontsize=11, facecolor=COLORS['figure'], edgecolor=COLORS['primary'])
ax1.grid(True, alpha=0.2, axis='y', color=COLORS['grid'])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['bottom'].set_color(COLORS['grid'])
ax1.spines['left'].set_color(COLORS['grid'])

# Revenue by Era
ax2.set_facecolor(COLORS['figure'])
eras = ['Pre-AI\n2016-2020', 'Data Center\n2021-2023', 'AI Boom\n2024-2025']
era_revenues = [
    revenue_df[(revenue_df['Year'] >= 2016) & (revenue_df['Year'] <= 2020)]['Revenue'].sum(),
    revenue_df[(revenue_df['Year'] >= 2021) & (revenue_df['Year'] <= 2023)]['Revenue'].sum(),
    revenue_df[(revenue_df['Year'] >= 2024) & (revenue_df['Year'] <= 2025)]['Revenue'].sum()
]

colors = ['#95A5A6', COLORS['base'], COLORS['bull']]
bars = ax2.bar(eras, era_revenues, color=colors, edgecolor='white', linewidth=2, width=0.6)

# Add value labels
for bar, value in zip(bars, era_revenues):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'${value:.1f}B',
            ha='center', va='bottom', fontsize=13, fontweight='bold', color=COLORS['text'])

ax2.set_ylabel('Total Revenue (Billions USD)', fontsize=12, fontweight='bold')
ax2.set_title('Revenue by Era', fontsize=14, fontweight='bold', pad=15)
ax2.grid(True, alpha=0.2, axis='y', color=COLORS['grid'])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_color(COLORS['grid'])
ax2.spines['left'].set_color(COLORS['grid'])

plt.tight_layout()
plt.savefig('outputs/growth_analysis_styled.png', dpi=300, bbox_inches='tight',
           facecolor=COLORS['background'])
print("✓ Growth analysis chart created")
plt.close()

print("\n✓ All styled charts created successfully!")

