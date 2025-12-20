#!/usr/bin/env python3
"""
Jesse Livermore Trading Game
Simulate short positions on BMNR with pseudo dollars
"The game taught me the game. And it will never be finished."
"""

import json
import os
from datetime import datetime
from fetch_and_generate import fetch_yahoo_finance

POSITION_FILE = "data/trading_position.json"

def load_position():
    """Load existing position or return None"""
    if os.path.exists(POSITION_FILE):
        with open(POSITION_FILE, 'r') as f:
            return json.load(f)
    return None

def save_position(position):
    """Save position to disk"""
    os.makedirs("data", exist_ok=True)
    with open(POSITION_FILE, 'w') as f:
        json.dump(position, f, indent=2)

def get_current_price():
    """Fetch current BMNR price"""
    data = fetch_yahoo_finance("BMNR")
    if data and "currentPrice" in data:
        return data["currentPrice"]
    return None

def calculate_pnl(position, current_price):
    """Calculate P&L for short position"""
    # Short P&L = (Entry Price - Current Price) × Shares
    entry_price = position["entry_price"]
    shares = position["shares"]
    price_diff = entry_price - current_price
    unrealized_pnl = price_diff * shares
    pnl_percent = (price_diff / entry_price) * 100
    return unrealized_pnl, pnl_percent

