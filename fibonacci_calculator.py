#!/usr/bin/env python3
"""
Fibonacci Retracement Calculator
Tests predictions like "$53.63 at the 618 Fibonacci level"
"""

import json
import urllib.request
from datetime import datetime, timedelta

def fetch_stock_data(symbol, days=90):
    """Fetch stock data"""
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
            
            data_points = []
            for i in range(len(timestamps)):
                if quotes['close'][i] is not None:
                    data_points.append({
                        'timestamp': datetime.fromtimestamp(timestamps[i]),
                        'high': quotes['high'][i],
                        'low': quotes['low'][i],
                        'close': quotes['close'][i]
                    })
            
            return data_points
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return []

def calculate_fibonacci_levels(low, high, direction="uptrend"):
    """
    Calculate Fibonacci retracement levels
    
    Fibonacci ratios:
    - 0.000 (0%)
    - 0.236 (23.6%)
    - 0.382 (38.2%)
    - 0.500 (50%)
    - 0.618 (61.8%) - The Golden Ratio minus 1
    - 0.786 (78.6%)
    - 1.000 (100%)
    
    For extensions beyond 100%:
    - 1.618 (161.8%) - The Golden Ratio
    - 2.618 (261.8%)
    """
    
    price_range = high - low
    
    levels = {
        '0.0% (Low)': low,
        '23.6%': low + price_range * 0.236,
        '38.2%': low + price_range * 0.382,
        '50.0%': low + price_range * 0.500,
        '61.8%': low + price_range * 0.618,  # THE GOLDEN RATIO LEVEL
        '78.6%': low + price_range * 0.786,
        '100% (High)': high,
        '161.8% Extension': high + price_range * 0.618,
        '261.8% Extension': high + price_range * 1.618,
    }
    
    return levels

def find_swing_points(data, lookback=20):
    """Find significant swing high and swing low"""
    closes = [d['close'] for d in data]
    highs = [d['high'] for d in data]
    lows = [d['low'] for d in data]
    
    # Find recent swing high and low
    recent_high = max(highs[-lookback:])
    recent_low = min(lows[-lookback:])
    
    # Find overall period high and low
    period_high = max(highs)
    period_low = min(lows)
    
    # Find dates
    recent_high_date = data[[d['high'] for d in data].index(recent_high)]['timestamp']
    recent_low_date = data[[d['low'] for d in data].index(recent_low)]['timestamp']
    
    return {
        'recent_high': recent_high,
        'recent_low': recent_low,
        'recent_high_date': recent_high_date,
        'recent_low_date': recent_low_date,
        'period_high': period_high,
        'period_low': period_low
    }

def analyze_claim(target_price, current_price, fib_levels):
    """Analyze a specific Fibonacci claim"""
    closest_level = None
    closest_diff = float('inf')
    
    for level_name, level_price in fib_levels.items():
        diff = abs(level_price - target_price)
        if diff < closest_diff:
            closest_diff = diff
            closest_level = (level_name, level_price)
    
    return closest_level, closest_diff

