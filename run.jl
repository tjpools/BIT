#!/usr/bin/env julia

# Standalone script - no package dependencies on Plots
# Install: julia -e 'using Pkg; Pkg.add(["HTTP", "JSON3", "DataFrames", "CSV"])'

using HTTP
using JSON3
using DataFrames
using Dates
using CSV

# Fetch stock data
function fetch_yahoo_finance(symbol::String)
    url = "https://query1.finance.yahoo.com/v8/finance/chart/$(symbol)"
    params = Dict(
        "period1" => string(Int(floor(datetime2unix(now() - Day(30))))),
        "period2" => string(Int(floor(datetime2unix(now())))),
        "interval" => "1h"
    )
    query_string = join(["$k=$v" for (k, v) in params], "&")
    full_url = "$url?$query_string"
    
    try
        response = HTTP.get(full_url)
        data = JSON3.read(String(response.body))
        result = data.chart.result[1]
        
        df = DataFrame(
            timestamp = unix2datetime.(result.timestamp),
            open = result.indicators.quote[1].open,
            high = result.indicators.quote[1].high,
            low = result.indicators.quote[1].low,
            close = result.indicators.quote[1].close,
            volume = result.indicators.quote[1].volume
        )
        dropmissing!(df)
        return df
    catch e
        @error "Failed to fetch data" exception=e
        return DataFrame()
    end
end

# Calculate statistics
function calculate_statistics(df::DataFrame)
    latest, previous = df[end, :], df[end-1, :]
    price_change = latest.close - previous.close
    returns = diff(log.(df.close))
    
    Dict(
        "current_price" => round(latest.close, digits=2),
        "price_change" => round(price_change, digits=2),
        "price_change_pct" => round((price_change / previous.close) * 100, digits=2),
        "daily_high" => round(maximum(df.high[end-min(23, end-1):end]), digits=2),
        "daily_low" => round(minimum(df.low[end-min(23, end-1):end]), digits=2),
        "volume" => Int(latest.volume),
        "volatility" => round(std(returns) * sqrt(252) * 100, digits=2),
        "last_update" => Dates.format(latest.timestamp, "yyyy-mm-dd HH:MM:SS UTC")
    )
end

# Generate HTML
function generate_html(df::DataFrame, stats::Dict)
    mkpath("docs")
    mkpath("data")
    
    # Save data
    CSV.write("data/bmnr_data.csv", df)
    
    # Format volume
    vol_str = stats["volume"] >= 1_000_000 ? string(round(stats["volume"]/1e6, digits=2), "M") :
              stats["volume"] >= 1_000 ? string(round(stats["volume"]/1e3, digits=2), "K") :
              string(stats["volume"])
    
    change_class = stats["price_change"] >= 0 ? "positive" : "negative"
    change_sign = stats["price_change"] >= 0 ? "+" : ""
    
    html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BitMine (BMNR) Tracker</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
.container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); overflow: hidden; }
header { background: #2c3e50; color: white; padding: 30px; text-align: center; }
h1 { font-size: 2.5em; margin-bottom: 10px; }
.subtitle { font-size: 1.1em; opacity: 0.9; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; background: #ecf0f1; }
.stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.stat-label { font-size: 0.9em; color: #7f8c8d; text-transform: uppercase; margin-bottom: 5px; }
.stat-value { font-size: 1.8em; font-weight: bold; color: #2c3e50; }
.positive { color: #27ae60; }
.negative { color: #e74c3c; }
.epilogue { padding: 30px; background: #34495e; color: white; }
.epilogue h2 { margin-bottom: 15px; color: #ecf0f1; }
.epilogue p { line-height: 1.6; margin-bottom: 10px; }
.filter-list { list-style: none; padding: 20px; }
.filter-list li { padding: 10px; margin: 5px 0; background: rgba(255,255,255,0.1); border-radius: 5px; }
footer { text-align: center; padding: 20px; background: #2c3e50; color: white; font-size: 0.9em; }
.chart-note { padding: 30px; text-align: center; color: #7f8c8d; font-style: italic; }
</style>
</head>
<body>
<div class="container">
<header><h1>🔷 BitMine (BMNR) Tracker</h1><p class="subtitle">Rigorous Analysis Through Formal Systems</p></header>
<div class="stats">
<div class="stat-card"><div class="stat-label">Current Price</div><div class="stat-value">\$$(stats["current_price"])</div></div>
<div class="stat-card"><div class="stat-label">24h Change</div><div class="stat-value $change_class">$change_sign$(stats["price_change"]) ($(stats["price_change_pct"])%)</div></div>
<div class="stat-card"><div class="stat-label">24h High</div><div class="stat-value">\$$(stats["daily_high"])</div></div>
<div class="stat-card"><div class="stat-label">24h Low</div><div class="stat-value">\$$(stats["daily_low"])</div></div>
<div class="stat-card"><div class="stat-label">Volume</div><div class="stat-value">$vol_str</div></div>
<div class="stat-card"><div class="stat-label">Volatility (Ann.)</div><div class="stat-value">$(stats["volatility"])%</div></div>
</div>
<div class="chart-note"><p>📊 Chart generation requires Python matplotlib. Data available in <a href="../data/bmnr_data.csv">CSV format</a>.</p></div>
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
<footer><p>Last Updated: $(stats["last_update"])</p><p>Data source: Yahoo Finance</p></footer>
</div>
</body>
</html>"""
    
    write("docs/index.html", html)
    println("✓ Generated docs/index.html")
end

# Main
println("="^50)
println("BitMine (BMNR) Tracker")
println("="^50)
println("\n📊 Fetching data...")
df = fetch_yahoo_finance("BMNR")
if !isempty(df)
    println("✓ Fetched $(nrow(df)) data points")
    stats = calculate_statistics(df)
    println("Current: \$$(stats["current_price"]) ($(stats["price_change_pct"])%)")
    generate_html(df, stats)
    println("\n✓ Complete! Open docs/index.html")
else
    println("❌ Failed to fetch data")
end
