"""
Data Loader for NVIDIA Financial Statements
Loads and prepares data for revenue forecasting
"""

import pandas as pd
import numpy as np
from datetime import datetime


class NVIDIADataLoader:
    """Load and prepare NVIDIA financial data"""
    
    def __init__(self, income_path, balance_path, cashflow_path):
        self.income_path = income_path
        self.balance_path = balance_path
        self.cashflow_path = cashflow_path
        
    def load_income_statement(self):
        """Load income statement data"""
        df = pd.read_csv(self.income_path)
        return df
    
    def load_balance_sheet(self):
        """Load balance sheet data"""
        df = pd.read_csv(self.balance_path)
        return df
    
    def load_cash_flow(self):
        """Load cash flow data"""
        df = pd.read_csv(self.cashflow_path)
        return df
    
    def prepare_revenue_data(self):
        """Extract and prepare revenue time series"""
        df = self.load_income_statement()
        
        # Get total revenue row
        revenue_row = df[df.iloc[:, 0].str.contains('Total Revenue', case=False, na=False)].iloc[0]
        
        # Extract years and revenue values
        years = revenue_row.index[1:-1]  # Exclude first column (label) and TTM
        revenues = revenue_row.values[1:-1]  # Exclude first column and TTM
        
        # Convert to numeric
        revenues = pd.to_numeric(revenues, errors='coerce')
        
        # Create DataFrame
        df_revenue = pd.DataFrame({
            'Year': years.astype(int),
            'Revenue': revenues / 1e9  # Convert to billions
        })
        
        # Create proper date column (fiscal year ends in January)
        df_revenue['Date'] = pd.to_datetime(df_revenue['Year'].astype(str) + '-01-31')
        df_revenue = df_revenue.sort_values('Year').reset_index(drop=True)
        
        return df_revenue
    
    def prepare_full_dataset(self):
        """Prepare comprehensive dataset with all key metrics"""
        income = self.load_income_statement()
        balance = self.load_balance_sheet()
        cashflow = self.load_cash_flow()
        
        # Helper function to extract metric
        def extract_metric(df, metric_name):
            row = df[df.iloc[:, 0].str.contains(metric_name, case=False, na=False, regex=False)]
            if len(row) > 0:
                values = row.iloc[0, 1:-1]  # Exclude label and TTM
                return pd.to_numeric(values, errors='coerce') / 1e9
            return None
        
        # Extract key metrics
        years = income.columns[1:-1].astype(int)
        
        data = {
            'Year': years,
            'Revenue': extract_metric(income, 'Total Revenue'),
            'Gross_Profit': extract_metric(income, 'Gross Profit'),
            'Operating_Income': extract_metric(income, 'Total Operating Profit'),
            'Net_Income': extract_metric(income, 'Net Income Available'),
            'R&D_Expense': extract_metric(income, 'Research and Development'),
            'Total_Assets': extract_metric(balance, 'Total Assets'),
            'Cash_Flow_Ops': extract_metric(cashflow, 'Cash Flow from Operating Activities'),
        }
        
        df_full = pd.DataFrame(data)
        df_full['Date'] = pd.to_datetime(df_full['Year'].astype(str) + '-01-31')
        df_full = df_full.sort_values('Year').reset_index(drop=True)
        
        # Calculate derived metrics
        df_full['Gross_Margin'] = (df_full['Gross_Profit'] / df_full['Revenue']) * 100
        df_full['Operating_Margin'] = (df_full['Operating_Income'] / df_full['Revenue']) * 100
        df_full['Net_Margin'] = (df_full['Net_Income'] / df_full['Revenue']) * 100
        df_full['Revenue_Growth'] = df_full['Revenue'].pct_change() * 100
        df_full['Asset_Turnover'] = df_full['Revenue'] / df_full['Total_Assets']
        
        return df_full
    
    def get_summary_stats(self):
        """Get summary statistics"""
        df = self.prepare_full_dataset()
        
        stats = {
            'Period': f"{df['Year'].min()} - {df['Year'].max()}",
            'Revenue_CAGR': ((df['Revenue'].iloc[-1] / df['Revenue'].iloc[0]) ** (1/len(df)) - 1) * 100,
            'Avg_Gross_Margin': df['Gross_Margin'].mean(),
            'Avg_Operating_Margin': df['Operating_Margin'].mean(),
            'Avg_Net_Margin': df['Net_Margin'].mean(),
            'Total_Growth': ((df['Revenue'].iloc[-1] / df['Revenue'].iloc[0]) - 1) * 100,
        }
        
        return stats


if __name__ == "__main__":
    # Test the loader
    loader = NVIDIADataLoader(
        '../NVDA-IncomeStatement.csv',
        '../NVDA-BalanceSheet.csv',
        '../NVDA-CashFlow.csv'
    )
    
    revenue_df = loader.prepare_revenue_data()
    print("Revenue Data:")
    print(revenue_df)
    print(f"\nRevenue range: ${revenue_df['Revenue'].min():.2f}B to ${revenue_df['Revenue'].max():.2f}B")
    
    full_df = loader.prepare_full_dataset()
    print("\nFull Dataset:")
    print(full_df)
    
    stats = loader.get_summary_stats()
    print("\nSummary Statistics:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}%")
        else:
            print(f"  {key}: {value}")

