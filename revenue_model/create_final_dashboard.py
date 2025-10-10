"""
Create final dashboard with full-screen charts, individual legends, and interpretations
"""

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

# Portfolio colors
COLORS = {
    'background': '#1a1a1a',
    'paper': '#2a2a2a',
    'text': '#E8E8E8',
    'primary': '#C0C0C0',
    'historical': '#3498DB',
    'bull': '#27AE60',
    'base': '#3498DB',
    'bear': '#E74C3C',
    'median': '#E74C3C'
}

# Create HTML with full-page layout
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>NVIDIA Revenue Forecasting Dashboard</title>
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            background: linear-gradient(135deg, {COLORS['background']} 0%, #2d2d2d 100%);
            color: {COLORS['text']};
            margin: 0;
            padding: 0;
            font-family: 'Arial', sans-serif;
        }}
        
        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .dashboard-header {{
            text-align: center;
            padding: 3rem 2rem;
            margin-bottom: 3rem;
            background: rgba(42, 42, 42, 0.8);
            border-radius: 15px;
            border: 1px solid {COLORS['primary']};
        }}
        
        .dashboard-header h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #999, #fff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }}
        
        .dashboard-header p {{
            color: {COLORS['primary']};
            font-size: 1.1rem;
        }}
        
        .chart-section {{
            margin-bottom: 5rem;
            background: rgba(42, 42, 42, 0.9);
            padding: 2.5rem;
            border-radius: 15px;
            border: 1px solid #444;
        }}
        
        .chart-title {{
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            color: {COLORS['text']};
            font-weight: bold;
            padding-bottom: 1rem;
            border-bottom: 2px solid {COLORS['primary']};
        }}
        
        .chart-container {{
            min-height: 600px;
            margin: 2rem 0;
            background: {COLORS['paper']};
            border-radius: 10px;
            padding: 1rem;
        }}
        
        .interpretation {{
            background: rgba(26, 26, 26, 0.6);
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid {COLORS['primary']};
            margin-top: 2rem;
            line-height: 1.8;
        }}
        
        .interpretation h3 {{
            color: {COLORS['primary']};
            font-size: 1.3rem;
            margin-bottom: 1rem;
        }}
        
        .interpretation h4 {{
            color: {COLORS['text']};
            font-size: 1.1rem;
            margin-top: 1.5rem;
            margin-bottom: 0.8rem;
        }}
        
        .interpretation p {{
            color: {COLORS['text']};
            margin-bottom: 1rem;
        }}
        
        .methodology {{
            background: rgba(52, 152, 219, 0.1);
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            border: 1px solid rgba(52, 152, 219, 0.3);
        }}
        
        .back-button {{
            display: inline-block;
            margin: 3rem 0;
            padding: 12px 30px;
            background: linear-gradient(45deg, #333, #444);
            color: {COLORS['text']};
            text-decoration: none;
            border-radius: 25px;
            border: 1px solid {COLORS['primary']};
            transition: all 0.3s ease;
            font-size: 1.1rem;
        }}
        
        .back-button:hover {{
            background: linear-gradient(45deg, #999, #fff);
            color: #333;
            transform: translateY(-2px);
        }}
        
        @media (max-width: 768px) {{
            .dashboard-header h1 {{
                font-size: 1.8rem;
            }}
            .chart-section {{
                padding: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-brand"></div>
        <div class="mobile-menu-toggle">
            <span></span>
            <span></span>
            <span></span>
        </div>
        <ul class="nav-links">
            <li><a href="../index.html">Home</a></li>
            <li><a href="../index.html#about">About</a></li>
            <li><a href="../index.html#projects">Projects</a></li>
            <li><a href="../index.html#contact">Contact</a></li>
        </ul>
    </nav>

    <div class="dashboard-container">
        <div class="dashboard-header">
            <h1><i class="fas fa-chart-line"></i> NVIDIA Revenue Forecasting Dashboard</h1>
            <p>Multi-Model Predictive Analysis | 2016-2030</p>
        </div>

        <!-- Chart 1: Scenario Analysis -->
        <div class="chart-section">
            <h2 class="chart-title">Scenario Analysis: Bull, Base & Bear Cases</h2>
            <div id="chart1" class="chart-container"></div>
            
            <div class="interpretation">
                <h3><i class="fas fa-lightbulb"></i> Interpretation</h3>
                <p>This chart presents three distinct revenue trajectories for NVIDIA through 2030, each representing fundamentally different technological and market outcomes. The historical data (2016-2025) shows NVIDIA's explosive growth from $5B to $131B, driven primarily by the AI revolution.</p>
                
                <h4>Bear Case ($480B by 2030 | 30% CAGR):</h4>
                <p>Assumes AI technology is reaching its law of diminishing returns. As the market matures, growth rates decline from current levels due to several factors: early adopters have completed their AI infrastructure investments, competition from AMD, Intel, and custom chips intensifies, and pricing pressure emerges as the technology commoditizes. This scenario reflects natural market saturation where exponential growth transitions to more sustainable linear expansion.</p>
                
                <h4>Base Case ($1,350B by 2030 | 60% CAGR):</h4>
                <p>Represents steady, sustained AI adoption across industries without dramatic acceleration or deceleration. This balanced view assumes continued data center expansion, growth in edge computing, automotive AI applications, and NVIDIA maintaining competitive advantages while facing realistic market pressures. This scenario accounts for both opportunities and challenges in a maturing AI market.</p>
                
                <h4>Bull Case ($4,392B by 2030 | 102% CAGR):</h4>
                <p>Assumes quantum computing will exponentially boost NVIDIA's revenue by enabling breakthrough applications impossible with classical computing. This paradigm shift would create entirely new markets in drug discovery, financial modeling, cryptography, and AI model training. NVIDIA's expertise in parallel processing and AI acceleration positions it as critical infrastructure for quantum-classical hybrid computing, capturing significant market share in this emerging multi-trillion dollar opportunity.</p>
                
                <div class="methodology">
                    <strong><i class="fas fa-cog"></i> Methodology:</strong> Growth rate-based forecasting using historical volatility analysis and Monte Carlo-derived growth parameters. Each scenario applies different CAGR assumptions to the 2025 baseline revenue of $130.5B, compounded annually through 2030.
                </div>
            </div>
        </div>

        <!-- Chart 2: Monte Carlo Simulation -->
        <div class="chart-section">
            <h2 class="chart-title">Monte Carlo Simulation: Probabilistic Forecast</h2>
            <div id="chart2" class="chart-container"></div>
            
            <div class="interpretation">
                <h3><i class="fas fa-lightbulb"></i> Interpretation</h3>
                <p>This probabilistic forecast uses 1,000 Monte Carlo simulations to quantify uncertainty and generate confidence intervals around revenue projections. Unlike single-point forecasts, this approach acknowledges that future outcomes exist within a range of possibilities influenced by numerous random variables.</p>
                
                <h4>Key Probabilistic Outcomes for 2030:</h4>
                <p><strong>P10 (10th Percentile - $263B):</strong> Represents the pessimistic boundary where only 10% of scenarios result in lower revenue. This conservative outcome suggests significant headwinds materialized.</p>
                
                <p><strong>Median (50th Percentile - $784B):</strong> The most statistically likely outcome where half of simulations exceed this value and half fall below. This represents the balanced expectation incorporating historical volatility patterns.</p>
                
                <p><strong>P90 (90th Percentile - $1,793B):</strong> The optimistic boundary where 90% of scenarios fall below this level. Achieving this outcome would require sustained exceptional growth with minimal setbacks.</p>
                
                <p><strong>80% Confidence Band (P10-P90):</strong> Statistical confidence that actual 2030 revenue will fall within this range, assuming historical volatility patterns persist and no fundamental market structure changes occur.</p>
                
                <div class="methodology">
                    <strong><i class="fas fa-cog"></i> Methodology:</strong> Monte Carlo simulation sampling from a normal distribution with mean growth rate (μ = 49.6%) and standard deviation (σ = 67.4%) derived from historical revenue data. Each of 1,000 iterations randomly samples annual growth rates for 5 years, compounding from the 2025 base. Percentiles calculated from the resulting distribution.
                </div>
            </div>
        </div>

        <!-- Chart 3: Multi-Model Comparison -->
        <div class="chart-section">
            <h2 class="chart-title">Multi-Model Forecast Comparison</h2>
            <div id="chart3" class="chart-container"></div>
            
            <div class="interpretation">
                <h3><i class="fas fa-lightbulb"></i> Interpretation</h3>
                <p>This chart compares nine distinct forecasting methodologies, each applying different mathematical assumptions to predict future revenue. The diversity of approaches provides perspective on model sensitivity and forecast robustness.</p>
                
                <h4>Key Model Categories:</h4>
                <p><strong>Machine Learning Models (Gradient Boosting, Random Forest):</strong> Achieved the best training performance with Gradient Boosting showing 0.03% MAPE. These ensemble methods capture non-linear patterns but may overfit to recent explosive growth, explaining their conservative forecasts around $130B.</p>
                
                <p><strong>Statistical Time Series (Exponential Smoothing):</strong> Applies adaptive weighting to recent observations with trend component. Produces moderate forecasts (~$478B by 2030) by smoothing volatility while maintaining growth momentum.</p>
                
                <p><strong>Polynomial Regression (degrees 2 & 3):</strong> Fits curves to historical data points. Higher-degree polynomials capture recent acceleration better, projecting more aggressive growth ($808B for degree 3) but risk overfitting to tail-end behavior.</p>
                
                <p><strong>Linear Regression:</strong> Assumes constant absolute growth rate. The most conservative approach ($125B) as it cannot capture exponential acceleration patterns evident in NVIDIA's recent performance.</p>
                
                <p><strong>Ensemble Forecast (white dashed line - $316B):</strong> Averages predictions from Polynomial degree 2, Exponential Smoothing, and Gradient Boosting to balance optimism and conservatism, reducing individual model bias.</p>
                
                <div class="methodology">
                    <strong><i class="fas fa-cog"></i> Methodology:</strong> Multiple regression techniques applied to historical revenue time series. ML models use scikit-learn implementations with default hyperparameters. Statistical models use statsmodels. All models trained on 2016-2025 data (10 observations), evaluated using MAE, RMSE, MAPE, and R² metrics. Ensemble combines three best-performing diverse models using simple averaging.
                </div>
            </div>
        </div>

        <!-- Chart 4: Model Performance -->
        <div class="chart-section">
            <h2 class="chart-title">Model Performance Metrics</h2>
            <div id="chart4" class="chart-container"></div>
            
            <div class="interpretation">
                <h3><i class="fas fa-lightbulb"></i> Interpretation</h3>
                <p>Mean Absolute Percentage Error (MAPE) measures average forecast accuracy on training data, with lower values indicating better historical fit. This chart reveals critical insights about model behavior and reliability.</p>
                
                <h4>Performance Analysis:</h4>
                <p><strong>Gradient Boosting (0.03% MAPE):</strong> Near-perfect training fit suggests potential overfitting. While technically superior on historical data, this model may not generalize well to unprecedented future scenarios, explaining its conservative forecasts.</p>
                
                <p><strong>Random Forest (9.5% MAPE):</strong> Strong performance with better generalization than Gradient Boosting. The ensemble nature provides robustness but still struggles with explosive recent growth patterns.</p>
                
                <p><strong>Exponential Smoothing (21.8% MAPE):</strong> Moderate accuracy reflects the challenge of capturing both steady growth (2016-2023) and explosive acceleration (2024-2025) in a single model.</p>
                
                <p><strong>Polynomial Models (35-65% MAPE):</strong> Higher error rates from attempting to fit complex curves to limited data points. Degree 3 outperforms degree 2 by better capturing recent acceleration.</p>
                
                <p><strong>Linear Regression (109% MAPE):</strong> Poor fit confirms NVIDIA's growth is fundamentally non-linear. This model's failure validates the need for more sophisticated approaches.</p>
                
                <div class="methodology">
                    <strong><i class="fas fa-cog"></i> Methodology:</strong> MAPE calculated as mean(|actual - predicted| / actual) × 100 on training period (2016-2025). Lower MAPE indicates better historical fit but doesn't guarantee future accuracy. Models with MAPE < 10% show excellent training performance, 10-25% good, 25-50% acceptable, >50% poor fit. Overfitting risk increases as MAPE approaches zero.
                </div>
            </div>
        </div>

        <a href="predictive-revenue-model.html" class="back-button">
            <i class="fas fa-arrow-left"></i> Back to Project Details
        </a>
    </div>

    <script src="../script.js"></script>
    <script>
        // Chart 1: Scenario Analysis
        const chart1Data = [
            {{
                x: {list(revenue_df['Year'].values)},
                y: {list(revenue_df['Revenue'].values)},
                mode: 'lines+markers',
                name: 'Historical',
                line: {{color: '{COLORS['historical']}', width: 4}},
                marker: {{size: 12, line: {{width: 2, color: 'white'}}}},
                hovertemplate: '<b>%{{x}}</b><br>Revenue: $%{{y:.1f}}B<extra></extra>'
            }},
            {{
                x: {list(analyzer.scenarios['Bull']['years'])},
                y: {list(analyzer.scenarios['Bull']['forecast'])},
                mode: 'lines+markers',
                name: 'Bull Case (Quantum Computing)',
                line: {{color: '{COLORS['bull']}', width: 4}},
                marker: {{size: 10}},
                hovertemplate: '<b>Bull Case</b><br>%{{x}}<br>$%{{y:.1f}}B<extra></extra>'
            }},
            {{
                x: {list(analyzer.scenarios['Base']['years'])},
                y: {list(analyzer.scenarios['Base']['forecast'])},
                mode: 'lines+markers',
                name: 'Base Case (Steady Growth)',
                line: {{color: '{COLORS['base']}', width: 4}},
                marker: {{size: 10}},
                hovertemplate: '<b>Base Case</b><br>%{{x}}<br>$%{{y:.1f}}B<extra></extra>'
            }},
            {{
                x: {list(analyzer.scenarios['Bear']['years'])},
                y: {list(analyzer.scenarios['Bear']['forecast'])},
                mode: 'lines+markers',
                name: 'Bear Case (Diminishing Returns)',
                line: {{color: '{COLORS['bear']}', width: 4}},
                marker: {{size: 10}},
                hovertemplate: '<b>Bear Case</b><br>%{{x}}<br>$%{{y:.1f}}B<extra></extra>'
            }}
        ];

        const chart1Layout = {{
            xaxis: {{title: '<b>Year</b>', gridcolor: '#444', color: '{COLORS['text']}'}},
            yaxis: {{title: '<b>Revenue ($B)</b>', gridcolor: '#444', color: '{COLORS['text']}'}},
            plot_bgcolor: '{COLORS['paper']}',
            paper_bgcolor: '{COLORS['paper']}',
            font: {{family: 'Arial', size: 12, color: '{COLORS['text']}'}},
            showlegend: true,
            legend: {{bgcolor: '{COLORS['paper']}', bordercolor: '{COLORS['primary']}', borderwidth: 1}},
            hovermode: 'closest',
            margin: {{l: 80, r: 40, t: 40, b: 80}}
        }};

        Plotly.newPlot('chart1', chart1Data, chart1Layout, {{responsive: true}});

        // Chart 2: Monte Carlo
        const years = {list(mc_results['years'])};
        const chart2Data = [
            {{
                x: {list(revenue_df['Year'].values)},
                y: {list(revenue_df['Revenue'].values)},
                mode: 'lines+markers',
                name: 'Historical',
                line: {{color: '{COLORS['historical']}', width: 4}},
                marker: {{size: 12, line: {{width: 2, color: 'white'}}}},
                hovertemplate: '<b>%{{x}}</b><br>Revenue: $%{{y:.1f}}B<extra></extra>'
            }},
            {{
                x: years,
                y: {list(mc_results['p90'])},
                mode: 'lines',
                name: 'P90 (Optimistic)',
                line: {{width: 0}},
                showlegend: true,
                hovertemplate: '<b>%{{x}}</b><br>P90: $%{{y:.1f}}B<extra></extra>'
            }},
            {{
                x: years,
                y: {list(mc_results['p10'])},
                mode: 'lines',
                name: '80% Confidence (P10-P90)',
                line: {{width: 0}},
                fill: 'tonexty',
                fillcolor: 'rgba(52, 152, 219, 0.3)',
                hovertemplate: '<b>%{{x}}</b><br>P10: $%{{y:.1f}}B<extra></extra>'
            }},
            {{
                x: years,
                y: {list(mc_results['median'])},
                mode: 'lines+markers',
                name: 'Median (P50)',
                line: {{color: '{COLORS['median']}', width: 4}},
                marker: {{size: 10}},
                hovertemplate: '<b>%{{x}}</b><br>Median: $%{{y:.1f}}B<extra></extra>'
            }}
        ];

        const chart2Layout = {{
            xaxis: {{title: '<b>Year</b>', gridcolor: '#444', color: '{COLORS['text']}'}},
            yaxis: {{title: '<b>Revenue ($B)</b>', gridcolor: '#444', color: '{COLORS['text']}'}},
            plot_bgcolor: '{COLORS['paper']}',
            paper_bgcolor: '{COLORS['paper']}',
            font: {{family: 'Arial', size: 12, color: '{COLORS['text']}'}},
            showlegend: true,
            legend: {{bgcolor: '{COLORS['paper']}', bordercolor: '{COLORS['primary']}', borderwidth: 1}},
            hovermode: 'closest',
            margin: {{l: 80, r: 40, t: 40, b: 80}}
        }};

        Plotly.newPlot('chart2', chart2Data, chart2Layout, {{responsive: true}});

        // Chart 3: Multi-Model Comparison
        const ensemble = {list(forecaster.forecasts['Ensemble']['Forecast'].values)};
        const ensemble_years = {list(forecaster.forecasts['Ensemble']['Year'].values)};
        
        const chart3Data = [
            {{
                x: {list(revenue_df['Year'].values)},
                y: {list(revenue_df['Revenue'].values)},
                mode: 'lines+markers',
                name: 'Historical',
                line: {{color: '{COLORS['historical']}', width: 4}},
                marker: {{size: 12, line: {{width: 2, color: 'white'}}}},
                hovertemplate: '<b>%{{x}}</b><br>Revenue: $%{{y:.1f}}B<extra></extra>'
            }},
            {{
                x: ensemble_years,
                y: ensemble,
                mode: 'lines+markers',
                name: 'Ensemble Forecast',
                line: {{color: 'white', width: 4, dash: 'dash'}},
                marker: {{size: 10}},
                hovertemplate: '<b>Ensemble</b><br>%{{x}}<br>$%{{y:.1f}}B<extra></extra>'
            }}
        ];
        
        // Add other models with opacity
        const modelColors = ['#E74C3C', '#9B59B6', '#3498DB', '#1ABC9C', '#F39C12'];
        let colorIdx = 0;
        const modelsToShow = ['Polynomial_3', 'Exponential Smoothing', 'Random Forest', 'Gradient Boosting', 'Linear Regression'];
        
        """ + "\n".join([
            f"chart3Data.push({{x: {list(forecaster.forecasts[model]['Year'].values)}, y: {list(forecaster.forecasts[model]['Forecast'].values)}, mode: 'lines', name: '{model}', line: {{width: 2}}, opacity: 0.6, hovertemplate: '<b>{model}</b><br>%{{x}}<br>$%{{y:.1f}}B<extra></extra>'}});"
            for model in ['Polynomial_3', 'Exponential Smoothing', 'Random Forest', 'Gradient Boosting', 'Linear Regression']
        ]) + f"""
        
        const chart3Layout = {{
            xaxis: {{title: '<b>Year</b>', gridcolor: '#444', color: '{COLORS['text']}'}},
            yaxis: {{title: '<b>Revenue ($B)</b>', gridcolor: '#444', color: '{COLORS['text']}'}},
            plot_bgcolor: '{COLORS['paper']}',
            paper_bgcolor: '{COLORS['paper']}',
            font: {{family: 'Arial', size: 12, color: '{COLORS['text']}'}},
            showlegend: true,
            legend: {{bgcolor: '{COLORS['paper']}', bordercolor: '{COLORS['primary']}', borderwidth: 1}},
            hovermode: 'closest',
            margin: {{l: 80, r: 40, t: 40, b: 80}}
        }};

        Plotly.newPlot('chart3', chart3Data, chart3Layout, {{responsive: true}});

        // Chart 4: Model Performance
        const metrics = {forecaster.get_metrics_summary().to_dict()};
        const modelNames = {list(forecaster.get_metrics_summary().index[:5])};
        const mapeValues = {list(forecaster.get_metrics_summary()['MAPE'].values[:5])};
        
        const chart4Data = [{{
            x: modelNames,
            y: mapeValues,
            type: 'bar',
            marker: {{
                color: '{COLORS['primary']}',
                line: {{color: 'white', width: 2}}
            }},
            hovertemplate: '<b>%{{x}}</b><br>MAPE: %{{y:.2f}}%<extra></extra>'
        }}];

        const chart4Layout = {{
            xaxis: {{title: '<b>Model</b>', tickangle: -45, gridcolor: '#444', color: '{COLORS['text']}'}},
            yaxis: {{title: '<b>MAPE (%)</b>', gridcolor: '#444', color: '{COLORS['text']}'}},
            plot_bgcolor: '{COLORS['paper']}',
            paper_bgcolor: '{COLORS['paper']}',
            font: {{family: 'Arial', size: 12, color: '{COLORS['text']}'}},
            showlegend: false,
            hovermode: 'closest',
            margin: {{l: 80, r: 40, t: 40, b: 120}}
        }};

        Plotly.newPlot('chart4', chart4Data, chart4Layout, {{responsive: true}});
    </script>
</body>
</html>
"""

# Write HTML file
with open('../project_pages/revenue_forecast_dashboard.html', 'w') as f:
    f.write(html_content)

print("✓ Final dashboard created with full-screen charts, individual legends, and interpretations!")