def main():
    print("=" * 70)
    print("Fibonacci Retracement Calculator")
    print("Testing claim: '$53.63 at the 618 Fibonacci level'")
    print("=" * 70)
    
    print("\n📊 Fetching BMNR data (90 days)...")
    data = fetch_stock_data("BMNR", days=90)
    
    if not data:
        print("✗ Failed to fetch data")
        return
    
    print(f"✓ Fetched {len(data)} data points")
    
    current_price = data[-1]['close']
    print(f"\n💰 Current Price: ${current_price:.2f}")
    
    # Find swing points
    swing = find_swing_points(data, lookback=30)
    
    print(f"\n📊 Recent Swing Analysis (30 days):")
    print(f"   High: ${swing['recent_high']:.2f} on {swing['recent_high_date'].strftime('%Y-%m-%d')}")
    print(f"   Low:  ${swing['recent_low']:.2f} on {swing['recent_low_date'].strftime('%Y-%m-%d')}")
    
    print(f"\n📊 Period High/Low (90 days):")
    print(f"   High: ${swing['period_high']:.2f}")
    print(f"   Low:  ${swing['period_low']:.2f}")
    
    # Calculate Fibonacci levels for different scenarios
    print("\n" + "=" * 70)
    print("FIBONACCI RETRACEMENT LEVELS")
    print("=" * 70)
    
    # Scenario 1: Recent swing (30 days)
    print(f"\n📐 Scenario 1: Recent Swing ({swing['recent_low']:.2f} to {swing['recent_high']:.2f})")
    print("-" * 70)
    fib_recent = calculate_fibonacci_levels(swing['recent_low'], swing['recent_high'])
    
    for level, price in fib_recent.items():
        marker = "  ← CURRENT" if abs(price - current_price) < 1 else ""
        print(f"   {level:20s} ${price:8.2f}{marker}")
    
    # Scenario 2: Period high/low (90 days)
    print(f"\n📐 Scenario 2: Period Range ({swing['period_low']:.2f} to {swing['period_high']:.2f})")
    print("-" * 70)
    fib_period = calculate_fibonacci_levels(swing['period_low'], swing['period_high'])
    
    for level, price in fib_period.items():
        marker = "  ← CURRENT" if abs(price - current_price) < 1 else ""
        print(f"   {level:20s} ${price:8.2f}{marker}")
    
    # Analyze the specific claim: $53.63 at 618 level
    print("\n" + "=" * 70)
    print("CLAIM ANALYSIS: '$53.63 at the 618 Fibonacci level'")
    print("=" * 70)
    
    target_price = 53.63
    
    print(f"\n🎯 Target: ${target_price}")
    print(f"💰 Current: ${current_price:.2f}")
    print(f"📊 Distance: ${target_price - current_price:.2f} ({((target_price/current_price - 1)*100):.1f}% move required)")
    
    # Check recent swing 61.8% level
    recent_618 = fib_recent['61.8%']
    period_618 = fib_period['61.8%']
    
    print(f"\n📐 61.8% Levels:")
    print(f"   Recent Swing: ${recent_618:.2f} (diff: ${abs(target_price - recent_618):.2f})")
    print(f"   Period Range: ${period_618:.2f} (diff: ${abs(target_price - period_618):.2f})")
    
    # Find what level $53.63 actually represents
    print(f"\n🔍 What does ${target_price} represent?")
    
    closest_recent, diff_recent = analyze_claim(target_price, current_price, fib_recent)
    closest_period, diff_period = analyze_claim(target_price, current_price, fib_period)
    
    print(f"\n   In Recent Swing: Closest to {closest_recent[0]} (${closest_recent[1]:.2f})")
    print(f"   Difference: ${diff_recent:.2f}")
    
    print(f"\n   In Period Range: Closest to {closest_period[0]} (${closest_period[1]:.2f})")
    print(f"   Difference: ${diff_period:.2f}")
    
    # Reverse engineer: what swing would give $53.63 at 61.8%?
    print(f"\n🔬 Reverse Engineering:")
    print(f"   For ${target_price} to be the 61.8% level...")
    
    # If target is 61.8% retracement from low to high:
    # target = low + (high - low) * 0.618
    # Solving for different scenarios:
    
    # Assuming current low, what high?
    required_high = (target_price - swing['recent_low']) / 0.618 + swing['recent_low']
    print(f"   With recent low ${swing['recent_low']:.2f}, need high of ${required_high:.2f}")
    
    # Assuming period low, what high?
    required_high_period = (target_price - swing['period_low']) / 0.618 + swing['period_low']
    print(f"   With period low ${swing['period_low']:.2f}, need high of ${required_high_period:.2f}")
    
    print("\n⚖️  VERDICT:")
    
    if diff_recent < 5 or diff_period < 5:
        print("   ✓ CLAIM IS REASONABLY ACCURATE")
        print(f"     ${target_price} aligns with a Fibonacci level")
    elif diff_recent < 10 or diff_period < 10:
        print("   ⚠️  CLAIM IS APPROXIMATE")
        print(f"     ${target_price} is close to, but not exactly at 61.8%")
    else:
        print("   ❌ CLAIM IS QUESTIONABLE")
        print(f"     ${target_price} doesn't align with standard 61.8% calculations")
        print(f"     May be using different swing points or extensions")
    
    print("\n📝 Assembly Programmer's Note:")
    print("   Fibonacci retracements are DESCRIPTIVE, not PREDICTIVE")
    print("   They describe levels where traders might act, not where price WILL go")
    print("   No causal mechanism - just pattern recognition in human behavior")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
