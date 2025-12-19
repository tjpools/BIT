#!/usr/bin/env python3
"""
BitMine (BMNR) Tracker - Python Implementation
Fetches data from Yahoo Finance and generates HTML visualization
"""

import json
import urllib.request
from datetime import datetime, timedelta
import os
import math

def fetch_yahoo_finance(symbol, days=30):
    """Fetch stock data from Yahoo Finance"""
    now = int(datetime.now().timestamp())
    past = int((datetime.now() - timedelta(days=days)).timestamp())
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    url += f"?period1={past}&period2={now}&interval=1d"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            result = data['chart']['result'][0]
            
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            # Build data list
            data_points = []
            for i in range(len(timestamps)):
                if quotes['close'][i] is not None:
                    data_points.append({
                        'timestamp': datetime.fromtimestamp(timestamps[i]),
                        'open': quotes['open'][i],
                        'high': quotes['high'][i],
                        'low': quotes['low'][i],
                        'close': quotes['close'][i],
                        'volume': quotes['volume'][i]
                    })
            
            return data_points
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def calculate_statistics(data):
    """Calculate statistics from stock data"""
    if not data:
        return {}
    
    latest = data[-1]
    previous = data[-2] if len(data) > 1 else latest
    
    price_change = latest['close'] - previous['close']
    price_change_pct = (price_change / previous['close']) * 100
    
    # Volatility calculation
    closes = [d['close'] for d in data]
    returns = [math.log(closes[i] / closes[i-1]) for i in range(1, len(closes))]
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    volatility = math.sqrt(variance) * math.sqrt(252) * 100  # Annualized
    
    stats = {
        'current_price': round(latest['close'], 2),
        'previous_price': round(previous['close'], 2),
        'price_change': round(price_change, 2),
        'price_change_pct': round(price_change_pct, 2),
        'daily_high': round(max(d['high'] for d in data[-5:]), 2),
        'daily_low': round(min(d['low'] for d in data[-5:]), 2),
        'volume': int(latest['volume']),
        'volatility': round(volatility, 2),
        'last_update': latest['timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC')
    }
    
    return stats

def format_volume(vol):
    """Format volume numbers"""
    if vol >= 1_000_000:
        return f"{vol / 1_000_000:.2f}M"
    elif vol >= 1_000:
        return f"{vol / 1_000:.2f}K"
    return str(vol)

def generate_html(data, stats):
    """Generate HTML page"""
    os.makedirs('docs', exist_ok=True)
    
    # Generate simple ASCII chart for now (can add matplotlib later)
    chart_placeholder = "📊 Chart generation with matplotlib coming next..."
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BitMine (BMNR) Tracker</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        header {{
            background: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .subtitle {{ font-size: 1.1em; opacity: 0.9; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #ecf0f1;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        .chart-container {{
            padding: 30px;
            text-align: center;
            font-size: 1.2em;
            color: #7f8c8d;
        }}
        .epilogue {{
            padding: 30px;
            background: #34495e;
            color: white;
        }}
        .epilogue h2 {{
            margin-bottom: 15px;
            color: #ecf0f1;
        }}
        .epilogue p {{
            line-height: 1.6;
            margin-bottom: 10px;
        }}
        .filter-list {{
            list-style: none;
            padding: 20px;
        }}
        .filter-list li {{
            padding: 10px;
            margin: 5px 0;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            background: #2c3e50;
            color: white;
            font-size: 0.9em;
        }}
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
                <div class="stat-value">${stats['current_price']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">24h Change</div>
                <div class="stat-value {'positive' if stats['price_change'] >= 0 else 'negative'}">
                    {'+' if stats['price_change'] >= 0 else ''}{stats['price_change']} ({stats['price_change_pct']}%)
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Recent High</div>
                <div class="stat-value">${stats['daily_high']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Recent Low</div>
                <div class="stat-value">${stats['daily_low']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Volume</div>
                <div class="stat-value">{format_volume(stats['volume'])}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Volatility (Ann.)</div>
                <div class="stat-value">{stats['volatility']}%</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>Price History (30 Days)</h2>
            <p>{chart_placeholder}</p>
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
            <p>Last Updated: {stats['last_update']}</p>
            <p>Data source: Yahoo Finance | Auto-updated hourly via GitHub Actions</p>
        </footer>
    </div>
</body>
</html>
"""
    
    with open('docs/index.html', 'w') as f:
        f.write(html)
    
    print(f"✓ HTML generated: docs/index.html")

def save_csv(data):
    """Save data to CSV"""
    os.makedirs('data', exist_ok=True)
    
    with open('data/bmnr_data.csv', 'w') as f:
        f.write('timestamp,open,high,low,close,volume\n')
        for d in data:
            f.write(f"{d['timestamp']},{d['open']},{d['high']},{d['low']},{d['close']},{d['volume']}\n")
    
    print(f"✓ Data saved: data/bmnr_data.csv")

def main():
    print("=" * 50)
    print("BitMine (BMNR) Tracker - Data Fetch & Update")
    print("=" * 50)
    
    print("\n📊 Fetching BMNR data from Yahoo Finance...")
    data = fetch_yahoo_finance("BMNR", days=30)
    
    if not data:
        print("✗ Failed to fetch data")
        return
    
    print(f"✓ Fetched {len(data)} data points")
    
    print("\n💾 Saving data to CSV...")
    save_csv(data)
    
    print("\n📈 Calculating statistics...")
    stats = calculate_statistics(data)
    
    print(f"Current Price: ${stats['current_price']}")
    print(f"24h Change: {stats['price_change']} ({stats['price_change_pct']}%)")
    
    print("\n🌐 Generating HTML page...")
    generate_html(data, stats)
    
    print("\n" + "=" * 50)
    print("✓ Update complete!")
    print("=" * 50)
    print("\n💡 Open docs/index.html in your browser to view the tracker")

if __name__ == "__main__":
    main()
