#!/usr/bin/env python3
"""
Jesse Livermore Trading Game
Simulate short selling with real-world mechanics
Currency: Bytes (฿) where ฿1 = $1 USD equivalent
"""

import json
import os
from datetime import datetime, timedelta
import urllib.request

POSITION_FILE = "data/trading_position.json"
BORROW_RATE = 0.08  # 8% annual hard-to-borrow fee
COMMISSION_RATE = 0.005  # 0.5% per trade
INITIAL_MARGIN = 1.50  # 150% required
MAINTENANCE_MARGIN = 1.25  # 125% maintenance
LIQUIDATION_THRESHOLD = 1.10  # 110% forced liquidation

def get_current_price():
    """Fetch current BMNR price from Yahoo Finance"""
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/BMNR?interval=1d"
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; BitMineTracker/1.0)'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            quote = data['chart']['result'][0]['meta']
            return float(quote.get('regularMarketPrice', 31.36))
    except Exception as e:
        print(f"⚠️  Price fetch failed: {e}")
        print(f"⚠️  Using fallback price: ฿31.36")
        return 31.36

def open_short_position(shares, capital):
    """Open a new short position"""
    
    if os.path.exists(POSITION_FILE):
        print("❌ Position already exists! Close it first with: check_position() then close_position()")
        return
    
    current_price = get_current_price()
    position_value = shares * current_price
    required_margin = position_value * INITIAL_MARGIN
    commission = position_value * COMMISSION_RATE
    
    print("\n" + "="*70)
    print("🎯 OPENING SHORT POSITION")
    print("="*70)
    print(f"\nCurrent BMNR Price: ฿{current_price:.2f}")
    print(f"\nShares to Short: {shares:,}")
    print(f"Position Value: ฿{position_value:,.2f}")
    print(f"Required Margin (150%): ฿{required_margin:,.2f}")
    print(f"Commission (0.5%): ฿{commission:,.2f}")
    print(f"\nTotal Capital Needed: ฿{required_margin + commission:,.2f}")
    print(f"Your Capital: ฿{capital:,.2f}")
    
    if capital < required_margin + commission:
        print(f"\n❌ INSUFFICIENT CAPITAL")
        print(f"Short: ฿{required_margin + commission - capital:,.2f}")
        return
    
    cash_after = capital - commission
    equity = cash_after - position_value
    margin_level = (equity / position_value) * 100
    
    print(f"\nCash After Commission: ฿{cash_after:,.2f}")
    print(f"Initial Equity: ฿{equity:,.2f}")
    print(f"Initial Margin Level: {margin_level:.1f}%")
    
    position = {
        "shares": shares,
        "entry_price": current_price,
        "entry_date": datetime.now().isoformat(),
        "initial_capital": capital,
        "cash": cash_after,
        "open_commission": commission,
        "borrow_rate": BORROW_RATE,
        "status": "OPEN"
    }
    
    os.makedirs('data', exist_ok=True)
    with open(POSITION_FILE, 'w') as f:
        json.dump(position, f, indent=2)
    
    print("\n" + "="*70)
    print("✅ POSITION OPENED")
    print("="*70)
    print("\n📊 The glyph now controls your fate.")
    print("💡 Check status anytime: check_position()")
    print("💡 Close when ready: close_position()")
    print("\n🏦 The House says: \"Good luck. You'll need it.\"")
    print(f"\n📈 Dashboard updating at: https://tjpools.github.io/BIT/")
    print("="*70 + "\n")

def check_position():
    """Check current position status"""
    
    if not os.path.exists(POSITION_FILE):
        print("\n❌ No active position")
        print("💡 Open one with: open_short_position(shares, capital)")
        return None
    
    with open(POSITION_FILE, 'r') as f:
        position = json.load(f)
    
    current_price = get_current_price()
    entry_price = position['entry_price']
    shares = position['shares']
    cash = position['cash']
    entry_date = datetime.fromisoformat(position['entry_date'])
    days_held = (datetime.now() - entry_date).total_seconds() / 86400
    
    # Calculate P&L
    position_value_entry = shares * entry_price
    position_value_current = shares * current_price
    price_pnl = position_value_entry - position_value_current
    
    # Calculate fees
    daily_borrow_fee = (position_value_entry * BORROW_RATE) / 365
    total_borrow_fees = daily_borrow_fee * days_held
    
    # Calculate equity and margin
    total_pnl = price_pnl - total_borrow_fees - position['open_commission']
    equity = cash + total_pnl
    margin_level = (equity / position_value_current) * 100 if position_value_current > 0 else 0
    
    print("\n" + "="*70)
    print("📊 POSITION STATUS")
    print("="*70)
    
    print(f"\n🎲 Entry: ฿{entry_price:.2f} → Current: ฿{current_price:.2f}")
    print(f"📅 Days Held: {days_held:.2f}")
    print(f"📈 Shares Short: {shares:,}")
    
    print(f"\n💰 PERFORMANCE:")
    print(f"  Price P&L: ฿{price_pnl:,.2f}")
    print(f"  Borrow Fees: -฿{total_borrow_fees:,.2f}")
    print(f"  Entry Commission: -฿{position['open_commission']:,.2f}")
    print(f"  {'─'*50}")
    print(f"  Net P&L: ฿{total_pnl:,.2f} ({(total_pnl/position['initial_capital'])*100:+.2f}%)")
    
    print(f"\n🏦 MARGIN STATUS:")
    print(f"  Cash: ฿{cash:,.2f}")
    print(f"  Current Equity: ฿{equity:,.2f}")
    print(f"  Position Value: ฿{position_value_current:,.2f}")
    print(f"  Margin Level: {margin_level:.1f}%")
    
    # Risk warnings
    if margin_level < LIQUIDATION_THRESHOLD * 100:
        print(f"\n🚨 LIQUIDATION - POSITION FORCE CLOSED AT ฿{current_price:.2f}")
        close_position_forced(current_price, "LIQUIDATED")
    elif margin_level < MAINTENANCE_MARGIN * 100:
        print(f"\n⚠️  MARGIN CALL - Deposit more capital or close position!")
        print(f"    Need margin > 125%, currently at {margin_level:.1f}%")
    elif margin_level < 140:
        print(f"\n⚠️  WARNING - Margin approaching maintenance level")
    else:
        print(f"\n✅ Margin healthy")
    
    print("\n" + "="*70 + "\n")
    
    return {
        'current_price': current_price,
        'margin_level': margin_level,
        'total_pnl': total_pnl,
        'equity': equity
    }

