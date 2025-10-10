"""
Create styled interactive dashboard matching portfolio theme
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# Portfolio color scheme
COLORS = {
    'background': '#1a1a1a',
    'paper': '#2a2a2a',
    'text': '#E8E8E8',
    'grid': '#444444',
    'primary': '#C0C0C0',
    'accent1': '#999999',
    'accent2': '#ffffff',
    'historical': '#3498DB',
    'bull': '#27AE60',
    'base': '#3498DB',
    'bear': '#E74C3C',
    'median': '#E74C3C'
}

# Create figure with subplots
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        '<b>Multi-Model Forecast Comparison</b>',
        '<b>Scenario Analysis: Bull, Base & Bear Cases</b>',
        '<b>Monte Carlo Simulation (1,000 iterations)</b>',
        '<b>Model Performance Metrics</b>'
    ),
    specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
          [{'type': 'scatter'}, {'type': 'bar'}]],
    vertical_spacing=0.15,
    horizontal_spacing=0.12
)

# 1. Historical + All Forecasts
fig.add_trace(
    go.Scatter(
        x=revenue_df['Year'], 
        y=revenue_df['Revenue'],
        mode='lines+markers', 
        name='Historical',
        line=dict(color=COLORS['historical'], width=4),
        marker=dict(size=12, line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:.1f}B<extra></extra>'
    ),
    row=1, col=1
)

# Add ensemble forecast prominently
ensemble_forecast = forecaster.forecasts['Ensemble']
fig.add_trace(
    go.Scatter(
        x=ensemble_forecast['Year'], 
        y=ensemble_forecast['Forecast'],
        mode='lines+markers', 
        name='Ensemble Forecast',
        line=dict(color=COLORS['accent2'], width=4, dash='dash'),
        marker=dict(size=10),
        hovertemplate='<b>%{x}</b><br>Forecast: $%{y:.1f}B<extra></extra>'
    ),
    row=1, col=1
)

# Add other forecasts with lower opacity
for name, forecast_df in forecaster.forecasts.items():
    if name != 'Ensemble' and 'Growth Rate' not in name:
        fig.add_trace(
            go.Scatter(
                x=forecast_df['Year'], 
                y=forecast_df['Forecast'],
                mode='lines', 
                name=name, 
                line=dict(width=2),
                opacity=0.5,
                hovertemplate='<b>%{x}</b><br>%{y:.1f}B<extra></extra>'
            ),
            row=1, col=1
        )

# 2. Scenarios
fig.add_trace(
    go.Scatter(
        x=revenue_df['Year'], 
        y=revenue_df['Revenue'],
        mode='lines+markers', 
        name='Historical',
        line=dict(color=COLORS['historical'], width=4),
        marker=dict(size=12, line=dict(width=2, color='white')),
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:.1f}B<extra></extra>'
    ),
    row=1, col=2
)

scenario_info = {
    'Bull': {'color': COLORS['bull'], 'desc': 'Quantum computing breakthrough'},
    'Base': {'color': COLORS['base'], 'desc': 'Steady AI growth'},
    'Bear': {'color': COLORS['bear'], 'desc': 'AI diminishing returns'}
}

for scenario_name, scenario_data in analyzer.scenarios.items():
    info = scenario_info[scenario_name]
    fig.add_trace(
        go.Scatter(
            x=scenario_data['years'], 
            y=scenario_data['forecast'],
            mode='lines+markers', 
            name=f"{scenario_name}<br><sub>{info['desc']}</sub>",
            line=dict(color=info['color'], width=4),
            marker=dict(size=10),
            hovertemplate=f'<b>{scenario_name} Case</b><br>%{{x}}<br>Revenue: $%{{y:.1f}}B<extra></extra>'
        ),
        row=1, col=2
    )

# 3. Monte Carlo
fig.add_trace(
    go.Scatter(
        x=revenue_df['Year'], 
        y=revenue_df['Revenue'],
        mode='lines+markers', 
        name='Historical',
        line=dict(color=COLORS['historical'], width=4),
        marker=dict(size=12, line=dict(width=2, color='white')),
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:.1f}B<extra></extra>'
    ),
    row=2, col=1
)

years = mc_results['years']
fig.add_trace(
    go.Scatter(
        x=years, 
        y=mc_results['p90'],
        mode='lines', 
        name='P90', 
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ),
    row=2, col=1
)

fig.add_trace(
    go.Scatter(
        x=years, 
        y=mc_results['p10'],
        mode='lines', 
        name='80% Confidence<br>(P10-P90)', 
        line=dict(width=0),
        fill='tonexty', 
        fillcolor='rgba(52, 152, 219, 0.3)',
        hovertemplate='<b>%{x}</b><br>P10: $%{y:.1f}B<extra></extra>'
    ),
    row=2, col=1
)

fig.add_trace(
    go.Scatter(
        x=years, 
        y=mc_results['median'],
        mode='lines+markers', 
        name='Median Forecast',
        line=dict(color=COLORS['median'], width=4),
        marker=dict(size=10),
        hovertemplate='<b>%{x}</b><br>Median: $%{y:.1f}B<extra></extra>'
    ),
    row=2, col=1
)

# 4. Model Performance
metrics_df = forecaster.get_metrics_summary().head(5)  # Top 5 models
fig.add_trace(
    go.Bar(
        x=metrics_df.index, 
        y=metrics_df['MAPE'],
        name='MAPE (%)', 
        marker_color=COLORS['primary'],
        marker_line=dict(width=2, color=COLORS['accent2']),
        hovertemplate='<b>%{x}</b><br>MAPE: %{y:.2f}%<extra></extra>'
    ),
    row=2, col=2
)

# Update axes labels
fig.update_xaxes(title_text="<b>Year</b>", title_font=dict(size=14, color=COLORS['text']), row=1, col=1, gridcolor=COLORS['grid'])
fig.update_xaxes(title_text="<b>Year</b>", title_font=dict(size=14, color=COLORS['text']), row=1, col=2, gridcolor=COLORS['grid'])
fig.update_xaxes(title_text="<b>Year</b>", title_font=dict(size=14, color=COLORS['text']), row=2, col=1, gridcolor=COLORS['grid'])
fig.update_xaxes(title_text="<b>Model</b>", title_font=dict(size=14, color=COLORS['text']), row=2, col=2, tickangle=-45, gridcolor=COLORS['grid'])

fig.update_yaxes(title_text="<b>Revenue ($B)</b>", title_font=dict(size=14, color=COLORS['text']), row=1, col=1, gridcolor=COLORS['grid'])
fig.update_yaxes(title_text="<b>Revenue ($B)</b>", title_font=dict(size=14, color=COLORS['text']), row=1, col=2, gridcolor=COLORS['grid'])
fig.update_yaxes(title_text="<b>Revenue ($B)</b>", title_font=dict(size=14, color=COLORS['text']), row=2, col=1, gridcolor=COLORS['grid'])
fig.update_yaxes(title_text="<b>MAPE (%)</b>", title_font=dict(size=14, color=COLORS['text']), row=2, col=2, gridcolor=COLORS['grid'])

# Update layout to match portfolio theme
fig.update_layout(
    title={
        'text': "<b style='font-size:28px;'>NVIDIA Revenue Forecasting Dashboard</b><br>" + 
                "<span style='font-size:16px; color:#C0C0C0;'>Multi-Model Predictive Analysis | 2016-2030</span>",
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 28, 'color': COLORS['text']}
    },
    showlegend=True,
    legend=dict(
        bgcolor='rgba(42, 42, 42, 0.9)',
        bordercolor=COLORS['primary'],
        borderwidth=1,
        font=dict(size=11, color=COLORS['text'])
    ),
    height=1100,
    plot_bgcolor=COLORS['paper'],
    paper_bgcolor=COLORS['background'],
    font=dict(family='Arial, sans-serif', size=12, color=COLORS['text']),
    hovermode='closest',
    hoverlabel=dict(
        bgcolor=COLORS['paper'],
        font_size=13,
        font_family="Arial, sans-serif",
        bordercolor=COLORS['primary']
    )
)

# Update subplot titles
for annotation in fig['layout']['annotations']:
    annotation['font'] = dict(size=16, color=COLORS['text'])

# Save
fig.write_html('../project_pages/revenue_forecast_dashboard.html')
print("✓ Styled dashboard created successfully!")