def open_short_position(shares, starting_capital):
    """Open a new short position"""
    current_price = get_current_price()
    if not current_price:
        print("❌ Unable to fetch current price")
        return None
    
    entry_value = shares * current_price
    
    # House/Brokerage terms (per SEC Regulation T and real-world practices)
    MARGIN_REQUIREMENT = 1.5  # 150% initial margin (SEC Reg T for shorts)
    BORROW_FEE_ANNUAL = 0.08  # 8% annual borrow fee (hard-to-borrow stock)
    MAINTENANCE_MARGIN = 1.25  # 125% maintenance margin (margin call trigger)
    LIQUIDATION_MARGIN = 1.10  # 110% forced liquidation threshold
    COMMISSION = 0.005  # 0.5% commission per trade (both open and close)
    
    required_margin = entry_value * MARGIN_REQUIREMENT
    commission_open = entry_value * COMMISSION
    
    # Check if player has enough capital (margin + commission)
    total_required = required_margin + commission_open
    if starting_capital < total_required:
        print("\n" + "="*70)
        print("🏦 THE HOUSE (BROKERAGE) REJECTS YOUR TRADE")
        print("="*70)
        print(f"❌ Insufficient capital!")
        print(f"📊 Position Value: ${entry_value:,.2f}")
        print(f"📊 Required Margin (150%): ${required_margin:,.2f}")
        print(f"💸 Commission (0.5%): ${commission_open:,.2f}")
        print(f"📊 Total Required: ${total_required:,.2f}")
        print(f"💰 Your Capital: ${starting_capital:,.2f}")
        print(f"💸 Shortfall: ${total_required - starting_capital:,.2f}")
        print("="*70)
        print()
        print("💡 The House: 'Can't let you borrow what you can't cover, pal.'")
    # Deduct commission from capital
    net_capital = starting_capital - commission_open
    
    position = {
        "type": "short",
        "symbol": "BMNR",
        "shares": shares,
        "entry_price": current_price,
        "entry_value": entry_value,
        "entry_time": datetime.now().isoformat(),
        "starting_capital": starting_capital,
        "net_capital": net_capital,
        "margin_requirement": MARGIN_REQUIREMENT,
        "maintenance_margin": MAINTENANCE_MARGIN,
        "liquidation_margin": LIQUIDATION_MARGIN,
        "borrow_fee_annual": BORROW_FEE_ANNUAL,
        "commission_rate": COMMISSION,
        "commission_paid": commission_open,
        "accumulated_fees": 0,
        "trade_history": [],
        "margin_calls": 0,
        "last_check": datetime.now().isoformat()": MARGIN_REQUIREMENT,
        "maintenance_margin": MAINTENANCE_MARGIN,
        "borrow_fee_annual": BORROW_FEE_ANNUAL,
        "accumulated_fees": 0 (Per SEC Reg T & Industry Standards):")
    print(f"   • Initial Margin: {MARGIN_REQUIREMENT*100:.0f}% (${required_margin:,.2f})")
    print(f"   • Maintenance Margin: {MAINTENANCE_MARGIN*100:.0f}% (margin call threshold)")
    print(f"   • Liquidation Threshold: {LIQUIDATION_MARGIN*100:.0f}% (forced close)")
    print(f"   • Borrow Fee: {BORROW_FEE_ANNUAL*100:.1f}% annually (~${entry_value * BORROW_FEE_ANNUAL / 365:.2f}/day)")
    print(f"   • Commission: {COMMISSION*100:.2f}% per trade")
    print()
    print("💰 ACCOUNT BREAKDOWN:")
    print(f"   Starting Capital:        ${starting_capital:,.2f}")
    print(f"   Commission (paid now):   -${commission_open:,.2f}")
    print(f"   Net Capital:             ${net_capital:,.2f}")
    print(f"   Margin Posted:           ${required_margin:,.2f}")
    print(f"   Free Cash:               ${net_capital - required_margin:,.2f}")
    print()
    print(f"⏰ Entry Time: {position['entry_time']}")
    print("="*70)
    print()
    print("💡 Jesse Livermore: 'It was never my thinking that made the big money")
    print("   for me. It always was my sitting.'")
    print()
    print("⚠️  The House: 'Remember - we can recall these shares anytime.")
    print("    If margin drops below {LIQUIDATION_MARGIN*100:.0f}%, we liquidate WITHOUT NOTICE!")
    print("    Keep checking your position. Good luck0f}% (margin call threshold)")
    print(f"   • Borrow Fee: {BORROW_FEE_ANNUAL*100:.1f}% annually (~{BORROW_FEE_ANNUAL*100/365:.3f}%/day)")
    print()
    print(f"🏦 Your Capital: ${starting_capital:,.2f}")
    print(f"🔒 Margin Posted: ${required_margin:,.2f}")
    print(f"💵 Buying Power Remaining: ${starting_capital - required_margin:,.2f}")
    print(f"⏰ Entry Time: {position['entry_time']}")
    print("="*70)
    print()
    print("💡 Jesse Livermore: 'It was never my thinking that made the big money")
    print("   for me. It always was my sitting.'")
    print()
    print("⚠️  The House: 'Remember, we can recall these shares anytime.")
    print("    Keep that margin healthy or we'll close you out!'")
    print()
    
    return position

def check_position():
    """Check current position status"""
    position = load_position(), accrues daily)
    from datetime import datetime
    entry_dt = datetime.fromisoformat(position["entry_time"])
    now_dt = datetime.now()
    days_elapsed = (now_dt - entry_dt).total_seconds() / 86400
    daily_fee_rate = position["borrow_fee_annual"] / 365
    total_borrow_fees = entry_value * daily_fee_rate * days_elapsed
    
    # Total costs
    total_fees = position["commission_paid"] + total_borrow_fees
    
    # Net P&L after all fees
    net_pnl = unrealized_pnl - total_fees
    
    # Calculate margin level (Critical for margin calls)
    # Equity = Net Capital + Unrealized P&L - Borrow Fees
    equity = position["net_capital"] + unrealized_pnl - total_borrow_fees
    margin_level = equity / current_value
    maintenance_margin = position["maintenance_margin"]
    liquidation_margin = position["liquidation_margin"]
    
    # Check for forced liquidation
    if margin_level < liquidation_margin:
        print("\n" + "🚨"*35)
        print("   💥 FORCED LIQUIDATION BY THE HOUSE 💥")
        print("🚨"*35)
        print()
        print("⚠️  Your margin level dropped below liquidation threshold!")
        print(f"   Liquidation Threshold: {liquidation_margin*100:.0f}%")
        print(f"   Your Margin Level: {margin_level*100:.1f}%")
        print()
        print("🏦 The House: 'We warned you. Liquidating your position NOW.'")
        print("   'No exceptions. Risk management is non-negotiable.'")
        print()
        
        # Force close the position
        close_position_forced()
        return
    from datetime import datetime
    entry_dt = datetime.fromisoformat(position["entry_time"])
    now_dt = datetime.now()
    days_elapsed = (now_dt - entry_dt).total_seconds() / 86400
    daily_fee_rate = position["borrow_fee_annual"] / 365
    new_fees = entry_value * daily_fee_rate * days_elapsed
    total_fees = position["accumulated_fees"] + new_fees
    
    # Net P&L after fees
    net_pnl = unrealized_pnl - total_fees
    
    # Calculate margin level
    # Equity = Starting Capital + Unrealized P&L - Fees
    equity = position["starting_capital"] + unrealized_pnl - total_fees
    margin_level = equity / current_value
    maintenance_margin = position["maintenance_margin"]
    
    # Track price history
    position["trade_history"].append({
        "timestamp": datetime.now().isoformat(),
        "price": current_price,
        "unrealized_pnl": unrealized_pnl,
        "pnl_percent": pnl_percent,
        "total_fees": total_fees,
        "margin_level": margin_level
    })
    position["accumulated_fees"] = total_fees
    save_position(position)
    
    # Display status
    print("\n" + "="*70)
    print("📊 JESSE LIVERMORE GAME - POSITION STATUS")
    print("="*70)
    print(f"🎯 Position: SHORT {shares:,} shares BMNR")
    print(f"📍 Entry Price: ${entry_price:.2f}")
    print(f"📍 Current Price: ${current_price:.2f}")
    print(f"📊 Price Change: ${current_price - entry_price:.2f} ({(current_price/entry_price - 1)*100:+.2f}%)")
    print("─"*70)
    print(f"💵 Entry Value: ${entry_value:,.2f}")
    print(f"💵 Current Value: ${current_value:,.2f}")
    print("─"*70)
    
    # P&L display with color indication
    if net_pnl >= 0:
        pnl_symbol = "✅"
        sentiment = "PROFIT"
    else:
        pnl_symbol = "⚠️"
        sentiment = "LOSS"
    
    print(f"💰 Unrealized P&L: ${unrealized_pnl:+,.2f} ({pnl_percent:+.2f}%)")
    print(f"🏦 Borrow Fees ({days_elapsed:.2f} days): -${total_fees:,.2f}")
    print(f"{pnl_symbol} Net P&L: ${net_pnl:+,.2f}")
    print(f"📈 Status: {sentiment}")
    print(f"💼 Account Equity: ${equity:,.2f}")
    print("─"*70)
    print(f"📊 MARGIN STATUS:")
    print(f"   Current Margin Level: {margin_level*100:.1f}%")
    
    # Calculate final fees
    from datetime import datetime
    entry_dt = datetime.fromisoformat(position["entry_time"])
    now_dt = datetime.now()
    days_elapsed = (now_dt - entry_dt).total_seconds() / 86400
    daily_fee_rate = position["borrow_fee_annual"] / 365
    entry_value = position["entry_value"]
    total_fees = entry_value * daily_fee_rate * days_elapsed
    
    # Net P&L after fees
    net_pnl = unrealized_pnl - total_fees
    final_capital = position["starting_capital"] + net_pnl
    
    print("\n" + "="*70)
    print("🏁 JESSE LIVERMORE GAME - POSITION CLOSED")
    print("="*70)
    print(f"📍 Entry Price: ${position['entry_price']:.2f}")
    print(f"📍 Exit Price: ${current_price:.2f}")
    print(f"🎯 Shares: {position['shares']:,}")
    print(f"⏱️  Duration: {days_elapsed:.2f} days")
    print("─"*70)
    print(f"💰 Starting Capital: ${position['starting_capital']:,.2f}")
    print(f"💵 Gross P&L: ${unrealized_pnl:+,.2f} ({pnl_percent:+.2f}%)")
    print(f"🏦 Borrow Fees: -${total_fees:,.2f}")
    print(f"💎 Net Realized P&L: ${net_pnl:+,.2f}")
    print(f"🏦 Final Capital: ${final_capital:,.2f}")
    print(f"📊 Total Return: {(net_pnl/position['starting_capital'])*100:+.2f}%")
    print("="*70)
    
    # The House takes its cut
    print()
    print(f"🏦 The House: 'Thanks for your business. We collected ${total_fees:.2f}")
    print(f"   in borrow fees. Come back anytime!'")
    
    if net
        print(f"   ✅ Margin healthy")
    
    print("="*70)
    
    # Jesse Livermore wisdom based on position
    if net_pnl > entry_value * 0.1:
        print("\n💡 Livermore: 'There is a time to go long, a time to go short,")
        print("   and a time to go fishing.' Consider your exit!")
    elif net_pnl < -entry_value * 0.1:
        print("\n💡 Livermore: 'The most important rule of trading is to play")
        print("   great defense, not great offense.' Review your thesis!")
    else:
        print("\n💡 Livermore: 'It was never my thinking that made the big money")
        print("   for me. It always was my sitting.' Be patient!")
    print()

