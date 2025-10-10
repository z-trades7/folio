"""
Advanced Revenue Forecasting Models for NVIDIA
Multiple methodologies with validation and comparison
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')


class RevenueForecaster:
    """Multi-model revenue forecasting system"""
    
    def __init__(self, df_revenue):
        """
        Initialize with revenue dataframe
        df_revenue should have columns: Year, Revenue, Date
        """
        self.df = df_revenue.copy()
        self.models = {}
        self.forecasts = {}
        self.metrics = {}
        
    def calculate_metrics(self, y_true, y_pred, model_name):
        """Calculate forecast accuracy metrics"""
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        r2 = r2_score(y_true, y_pred)
        
        self.metrics[model_name] = {
            'MAE': mae,
            'RMSE': rmse,
            'MAPE': mape,
            'R²': r2
        }
        
        return self.metrics[model_name]
    
    def linear_regression_forecast(self, years_ahead=5):
        """Simple linear regression forecast"""
        X = self.df[['Year']].values
        y = self.df['Revenue'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Forecast
        future_years = np.arange(self.df['Year'].max() + 1, 
                                 self.df['Year'].max() + years_ahead + 1).reshape(-1, 1)
        forecast = model.predict(future_years)
        
        # Calculate metrics on training data
        y_pred = model.predict(X)
        self.calculate_metrics(y, y_pred, 'Linear Regression')
        
        self.models['Linear Regression'] = model
        self.forecasts['Linear Regression'] = pd.DataFrame({
            'Year': future_years.flatten(),
            'Forecast': forecast
        })
        
        return self.forecasts['Linear Regression']
    
    def polynomial_regression_forecast(self, degree=2, years_ahead=5):
        """Polynomial regression forecast"""
        X = self.df[['Year']].values
        y = self.df['Revenue'].values
        
        poly = PolynomialFeatures(degree=degree)
        X_poly = poly.fit_transform(X)
        
        model = LinearRegression()
        model.fit(X_poly, y)
        
        # Forecast
        future_years = np.arange(self.df['Year'].max() + 1, 
                                 self.df['Year'].max() + years_ahead + 1).reshape(-1, 1)
        future_X_poly = poly.transform(future_years)
        forecast = model.predict(future_X_poly)
        
        # Calculate metrics
        y_pred = model.predict(X_poly)
        self.calculate_metrics(y, y_pred, f'Polynomial (degree {degree})')
        
        self.models[f'Polynomial_{degree}'] = {'model': model, 'poly': poly}
        self.forecasts[f'Polynomial_{degree}'] = pd.DataFrame({
            'Year': future_years.flatten(),
            'Forecast': forecast
        })
        
        return self.forecasts[f'Polynomial_{degree}']
    
    def exponential_smoothing_forecast(self, years_ahead=5):
        """Exponential Smoothing forecast"""
        y = self.df['Revenue'].values
        
        # Fit model
        model = ExponentialSmoothing(y, trend='add', seasonal=None)
        fit = model.fit()
        
        # Forecast
        forecast = fit.forecast(steps=years_ahead)
        future_years = np.arange(self.df['Year'].max() + 1, 
                                 self.df['Year'].max() + years_ahead + 1)
        
        # Calculate metrics
        y_pred = fit.fittedvalues
        self.calculate_metrics(y, y_pred, 'Exponential Smoothing')
        
        self.models['Exponential Smoothing'] = fit
        self.forecasts['Exponential Smoothing'] = pd.DataFrame({
            'Year': future_years,
            'Forecast': forecast
        })
        
        return self.forecasts['Exponential Smoothing']
    
    def growth_rate_forecast(self, years_ahead=5, method='cagr'):
        """
        Growth rate-based forecast
        method: 'cagr' for compound annual growth rate, 'recent' for recent years
        """
        revenues = self.df['Revenue'].values
        
        if method == 'cagr':
            # Use historical CAGR
            n_years = len(revenues) - 1
            cagr = (revenues[-1] / revenues[0]) ** (1/n_years) - 1
            growth_rate = cagr
        elif method == 'recent':
            # Use average growth of last 3 years
            recent_revenues = revenues[-3:]
            growth_rates = []
            for i in range(1, len(recent_revenues)):
                growth_rates.append((recent_revenues[i] / recent_revenues[i-1]) - 1)
            growth_rate = np.mean(growth_rates)
        
        # Forecast
        last_revenue = revenues[-1]
        forecasts = []
        for i in range(1, years_ahead + 1):
            forecasts.append(last_revenue * (1 + growth_rate) ** i)
        
        future_years = np.arange(self.df['Year'].max() + 1, 
                                 self.df['Year'].max() + years_ahead + 1)
        
        model_name = f'Growth Rate ({method.upper()}): {growth_rate*100:.2f}%'
        self.forecasts[model_name] = pd.DataFrame({
            'Year': future_years,
            'Forecast': forecasts
        })
        
        return self.forecasts[model_name], growth_rate
    
    def random_forest_forecast(self, years_ahead=5):
        """Random Forest regression forecast"""
        X = self.df[['Year']].values
        y = self.df['Revenue'].values
        
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5)
        model.fit(X, y)
        
        # Forecast
        future_years = np.arange(self.df['Year'].max() + 1, 
                                 self.df['Year'].max() + years_ahead + 1).reshape(-1, 1)
        forecast = model.predict(future_years)
        
        # Calculate metrics
        y_pred = model.predict(X)
        self.calculate_metrics(y, y_pred, 'Random Forest')
        
        self.models['Random Forest'] = model
        self.forecasts['Random Forest'] = pd.DataFrame({
            'Year': future_years.flatten(),
            'Forecast': forecast
        })
        
        return self.forecasts['Random Forest']
    
    def gradient_boosting_forecast(self, years_ahead=5):
        """Gradient Boosting regression forecast"""
        X = self.df[['Year']].values
        y = self.df['Revenue'].values
        
        model = GradientBoostingRegressor(n_estimators=100, random_state=42, 
                                         max_depth=3, learning_rate=0.1)
        model.fit(X, y)
        
        # Forecast
        future_years = np.arange(self.df['Year'].max() + 1, 
                                 self.df['Year'].max() + years_ahead + 1).reshape(-1, 1)
        forecast = model.predict(future_years)
        
        # Calculate metrics
        y_pred = model.predict(X)
        self.calculate_metrics(y, y_pred, 'Gradient Boosting')
        
        self.models['Gradient Boosting'] = model
        self.forecasts['Gradient Boosting'] = pd.DataFrame({
            'Year': future_years.flatten(),
            'Forecast': forecast
        })
        
        return self.forecasts['Gradient Boosting']
    
    def ensemble_forecast(self, years_ahead=5, models_to_use=None):
        """Ensemble forecast combining multiple models"""
        if models_to_use is None:
            models_to_use = ['Polynomial_2', 'Exponential Smoothing', 'Gradient Boosting']
        
        # Ensure models are trained
        if not self.forecasts:
            self.run_all_models(years_ahead=years_ahead)
        
        # Average forecasts
        forecast_values = []
        for model_name in models_to_use:
            if model_name in self.forecasts:
                forecast_values.append(self.forecasts[model_name]['Forecast'].values)
        
        ensemble_forecast = np.mean(forecast_values, axis=0)
        future_years = np.arange(self.df['Year'].max() + 1, 
                                 self.df['Year'].max() + years_ahead + 1)
        
        self.forecasts['Ensemble'] = pd.DataFrame({
            'Year': future_years,
            'Forecast': ensemble_forecast
        })
        
        return self.forecasts['Ensemble']
    
    def run_all_models(self, years_ahead=5):
        """Run all forecasting models"""
        print("Running all forecasting models...")
        
        self.linear_regression_forecast(years_ahead)
        print("  ✓ Linear Regression")
        
        self.polynomial_regression_forecast(degree=2, years_ahead=years_ahead)
        print("  ✓ Polynomial Regression (degree 2)")
        
        self.polynomial_regression_forecast(degree=3, years_ahead=years_ahead)
        print("  ✓ Polynomial Regression (degree 3)")
        
        self.exponential_smoothing_forecast(years_ahead)
        print("  ✓ Exponential Smoothing")
        
        self.growth_rate_forecast(years_ahead, method='cagr')
        print("  ✓ CAGR-based Growth")
        
        self.growth_rate_forecast(years_ahead, method='recent')
        print("  ✓ Recent Growth Rate")
        
        self.random_forest_forecast(years_ahead)
        print("  ✓ Random Forest")
        
        self.gradient_boosting_forecast(years_ahead)
        print("  ✓ Gradient Boosting")
        
        self.ensemble_forecast(years_ahead)
        print("  ✓ Ensemble Model")
        
        print("\nAll models trained successfully!")
        
    def get_all_forecasts(self):
        """Get all forecasts in a single dataframe"""
        all_forecasts = pd.DataFrame({'Year': self.forecasts[list(self.forecasts.keys())[0]]['Year']})
        
        for name, df in self.forecasts.items():
            all_forecasts[name] = df['Forecast'].values
        
        return all_forecasts
    
    def get_metrics_summary(self):
        """Get summary of all model metrics"""
        if not self.metrics:
            return pd.DataFrame()
        
        metrics_df = pd.DataFrame(self.metrics).T
        metrics_df = metrics_df.sort_values('MAPE')
        return metrics_df


if __name__ == "__main__":
    from data_loader import NVIDIADataLoader
    
    # Load data
    loader = NVIDIADataLoader(
        '../NVDA-IncomeStatement.csv',
        '../NVDA-BalanceSheet.csv',
        '../NVDA-CashFlow.csv'
    )
    
    revenue_df = loader.prepare_revenue_data()
    
    # Create forecaster
    forecaster = RevenueForecaster(revenue_df)
    
    # Run all models
    forecaster.run_all_models(years_ahead=5)
    
    # Get forecasts
    all_forecasts = forecaster.get_all_forecasts()
    print("\nForecasts for 2026-2030:")
    print(all_forecasts)
    
    # Get metrics
    metrics = forecaster.get_metrics_summary()
    print("\nModel Performance Metrics:")
    print(metrics)

