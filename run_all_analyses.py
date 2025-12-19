#!/usr/bin/env python3
"""
BitMine Immersion - Complete Analysis Suite
Runs all analysis tools in sequence
"""

import subprocess
import sys
from datetime import datetime

def run_command(cmd, description):
    """Run a command and display results"""
    print("\n" + "=" * 80)
    print(f"▶️  {description}")
    print("=" * 80)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        if result.returncode != 0:
            print(f"⚠️  Warning: {description} returned non-zero exit code")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "BitMine Immersion - Full Analysis" + " " * 25 + "║")
    print("║" + " " * 20 + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = {}
    
    # 1. Fetch data and generate tracker
    results['tracker'] = run_command(
        'python3 fetch_and_generate.py',
        'Stock Data Tracker'
    )
    
    # 2. ETH correlation
    results['eth'] = run_command(
        'python3 eth_correlation.py',
        'ETH Correlation Analysis'
    )
    
    # 3. Fibonacci calculator
    results['fibonacci'] = run_command(
        'python3 fibonacci_calculator.py',
        'Fibonacci Retracement Calculator'
    )
    
    # 4. Prediction tracker status
    results['predictions'] = run_command(
        'python3 prediction_tracker.py',
        'Prediction Tracker Status'
    )
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 ANALYSIS COMPLETE")
    print("=" * 80)
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\n✅ Successful: {success_count}/{total_count}")
    
    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"   {status} {name.title()}")
    
    print("\n📁 Output Files:")
    print("   • docs/index.html         - Interactive dashboard")
    print("   • data/bmnr_data.csv      - Historical price data")
    print("   • data/predictions.json   - Tracked predictions")
    
    print("\n💡 Next Steps:")
    print("   • Open docs/index.html in your browser")
    print("   • Review prediction progress")
    print("   • Add new predictions as claims arise")
    
    print("\n" + "=" * 80)
    print("Structure determines solvability. Formal foundations before claims.")
    print("=" * 80 + "\n")
    
    return 0 if success_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())