def close_position():
    """Close the short position"""
    position = load_position()
    if not position:
        print("\n❌ No active position to close!\n")
        return
    
    current_price = get_current_price()
    if not current_price:
        print("❌ Unable to fetch current price")
        return
    
    unrealized_pnl, pnl_percent = calculate_pnl(position, current_price)
    final_capital = position["starting_capital"] + unrealized_pnl
    
    print("\n" + "="*70)
    print("🏁 JESSE LIVERMORE GAME - POSITION CLOSED")
    print("="*70)
    print(f"📍 Entry Price: ${position['entry_price']:.2f}")
    print(f"📍 Exit Price: ${current_price:.2f}")
    print(f"🎯 Shares: {position['shares']:,}")
    print("─"*70)
    print(f"💰 Starting Capital: ${position['starting_capital']:,.2f}")
    print(f"💵 Realized P&L: ${unrealized_pnl:+,.2f} ({pnl_percent:+.2f}%)")
    print(f"🏦 Final Capital: ${final_capital:,.2f}")
    print("="*70)
    
    if unrealized_pnl > 0:
        print("\n🎉 Profitable Trade! Jesse would be proud.")
        print("💡 'The big money was not in the individual fluctuations")
        print("   but in the main movements.'")
    else:
        print("\n📚 Learning Experience.")
        print("💡 'There is nothing new in Wall Street. There can't be")
        print("   because speculation is as old as the hills.'")
    
    # Archive and clear
    os.remove(POSITION_FILE)
    print("\n✅ Position closed and archived.\n")

