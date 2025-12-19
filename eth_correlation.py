#!/usr/bin/env python3
"""
ETH-BMNR Correlation Analysis
Tests the claim: "ETH would get this going"
"""

import json
import urllib.request
from datetime import datetime, timedelta
import math
import logging
import os

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/eth_correlation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_crypto_data(symbol, days=30):
    """Fetch cryptocurrency data from Yahoo Finance"""
    logger.info(f"Fetching {symbol} data for {days} days")
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
                        'close': quotes['close'][i]
                    })
            
            logger.info(f"Successfully fetched {len(data_points)} data points for {symbol}")
            return data_points
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}", exc_info=True)
        print(f"Error fetching {symbol}: {e}")
        return []

def calculate_returns(data):
    """Calculate daily returns"""
    closes = [d['close'] for d in data]
    returns = []
    for i in range(1, len(closes)):
        ret = (closes[i] - closes[i-1]) / closes[i-1]
        returns.append(ret)
    return returns

def calculate_correlation(returns1, returns2):
    """Calculate Pearson correlation coefficient"""
    if len(returns1) != len(returns2) or len(returns1) == 0:
        return None
    
    n = len(returns1)
    mean1 = sum(returns1) / n
    mean2 = sum(returns2) / n
    
    numerator = sum((returns1[i] - mean1) * (returns2[i] - mean2) for i in range(n))
    
    sum_sq1 = sum((r - mean1) ** 2 for r in returns1)
    sum_sq2 = sum((r - mean2) ** 2 for r in returns2)
    
    denominator = math.sqrt(sum_sq1 * sum_sq2)
    
    if denominator == 0:
        return None
    
    return numerator / denominator

def main():
    logger.info("=" * 70)
    logger.info("Starting ETH-BMNR Correlation Analysis")
    logger.info("=" * 70)
    
    print("=" * 70)
    print("ETH-BMNR Correlation Analysis")
    print("Testing the claim: 'ETH would get this going'")
    print("=" * 70)
    
    print("\n📊 Fetching ETH-USD data...")
    eth_data = fetch_crypto_data("ETH-USD", days=30)
    
    print("📊 Fetching BMNR data...")
    bmnr_data = fetch_crypto_data("BMNR", days=30)
    
    if not eth_data or not bmnr_data:
        print("✗ Failed to fetch data")
        return
    
    print(f"✓ ETH: {len(eth_data)} data points")
    print(f"✓ BMNR: {len(bmnr_data)} data points")
    
    # Align data by date
    eth_dict = {d['timestamp'].date(): d['close'] for d in eth_data}
    bmnr_dict = {d['timestamp'].date(): d['close'] for d in bmnr_data}
    
    common_dates = sorted(set(eth_dict.keys()) & set(bmnr_dict.keys()))
    
    if len(common_dates) < 2:
        print("✗ Not enough overlapping data points")
        return
    
    print(f"✓ {len(common_dates)} overlapping trading days")
    
    # Create aligned data
    aligned_eth = [eth_dict[date] for date in common_dates]
    aligned_bmnr = [bmnr_dict[date] for date in common_dates]
    
    # Calculate returns
    eth_returns = calculate_returns([{'close': c} for c in aligned_eth])
    bmnr_returns = calculate_returns([{'close': c} for c in aligned_bmnr])
    
    # Calculate correlation
    correlation = calculate_correlation(eth_returns, bmnr_returns)
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    if correlation is not None:
        print(f"\n📈 Correlation Coefficient: {correlation:.4f}")
        print(f"   Coefficient of Determination (R²): {correlation**2:.4f}")
        
        # Interpretation
        print("\n📊 Interpretation:")
        abs_corr = abs(correlation)
        
        if abs_corr < 0.3:
            strength = "WEAK"
            color = "🟡"
        elif abs_corr < 0.7:
            strength = "MODERATE"
            color = "🟠"
        else:
            strength = "STRONG"
            color = "🔴"
        
        direction = "POSITIVE" if correlation > 0 else "NEGATIVE"
        
        print(f"   {color} {strength} {direction} correlation")
        
        if abs_corr < 0.3:
            print(f"   → ETH and BMNR move largely independently")
        elif abs_corr < 0.5:
            print(f"   → Some relationship, but many other factors at play")
        elif abs_corr < 0.7:
            print(f"   → Notable correlation, but not deterministic")
        else:
            print(f"   → Strong correlation - movements are related")
        
        print(f"\n   R² = {correlation**2:.4f} means {correlation**2*100:.1f}% of BMNR's")
        print(f"   variance can be explained by ETH's movements")
        
        print("\n🔬 Assembly Programmer's Translation:")
        print(f"   if (ETH moves X%), expect BMNR to move ~{correlation:.2f}*X%")
        print(f"   (with {(1-correlation**2)*100:.1f}% unexplained variance)")
        
        # Verdict on the claim
        print("\n⚖️  VERDICT on 'ETH would get this going':")
        if abs_corr < 0.3:
            print("   ❌ CLAIM UNSUPPORTED - Correlation is too weak")
            print("      ETH price changes do NOT reliably drive BMNR")
        elif abs_corr < 0.5:
            print("   ⚠️  CLAIM PARTIALLY SUPPORTED - Weak to moderate correlation")
            print("      ETH may have SOME influence, but other factors dominate")
        elif abs_corr < 0.7:
            print("   ⚠️  CLAIM SUPPORTED - Moderate correlation exists")
            print("      ETH movements DO relate to BMNR, but aren't the only factor")
        else:
            print("   ✓ CLAIM STRONGLY SUPPORTED - Strong correlation")
            print("      ETH and BMNR move together significantly")
        
        # Statistical significance note
        n = len(eth_returns)
        print(f"\n📝 Note: Based on n={n} data points ({len(common_dates)} days)")
        if n < 10:
            print("   ⚠️  WARNING: Small sample size - correlation may not be reliable")
    else:
        print("✗ Could not calculate correlation")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
