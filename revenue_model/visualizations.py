"""
Professional Visualizations for Revenue Forecasting
Creates publication-quality charts for analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 11


class ForecastVisualizer:
    """Create professional visualizations for revenue forecasts"""
    
    def __init__(self, df_revenue, forecaster, analyzer):
        self.df = df_revenue
        self.forecaster = forecaster
        self.analyzer = analyzer
        
    def plot_historical_and_forecasts(self, save_path=None):
        """Plot historical data with all forecast models"""
        fig, ax = plt.subplots(figsize=(16, 9))
        
        # Historical data
        ax.plot(self.df['Year'], self.df['Revenue'], 
               'o-', linewidth=3, markersize=10, 
               label='Historical', color='#1f77b4', zorder=3)
        
        # All forecasts
        colors = plt.cm.Set3(np.linspace(0, 1, len(self.forecaster.forecasts)))
        
        for (name, forecast_df), color in zip(self.forecaster.forecasts.items(), colors):
            if 'Growth Rate' in name:
                linestyle = '--'
                alpha = 0.6
            else:
                linestyle = '-'
                alpha = 0.7
            
            ax.plot(forecast_df['Year'], forecast_df['Forecast'],
                   linestyle, linewidth=2, label=name, color=color, alpha=alpha)
        
        ax.set_xlabel('Year', fontsize=14, fontweight='bold')
        ax.set_ylabel('Revenue (Billions USD)', fontsize=14, fontweight='bold')
        ax.set_title('NVIDIA Revenue Forecast: Multi-Model Comparison (2016-2030)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        # Add annotation
        last_year = self.df['Year'].iloc[-1]
        last_revenue = self.df['Revenue'].iloc[-1]
        ax.annotate(f'${last_revenue:.1f}B\n({last_year})', 
                   xy=(last_year, last_revenue), 
                   xytext=(last_year-2, last_revenue+20),
                   fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', lw=2))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved: {save_path}")
        
        return fig
    
    def plot_scenarios(self, save_path=None):
        """Plot Bull/Base/Bear scenarios"""
        fig, ax = plt.subplots(figsize=(16, 9))
        
        # Historical
        ax.plot(self.df['Year'], self.df['Revenue'],
               'o-', linewidth=3, markersize=10, label='Historical', color='#2C3E50')
        
        # Scenarios
        scenarios = self.analyzer.scenarios
        colors = {'Bull': '#27AE60', 'Base': '#3498DB', 'Bear': '#E74C3C'}
        
        for scenario_name, scenario_data in scenarios.items():
            ax.plot(scenario_data['years'], scenario_data['forecast'],
                   'o-', linewidth=3, markersize=8, 
                   label=f"{scenario_name} ({scenario_data['growth_rate']*100:.1f}% CAGR)",
                   color=colors[scenario_name])
        
        ax.set_xlabel('Year', fontsize=14, fontweight='bold')
        ax.set_ylabel('Revenue (Billions USD)', fontsize=14, fontweight='bold')
        ax.set_title('NVIDIA Revenue Scenarios: Bull, Base, and Bear Cases', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=12, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved: {save_path}")
        
        return fig
    
    def plot_monte_carlo(self, mc_results, save_path=None):
        """Plot Monte Carlo simulation results"""
        fig, ax = plt.subplots(figsize=(16, 9))
        
        # Historical
        ax.plot(self.df['Year'], self.df['Revenue'],
               'o-', linewidth=3, markersize=10, label='Historical', color='#2C3E50')
        
        # Monte Carlo bands
        years = mc_results['years']
        ax.fill_between(years, mc_results['p10'], mc_results['p90'],
                       alpha=0.2, color='#3498DB', label='80% Confidence (P10-P90)')
        ax.fill_between(years, mc_results['p25'], mc_results['p75'],
                       alpha=0.3, color='#3498DB', label='50% Confidence (P25-P75)')
        
        # Median
        ax.plot(years, mc_results['median'],
               'o-', linewidth=3, markersize=8, label='Median Forecast', color='#E74C3C')
        
        ax.set_xlabel('Year', fontsize=14, fontweight='bold')
        ax.set_ylabel('Revenue (Billions USD)', fontsize=14, fontweight='bold')
        ax.set_title('NVIDIA Revenue Forecast: Monte Carlo Simulation (1,000 iterations)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=12, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved: {save_path}")
        
        return fig
    
    def plot_growth_analysis(self, save_path=None):
        """Plot revenue growth rate analysis"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Calculate growth rates
        growth_rates = self.df['Revenue'].pct_change() * 100
        
        # Growth rate over time
        ax1.bar(self.df['Year'][1:], growth_rates[1:], color='#3498DB', alpha=0.7, edgecolor='black')
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.axhline(y=growth_rates.mean(), color='red', linestyle='--', linewidth=2,
                   label=f'Avg: {growth_rates.mean():.1f}%')
        ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax1.set_ylabel('YoY Growth Rate (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Year-over-Year Revenue Growth', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Revenue by decade/period
        periods = ['2016-2018', '2019-2021', '2022-2024', '2025']
        period_revenues = [
            self.df[(self.df['Year'] >= 2016) & (self.df['Year'] <= 2018)]['Revenue'].sum(),
            self.df[(self.df['Year'] >= 2019) & (self.df['Year'] <= 2021)]['Revenue'].sum(),
            self.df[(self.df['Year'] >= 2022) & (self.df['Year'] <= 2024)]['Revenue'].sum(),
            self.df[self.df['Year'] == 2025]['Revenue'].sum()
        ]
        
        colors = ['#95A5A6', '#3498DB', '#E74C3C', '#27AE60']
        bars = ax2.bar(periods, period_revenues, color=colors, edgecolor='black', linewidth=2)
        
        # Add value labels
        for bar, value in zip(bars, period_revenues):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'${value:.1f}B',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax2.set_ylabel('Total Revenue (Billions USD)', fontsize=12, fontweight='bold')
        ax2.set_title('Revenue by Period', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved: {save_path}")
        
        return fig
    
    def create_interactive_dashboard(self, mc_results, save_path='../project_pages/revenue_forecast_dashboard.html'):
        """Create interactive Plotly dashboard"""
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Historical & Forecast Models', 'Scenario Analysis',
                          'Monte Carlo Confidence Intervals', 'Model Performance'),
            specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
                  [{'type': 'scatter'}, {'type': 'bar'}]],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        # 1. Historical + All Forecasts
        fig.add_trace(
            go.Scatter(x=self.df['Year'], y=self.df['Revenue'],
                      mode='lines+markers', name='Historical',
                      line=dict(color='#1f77b4', width=3),
                      marker=dict(size=10)),
            row=1, col=1
        )
        
        for name, forecast_df in self.forecaster.forecasts.items():
            fig.add_trace(
                go.Scatter(x=forecast_df['Year'], y=forecast_df['Forecast'],
                          mode='lines', name=name, line=dict(width=2)),
                row=1, col=1
            )
        
        # 2. Scenarios
        fig.add_trace(
            go.Scatter(x=self.df['Year'], y=self.df['Revenue'],
                      mode='lines+markers', name='Historical',
                      line=dict(color='#2C3E50', width=3),
                      marker=dict(size=10), showlegend=False),
            row=1, col=2
        )
        
        scenario_colors = {'Bull': '#27AE60', 'Base': '#3498DB', 'Bear': '#E74C3C'}
        for scenario_name, scenario_data in self.analyzer.scenarios.items():
            fig.add_trace(
                go.Scatter(x=scenario_data['years'], y=scenario_data['forecast'],
                          mode='lines+markers', name=scenario_name,
                          line=dict(color=scenario_colors[scenario_name], width=3)),
                row=1, col=2
            )
        
        # 3. Monte Carlo
        fig.add_trace(
            go.Scatter(x=self.df['Year'], y=self.df['Revenue'],
                      mode='lines+markers', name='Historical',
                      line=dict(color='#2C3E50', width=3),
                      showlegend=False),
            row=2, col=1
        )
        
        years = mc_results['years']
        fig.add_trace(
            go.Scatter(x=years, y=mc_results['p90'],
                      mode='lines', name='P90', line=dict(width=0),
                      showlegend=False),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=years, y=mc_results['p10'],
                      mode='lines', name='P10-P90', line=dict(width=0),
                      fill='tonexty', fillcolor='rgba(52, 152, 219, 0.2)'),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=years, y=mc_results['median'],
                      mode='lines+markers', name='Median',
                      line=dict(color='#E74C3C', width=3)),
            row=2, col=1
        )
        
        # 4. Model Performance
        metrics_df = self.forecaster.get_metrics_summary()
        fig.add_trace(
            go.Bar(x=metrics_df.index, y=metrics_df['MAPE'],
                  name='MAPE', marker_color='#3498DB'),
            row=2, col=2
        )
        
        # Update layout
        fig.update_xaxes(title_text="Year", row=1, col=1)
        fig.update_xaxes(title_text="Year", row=1, col=2)
        fig.update_xaxes(title_text="Year", row=2, col=1)
        fig.update_xaxes(title_text="Model", row=2, col=2, tickangle=-45)
        
        fig.update_yaxes(title_text="Revenue ($B)", row=1, col=1)
        fig.update_yaxes(title_text="Revenue ($B)", row=1, col=2)
        fig.update_yaxes(title_text="Revenue ($B)", row=2, col=1)
        fig.update_yaxes(title_text="MAPE (%)", row=2, col=2)
        
        fig.update_layout(
            title_text="<b>NVIDIA Revenue Forecasting Dashboard</b><br><sub>Multi-Model Predictive Analysis</sub>",
            title_font_size=24,
            showlegend=True,
            height=1000,
            template='plotly_white'
        )
        
        # Save
        fig.write_html(save_path)
        print(f"✓ Interactive dashboard saved: {save_path}")
        
        return fig


if __name__ == "__main__":
    from data_loader import NVIDIADataLoader
    from forecast_models import RevenueForecaster
    from scenario_analysis import ScenarioAnalyzer
    
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
    
    # Create visualizations
    viz = ForecastVisualizer(revenue_df, forecaster, analyzer)
    
    print("\nGenerating visualizations...")
    viz.plot_historical_and_forecasts('forecast_comparison.png')
    viz.plot_scenarios('scenarios.png')
    viz.plot_monte_carlo(mc_results, 'monte_carlo.png')
    viz.plot_growth_analysis('growth_analysis.png')
    
    print("\nGenerating interactive dashboard...")
    viz.create_interactive_dashboard(mc_results)
    
    print("\n✓ All visualizations created successfully!")

