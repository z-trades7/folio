"""
Scenario Analysis for Revenue Forecasting
Bull, Base, and Bear case scenarios with Monte Carlo simulation
"""

import pandas as pd
import numpy as np
from scipy import stats


class ScenarioAnalyzer:
    """Generate and analyze multiple revenue scenarios"""
    
    def __init__(self, df_revenue, forecaster):
        self.df = df_revenue
        self.forecaster = forecaster
        self.scenarios = {}
        
    def calculate_volatility(self):
        """Calculate historical revenue volatility"""
        growth_rates = self.df['Revenue'].pct_change().dropna()
        volatility = growth_rates.std()
        mean_growth = growth_rates.mean()
        return mean_growth, volatility
    
    def generate_scenarios(self, years_ahead=5):
        """
        Generate Bull, Base, and Bear scenarios
        """
        last_revenue = self.df['Revenue'].iloc[-1]
        mean_growth, volatility = self.calculate_volatility()
        
        # Calculate recent acceleration (last 3 years)
        recent_growth = self.df['Revenue'].iloc[-3:].pct_change().mean()
        
        # Define scenarios
        scenarios_def = {
            'Bull': {
                'growth_rate': recent_growth * 0.85,  # 85% of recent explosive growth
                'description': 'AI demand continues strong, market share expands'
            },
            'Base': {
                'growth_rate': mean_growth * 1.2,  # 20% above historical average
                'description': 'Steady AI adoption, competitive market'
            },
            'Bear': {
                'growth_rate': mean_growth * 0.6,  # 60% of historical average
                'description': 'Market saturation, increased competition'
            }
        }
        
        future_years = np.arange(self.df['Year'].max() + 1, 
                                 self.df['Year'].max() + years_ahead + 1)
        
        for scenario_name, scenario_data in scenarios_def.items():
            growth_rate = scenario_data['growth_rate']
            forecasts = []
            current_revenue = last_revenue
            
            for year in range(years_ahead):
                current_revenue = current_revenue * (1 + growth_rate)
                forecasts.append(current_revenue)
            
            self.scenarios[scenario_name] = {
                'years': future_years,
                'forecast': np.array(forecasts),
                'growth_rate': growth_rate,
                'description': scenario_data['description']
            }
        
        return self.scenarios
    
    def monte_carlo_simulation(self, years_ahead=5, n_simulations=1000):
        """
        Monte Carlo simulation for confidence intervals
        """
        last_revenue = self.df['Revenue'].iloc[-1]
        mean_growth, volatility = self.calculate_volatility()
        
        # Run simulations
        simulations = np.zeros((n_simulations, years_ahead))
        
        for sim in range(n_simulations):
            current_revenue = last_revenue
            for year in range(years_ahead):
                # Sample growth rate from normal distribution
                growth = np.random.normal(mean_growth, volatility)
                current_revenue = current_revenue * (1 + growth)
                simulations[sim, year] = current_revenue
        
        # Calculate percentiles
        future_years = np.arange(self.df['Year'].max() + 1, 
                                 self.df['Year'].max() + years_ahead + 1)
        
        monte_carlo_results = {
            'years': future_years,
            'median': np.median(simulations, axis=0),
            'mean': np.mean(simulations, axis=0),
            'p10': np.percentile(simulations, 10, axis=0),
            'p25': np.percentile(simulations, 25, axis=0),
            'p75': np.percentile(simulations, 75, axis=0),
            'p90': np.percentile(simulations, 90, axis=0),
            'all_simulations': simulations
        }
        
        return monte_carlo_results
    
    def sensitivity_analysis(self, years_ahead=5):
        """
        Sensitivity analysis: impact of growth rate changes
        """
        last_revenue = self.df['Revenue'].iloc[-1]
        mean_growth, _ = self.calculate_volatility()
        
        # Test different growth rates
        growth_rates = np.arange(-0.10, 0.61, 0.05)  # -10% to +60%
        future_years = np.arange(self.df['Year'].max() + 1, 
                                 self.df['Year'].max() + years_ahead + 1)
        
        sensitivity_results = []
        
        for growth_rate in growth_rates:
            final_revenue = last_revenue * (1 + growth_rate) ** years_ahead
            sensitivity_results.append({
                'growth_rate': growth_rate * 100,
                f'revenue_{years_ahead}y': final_revenue,
                'total_growth': ((final_revenue / last_revenue) - 1) * 100
            })
        
        return pd.DataFrame(sensitivity_results)
    
    def get_summary(self, years_ahead=5):
        """Get summary of all scenarios"""
        if not self.scenarios:
            self.generate_scenarios(years_ahead)
        
        summary = []
        for name, data in self.scenarios.items():
            summary.append({
                'Scenario': name,
                f'{years_ahead}Y Revenue': f"${data['forecast'][-1]:.2f}B",
                'Avg Growth Rate': f"{data['growth_rate']*100:.2f}%",
                'Description': data['description']
            })
        
        return pd.DataFrame(summary)


if __name__ == "__main__":
    from data_loader import NVIDIADataLoader
    from forecast_models import RevenueForecaster
    
    # Load data
    loader = NVIDIADataLoader(
        '../NVDA-IncomeStatement.csv',
        '../NVDA-BalanceSheet.csv',
        '../NVDA-CashFlow.csv'
    )
    
    revenue_df = loader.prepare_revenue_data()
    
    # Create forecaster and scenarios
    forecaster = RevenueForecaster(revenue_df)
    analyzer = ScenarioAnalyzer(revenue_df, forecaster)
    
    # Generate scenarios
    print("="*70)
    print("SCENARIO ANALYSIS")
    print("="*70)
    
    scenarios = analyzer.generate_scenarios(years_ahead=5)
    summary = analyzer.get_summary()
    print("\nScenario Summary:")
    print(summary.to_string(index=False))
    
    # Monte Carlo
    print("\n" + "="*70)
    print("MONTE CARLO SIMULATION (1,000 runs)")
    print("="*70)
    
    mc_results = analyzer.monte_carlo_simulation(years_ahead=5, n_simulations=1000)
    mc_df = pd.DataFrame({
        'Year': mc_results['years'],
        'P10 (Pessimistic)': mc_results['p10'],
        'P50 (Median)': mc_results['median'],
        'P90 (Optimistic)': mc_results['p90']
    })
    print("\n", mc_df.to_string(index=False))
    
    # Sensitivity
    print("\n" + "="*70)
    print("SENSITIVITY ANALYSIS")
    print("="*70)
    
    sensitivity = analyzer.sensitivity_analysis(years_ahead=5)
    print("\nImpact of Growth Rate on 5-Year Revenue:")
    print(sensitivity[::3].to_string(index=False))  # Show every 3rd row