def close_position():
    """Close position voluntarily"""
    
    if not os.path.exists(POSITION_FILE):
        print("\n❌ No active position to close")
        return
    
    with open(POSITION_FILE, 'r') as f:
        position = json.load(f)
    
    if position['status'] == 'LIQUIDATED':
        print("\n💀 Position already liquidated by The House")
        return
    
    current_price = get_current_price()
    shares = position['shares']
    position_value = shares * current_price
    close_commission = position_value * COMMISSION_RATE
    
    status = check_position()
    if not status:
        return
    
    final_equity = status['equity'] - close_commission
    total_return = ((final_equity - position['initial_capital']) / position['initial_capital']) * 100
    
    print("\n" + "="*70)
    print("🔒 CLOSING POSITION")
    print("="*70)
    print(f"\nClosing Price: ฿{current_price:.2f}")
    print(f"Closing Commission: ฿{close_commission:,.2f}")
    print(f"Final Equity: ฿{final_equity:,.2f}")
    print(f"Total Return: {total_return:+.2f}%")
    
    position['status'] = 'CLOSED'
    position['close_price'] = current_price
    position['close_date'] = datetime.now().isoformat()
    position['close_commission'] = close_commission
    position['final_equity'] = final_equity
    position['total_return'] = total_return
    
    with open(POSITION_FILE, 'w') as f:
        json.dump(position, f, indent=2)
    
    # Archive and remove active position
    archive_file = f"data/closed_position_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(archive_file, 'w') as f:
        json.dump(position, f, indent=2)
    
    os.remove(POSITION_FILE)
    
    if total_return > 0:
        print("\n✅ Profitable exit - well played")
        print("💬 Livermore: \"Profits always take care of themselves but losses never do.\"")
    else:
        print("\n📉 Loss realized - the glyph won this round")
        print("💬 Livermore: \"The market is never wrong. Opinions often are.\"")
    
    print(f"\n📁 Position archived: {archive_file}")
    print("="*70 + "\n")

def close_position_forced(price, reason="LIQUIDATED"):
    """Force close position (liquidation)"""
    
    with open(POSITION_FILE, 'r') as f:
        position = json.load(f)
    
    shares = position['shares']
    position_value = shares * price
    close_commission = position_value * COMMISSION_RATE
    
    position['status'] = reason
    position['close_price'] = price
    position['close_date'] = datetime.now().isoformat()
    position['close_commission'] = close_commission
    
    with open(POSITION_FILE, 'w') as f:
        json.dump(position, f, indent=2)
    
    archive_file = f"data/liquidated_position_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(archive_file, 'w') as f:
        json.dump(position, f, indent=2)
    
    os.remove(POSITION_FILE)
    
    print("\n💀 THE HOUSE HAS SPOKEN")
    print("💬 Livermore: \"Markets can remain irrational longer than you can remain solvent.\"")
    print(f"📁 Position archived: {archive_file}")

def show_menu():
    """Display interactive menu"""
    print("\n" + "="*70)
    print("🎰 JESSE LIVERMORE TRADING GAME")
    print("="*70)
    print("\nAvailable commands:")
    print("  1. open_short_position(shares, capital) - Open new short")
    print("  2. check_position() - Check current status")
    print("  3. close_position() - Close position")
    print("  4. get_current_price() - Fetch current BMNR price")
    print("\nExamples:")
    print("  Conservative: open_short_position(1000, 50000)")
    print("  Moderate:     open_short_position(2000, 100000)")
    print("  Aggressive:   open_short_position(3000, 150000)")
    print("\nCurrent BMNR: ฿{:.2f}".format(get_current_price()))
    print("="*70 + "\n")

if __name__ == "__main__":
    show_menu()
