using Dates

"""
Generate HTML page with stock data visualization
"""
function generate_html(df::DataFrame, stats::Dict, output_file::String="docs/index.html")
    mkpath(dirname(output_file))
    
    # Generate plot
    plot_file = joinpath(dirname(output_file), "price_chart.png")
    generate_plot(df, plot_file)
    
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BitMine (BMNR) Tracker</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            header {
                background: #2c3e50;
                color: white;
                padding: 30px;
                text-align: center;
            }
            h1 { font-size: 2.5em; margin-bottom: 10px; }
            .subtitle { font-size: 1.1em; opacity: 0.9; }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                padding: 30px;
                background: #ecf0f1;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .stat-label {
                font-size: 0.9em;
                color: #7f8c8d;
                text-transform: uppercase;
                margin-bottom: 5px;
            }
            .stat-value {
                font-size: 1.8em;
                font-weight: bold;
                color: #2c3e50;
            }
            .positive { color: #27ae60; }
            .negative { color: #e74c3c; }
            .chart-container {
                padding: 30px;
            }
            .chart-container img {
                width: 100%;
                height: auto;
                border-radius: 8px;
            }
            .epilogue {
                padding: 30px;
                background: #34495e;
                color: white;
            }
            .epilogue h2 {
                margin-bottom: 15px;
                color: #ecf0f1;
            }
            .epilogue p {
                line-height: 1.6;
                margin-bottom: 10px;
            }
            .filter-list {
                list-style: none;
                padding: 20px;
            }
            .filter-list li {
                padding: 10px;
                margin: 5px 0;
                background: rgba(255,255,255,0.1);
                border-radius: 5px;
            }
            footer {
                text-align: center;
                padding: 20px;
                background: #2c3e50;
                color: white;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🔷 BitMine (BMNR) Tracker</h1>
                <p class="subtitle">Rigorous Analysis Through Formal Systems</p>
            </header>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-label">Current Price</div>
                    <div class="stat-value">\$$(stats["current_price"])</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">24h Change</div>
                    <div class="stat-value $(stats["price_change"] >= 0 ? "positive" : "negative")">
                        $(stats["price_change"] >= 0 ? "+" : "")$(stats["price_change"]) ($(stats["price_change_pct"])%)
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">24h High</div>
                    <div class="stat-value">\$$(stats["daily_high"])</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">24h Low</div>
                    <div class="stat-value">\$$(stats["daily_low"])</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Volume</div>
                    <div class="stat-value">$(format_volume(stats["volume"]))</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Volatility (Ann.)</div>
                    <div class="stat-value">$(stats["volatility"])%</div>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>Price History (30 Days)</h2>
                <img src="price_chart.png" alt="BMNR Price Chart">
            </div>
            
            <div class="epilogue">
                <h2>📐 The Intellectual Filter</h2>
                <p>This tracker applies rigorous epistemological principles to evaluate market claims:</p>
                <ul class="filter-list">
                    <li><strong>Galois Principle:</strong> Small cases lie about general behavior</li>
                    <li><strong>GEB/Formal Systems:</strong> Distinguish syntax from semantics</li>
                    <li><strong>Protein Complexity:</strong> Emergent causality changes with scale</li>
                    <li><strong>Assembly Discipline:</strong> Understand constraints before abstraction</li>
                    <li><strong>Toy Universe Method:</strong> Prove in constrained systems first</li>
                </ul>
                <p><em>Structure determines solvability. Formal foundations before claims.</em></p>
            </div>
            
            <footer>
                <p>Last Updated: $(stats["last_update"])</p>
                <p>Data source: Yahoo Finance | Auto-updated hourly via GitHub Actions</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    write(output_file, html)
    println("HTML generated: $output_file")
end

"""
Generate price chart using Python matplotlib (fallback)
"""
function generate_plot(df::DataFrame, output_file::String)
    # Create Python script to generate chart
    python_script = """
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Read data from CSV
df = pd.read_csv('data/bmnr_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Create figure
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df['timestamp'], df['close'], linewidth=2, color='#3498db', label='BMNR Close Price')

# Formatting
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Price (USD)', fontsize=12)
ax.set_title('BitMine (BMNR) Price History', fontsize=14, fontweight='bold')
ax.legend(loc='upper right')
ax.grid(True, linestyle=':', alpha=0.6)

# Format x-axis dates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
plt.xticks(rotation=45)

# Tight layout
plt.tight_layout()
plt.savefig('$output_file', dpi=150, bbox_inches='tight')
print('Plot saved: $output_file')
"""
    
    # Write and execute Python script
    script_file = "generate_plot.py"
    write(script_file, python_script)
    
    try
        run(`python3 $script_file`)
        rm(script_file)
    catch e
        @warn "Could not generate plot with Python. Install matplotlib: pip install matplotlib pandas"
        # Create simple text-based chart indicator
        write(output_file * ".txt", "Chart generation requires Python with matplotlib and pandas")
    end
end

"""
Format large numbers (volume)
"""
function format_volume(vol::Int)
    if vol >= 1_000_000
        return string(round(vol / 1_000_000, digits=2), "M")
    elseif vol >= 1_000
        return string(round(vol / 1_000, digits=2), "K")
    else
        return string(vol)
    end
end
