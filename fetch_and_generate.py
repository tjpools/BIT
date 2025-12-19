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
import time
import random
import logging

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fetch_and_generate.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def validate_stock_data(data_point):
    """
    Validate stock data for integrity and sanity
    
    Checks:
    - Required fields exist
    - Prices are positive and within reasonable bounds
    - High >= Low (no data corruption)
    - Volume is non-negative
    
    Raises:
        ValueError: If data is invalid with descriptive message
    """
    required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    
    # Check required fields
    for field in required_fields:
        if field not in data_point:
            raise ValueError(f"Missing required field: {field}")
        if data_point[field] is None:
            raise ValueError(f"Field '{field}' is None")
    
    # Price sanity checks
    prices = [data_point['open'], data_point['high'], data_point['low'], data_point['close']]
    
    for price_name, price in zip(['open', 'high', 'low', 'close'], prices):
        if price <= 0:
            raise ValueError(f"{price_name} price must be positive, got {price}")
        if price > 1_000_000:  # $1M threshold for sanity
            raise ValueError(f"{price_name} price {price} exceeds sanity threshold ($1M)")
    
    # Data corruption checks
    if data_point['high'] < data_point['low']:
        raise ValueError(
            f"Data corruption: high ({data_point['high']}) < low ({data_point['low']})"
        )
    
    # Volume sanity check
    if data_point['volume'] < 0:
        raise ValueError(f"Volume cannot be negative, got {data_point['volume']}")
    
    return True

def fetch_with_retry(url, headers, max_retries=3, initial_timeout=10):
    """
    Fetch URL with exponential backoff retry logic
    
    Args:
        url: URL to fetch
        headers: HTTP headers dict
        max_retries: Maximum number of retry attempts
        initial_timeout: Initial timeout in seconds
    
    Returns:
        Response data as string
    
    Raises:
        Exception: If all retries fail
    """
    timeout = initial_timeout
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching {url} (attempt {attempt + 1}/{max_retries})")
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                logger.info(f"Successfully fetched data (status: {response.status})")
                return response.read().decode()
                
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limited
                # Exponential backoff with jitter
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limited (429). Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
                timeout *= 2  # Increase timeout for next attempt
                
            elif e.code >= 500:  # Server error
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Server error ({e.code}). Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
                
            else:
                logger.error(f"HTTP error {e.code}: {e.reason}")
                raise
                
        except urllib.error.URLError as e:
            logger.warning(f"URL error: {e.reason}. Retrying...")
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
    
    raise Exception(f"Failed to fetch data after {max_retries} attempts")

def fetch_yahoo_finance(symbol, days=30):
    """Fetch stock data from Yahoo Finance with retry logic and validation"""
    logger.info(f"Fetching {symbol} data for last {days} days")
    now = int(datetime.now().timestamp())
    past = int((datetime.now() - timedelta(days=days)).timestamp())
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    url += f"?period1={past}&period2={now}&interval=1d"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # Use retry logic for fetching
        response_data = fetch_with_retry(url, headers)
        data = json.loads(response_data)
        
        # Validate response structure
        if 'chart' not in data or 'result' not in data['chart']:
            logger.error("Invalid response structure from Yahoo Finance")
            raise ValueError("Invalid API response structure")
        
        if not data['chart']['result']:
            logger.error(f"No data returned for symbol {symbol}")
            raise ValueError(f"No data available for symbol {symbol}")
        
        result = data['chart']['result'][0]
        
        timestamps = result['timestamp']
        quotes = result['indicators']['quote'][0]
        
        # Build data list
        data_points = []
        invalid_count = 0
        
        for i in range(len(timestamps)):
            if quotes['close'][i] is not None:
                try:
                    data_point = {
                        'timestamp': datetime.fromtimestamp(timestamps[i]),
                        'open': quotes['open'][i],
                        'high': quotes['high'][i],
                        'low': quotes['low'][i],
                        'close': quotes['close'][i],
                        'volume': quotes['volume'][i]
                    }
                    
                    # Validate data point
                    validate_stock_data(data_point)
                    data_points.append(data_point)
                    
                except ValueError as e:
                    invalid_count += 1
                    logger.warning(f"Invalid data point at index {i}: {e}")
                    continue
        
        if invalid_count > 0:
            logger.warning(f"Skipped {invalid_count} invalid data points")
        
        logger.info(f"Successfully fetched {len(data_points)} valid data points")
        return data_points
        
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}", exc_info=True)
        return []

def calculate_statistics(data):
    """Calculate statistics from stock data"""
    logger.info("Calculating statistics")
    
    if not data:
        logger.warning("No data provided for statistics calculation")
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
    
    logger.info(f"Statistics calculated: Current price ${stats['current_price']}, Change {stats['price_change_pct']}%")
    return stats

def format_volume(vol):
    """Format volume numbers"""
    if vol >= 1_000_000:
        return f"{vol / 1_000_000:.2f}M"
    elif vol >= 1_000:
        return f"{vol / 1_000:.2f}K"
    return str(vol)

def generate_html(data, stats):
    """Generate HTML page with Content Security Policy"""
    logger.info("Generating HTML page")
    os.makedirs('docs', exist_ok=True)
    
    # Generate simple ASCII chart for now (can add matplotlib later)
    chart_placeholder = "📊 Chart generation with matplotlib coming next..."
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self' https://query1.finance.yahoo.com https://query2.finance.yahoo.com; img-src 'self' data:; font-src 'self';">
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
    
    logger.info("HTML generated: docs/index.html")
    print(f"✓ HTML generated: docs/index.html")

def save_csv(data):
    """Save data to CSV"""
    logger.info("Saving data to CSV")
    os.makedirs('data', exist_ok=True)
    
    with open('data/bmnr_data.csv', 'w') as f:
        f.write('timestamp,open,high,low,close,volume\n')
        for d in data:
            f.write(f"{d['timestamp']},{d['open']},{d['high']},{d['low']},{d['close']},{d['volume']}\n")
    
    logger.info(f"Data saved: data/bmnr_data.csv ({len(data)} records)")
    print(f"✓ Data saved: data/bmnr_data.csv")

def main():
    logger.info("=" * 50)
    logger.info("BitMine (BMNR) Tracker - Data Fetch & Update")
    logger.info("=" * 50)
    
    print("=" * 50)
    print("BitMine (BMNR) Tracker - Data Fetch & Update")
    print("=" * 50)
    
    print("\n📊 Fetching BMNR data from Yahoo Finance...")
    logger.info("Starting data fetch for BMNR")
    data = fetch_yahoo_finance("BMNR", days=30)
    
    if not data:
        logger.error("Failed to fetch data - exiting")
        print("✗ Failed to fetch data")
        return
    
    logger.info(f"Fetched {len(data)} data points successfully")
    print(f"✓ Fetched {len(data)} data points")
    
    print("\n💾 Saving data to CSV...")
    save_csv(data)
    
    print("\n📈 Calculating statistics...")
    stats = calculate_statistics(data)
    
    print(f"Current Price: ${stats['current_price']}")
    print(f"24h Change: {stats['price_change']} ({stats['price_change_pct']}%)")
    
    print("\n🌐 Generating HTML page...")
    generate_html(data, stats)
    
    logger.info("Update complete!")
    print("\n" + "=" * 50)
    print("✓ Update complete!")
    print("=" * 50)
    print("\n💡 Open docs/index.html in your browser to view the tracker")

if __name__ == "__main__":
    main()