def show_help():
    """Display game instructions"""
    print("\n" + "="*70)
    print("🎮 JESSE LIVERMORE TRADING GAME")
    print("="*70)
    print()
    print("Commands:")
    print("  python jesse_livermore_game.py open <shares> <capital>")
    print("    Example: python jesse_livermore_game.py open 1000 10000")
    print("    Opens a SHORT position of 1000 shares with $10,000 capital")
    print()
    print("  python jesse_livermore_game.py check")
    print("    Check current position P&L")
    print()
    print("  python jesse_livermore_game.py close")
    print("    Close position and realize P&L")
    print()
    print("SHORT POSITION MECHANICS:")
    print("  • You borrow shares and sell them at current price")
    print("  • Profit when price goes DOWN (buy back cheaper)")
    print("  • Loss when price goes UP (buy back more expensive)")
    print("  • P&L = (Entry Price - Current Price) × Shares")
    print()
    print("💡 Jesse Livermore (1877-1940):")
    print("   Legendary trader who made and lost several fortunes.")
    print("   Known for shorting before the 1929 crash ($100M profit).")
    print("   'The game taught me the game. And it will never be finished.'")
    print("="*70)
    print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "open":
        if len(sys.argv) != 4:
            print("❌ Usage: python jesse_livermore_game.py open <shares> <capital>")
            sys.exit(1)
        shares = int(sys.argv[2])
        capital = float(sys.argv[3])
        open_short_position(shares, capital)
    
    elif command == "check":
        check_position()
    
    elif command == "close":
        close_position()
    
    elif command == "help":
        show_help()
    
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)
