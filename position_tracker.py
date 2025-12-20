#!/usr/bin/env python3
"""
Jesse Livermore Position Tracker
Integrates with BMNR tracker to show active short position
"""

import json
import os
from datetime import datetime

POSITION_FILE = "data/trading_position.json"

def load_position():
    """Load active position if exists"""
    if os.path.exists(POSITION_FILE):
        try:
            with open(POSITION_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def calculate_position_status(position, current_price):
    """Calculate all position metrics"""
    entry_price = position["entry_price"]
    shares = position["shares"]
    entry_value = position["entry_value"]
    current_value = shares * current_price
    
    # P&L calculation (short: profit when price falls)
    price_diff = entry_price - current_price
    unrealized_pnl = price_diff * shares
    pnl_percent = (price_diff / entry_price) * 100
    
    # Time-based fees
    entry_dt = datetime.fromisoformat(position["entry_time"])
    now_dt = datetime.now()
    days_elapsed = (now_dt - entry_dt).total_seconds() / 86400
    
    daily_fee_rate = position["borrow_fee_annual"] / 365
    borrow_fees = entry_value * daily_fee_rate * days_elapsed
    
    total_fees = position["commission_paid"] + borrow_fees
    net_pnl = unrealized_pnl - total_fees
    
    # Margin calculation
    equity = position["net_capital"] + unrealized_pnl - borrow_fees
    margin_level = equity / current_value if current_value > 0 else 0
    
    return {
        "current_price": current_price,
        "current_value": current_value,
        "unrealized_pnl": unrealized_pnl,
        "pnl_percent": pnl_percent,
        "borrow_fees": borrow_fees,
        "total_fees": total_fees,
        "net_pnl": net_pnl,
        "equity": equity,
        "margin_level": margin_level,
        "days_elapsed": days_elapsed
    }

def generate_position_html_section(position, status):
    """Generate HTML section for position display"""
    
    # Determine status indicators
    if status["margin_level"] < position["liquidation_margin"]:
        margin_status = "💥 LIQUIDATION IMMINENT"
        margin_class = "liquidation"
    elif status["margin_level"] < position["maintenance_margin"]:
        margin_status = "🚨 MARGIN CALL"
        margin_class = "margin-call"
    elif status["margin_level"] < position["maintenance_margin"] * 1.1:
        margin_status = "⚠️ WARNING"
        margin_class = "warning"
    else:
        margin_status = "✅ HEALTHY"
        margin_class = "healthy"
    
    pnl_class = "profit" if status["net_pnl"] >= 0 else "loss"
    pnl_symbol = "✅" if status["net_pnl"] >= 0 else "⚠️"
    
    html = f"""
    <div class="position-container">
        <h2>📉 Active Short Position</h2>
        
        <div class="position-header {pnl_class}">
            <div class="stat-box">
                <span class="label">Position</span>
                <span class="value">SHORT {position['shares']:,} shares</span>
            </div>
            <div class="stat-box">
                <span class="label">Entry Price</span>
                <span class="value">฿{position['entry_price']:.2f}</span>
            </div>
            <div class="stat-box">
                <span class="label">Current Price</span>
                <span class="value">฿{status['current_price']:.2f}</span>
            </div>
            <div class="stat-box">
                <span class="label">Duration</span>
                <span class="value">{status['days_elapsed']:.1f} days</span>
            </div>
        </div>
        
        <div class="position-pnl {pnl_class}">
            <h3>{pnl_symbol} Net P&L: ฿{status['net_pnl']:+,.2f} ({status['pnl_percent']:+.2f}%)</h3>
            <div class="pnl-breakdown">
                <span>Unrealized P&L: ฿{status['unrealized_pnl']:+,.2f}</span>
                <span>Fees: -฿{status['total_fees']:,.2f}</span>
            </div>
        </div>
        
        <div class="margin-status {margin_class}">
            <h3>Margin Level: {status['margin_level']*100:.1f}% - {margin_status}</h3>
            <div class="margin-bars">
                <div class="margin-bar">
                    <div class="margin-fill" style="width: {min(status['margin_level']*100, 200)}%"></div>
                </div>
                <div class="margin-thresholds">
                    <span>Liquidation: {position['liquidation_margin']*100:.0f}%</span>
                    <span>Maintenance: {position['maintenance_margin']*100:.0f}%</span>
                    <span>Current: {status['margin_level']*100:.1f}%</span>
                </div>
            </div>
        </div>
        
        <div class="position-details">
            <div class="detail-row">
                <span>Entry Value:</span>
                <span>฿{position['entry_value']:,.2f}</span>
            </div>
            <div class="detail-row">
                <span>Current Value:</span>
                <span>฿{status['current_value']:,.2f}</span>
            </div>
            <div class="detail-row">
                <span>Account Equity:</span>
                <span>฿{status['equity']:,.2f}</span>
            </div>
            <div class="detail-row">
                <span>Borrow Fees Accrued:</span>
                <span>-฿{status['borrow_fees']:,.2f}</span>
            </div>
        </div>
        
        <div class="house-message">
            <strong>🏦 The House:</strong> {get_house_message(status['margin_level'], position)}
        </div>
        
        <div class="livermore-quote">
            <em>"{get_livermore_quote(status['net_pnl'], position['entry_value'])}"</em>
        </div>
    </div>
    """
    
    return html

def get_house_message(margin_level, position):
    """Get appropriate message from The House"""
    if margin_level < position["liquidation_margin"]:
        return "LIQUIDATING YOUR POSITION NOW. No exceptions."
    elif margin_level < position["maintenance_margin"]:
        return "MARGIN CALL! Deposit funds NOW or we liquidate."
    elif margin_level < position["maintenance_margin"] * 1.05:
        return "One more tick against you and you're getting a margin call!"
    elif margin_level < position["maintenance_margin"] * 1.1:
        return "We're watching this position closely..."
    else:
        return "Position looks good. Keep monitoring it."

def get_livermore_quote(net_pnl, entry_value):
    """Get appropriate Livermore quote"""
    pnl_ratio = net_pnl / entry_value if entry_value > 0 else 0
    
    if pnl_ratio > 0.1:
        return "There is a time to go long, a time to go short, and a time to go fishing. Consider your exit!"
    elif pnl_ratio < -0.1:
        return "The most important rule of trading is to play great defense, not great offense."
    else:
        return "It was never my thinking that made the big money for me. It always was my sitting."

def get_position_css():
    """Additional CSS for position display"""
    return """
    .position-container {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        border: 2px solid #16213e;
    }
    
    .position-header {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .stat-box {
        background: #0f3460;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    
    .stat-box .label {
        display: block;
        font-size: 0.85em;
        color: #94a3b8;
        margin-bottom: 5px;
    }
    
    .stat-box .value {
        display: block;
        font-size: 1.2em;
        font-weight: bold;
        color: #e2e8f0;
    }
    
    .position-pnl {
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        text-align: center;
    }
    
    .position-pnl.profit {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
        border: 2px solid #10b981;
    }
    
    .position-pnl.loss {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        border: 2px solid #ef4444;
    }
    
    .position-pnl h3 {
        margin: 0 0 10px 0;
        font-size: 1.5em;
    }
    
    .pnl-breakdown {
        display: flex;
        justify-content: center;
        gap: 20px;
        font-size: 0.9em;
        opacity: 0.9;
    }
    
    .margin-status {
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
    }
    
    .margin-status.healthy {
        background: #064e3b;
        border: 2px solid #10b981;
    }
    
    .margin-status.warning {
        background: #78350f;
        border: 2px solid #f59e0b;
    }
    
    .margin-status.margin-call {
        background: #7f1d1d;
        border: 2px solid #ef4444;
        animation: pulse 2s infinite;
    }
    
    .margin-status.liquidation {
        background: #450a0a;
        border: 3px solid #dc2626;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .margin-bars {
        margin-top: 15px;
    }
    
    .margin-bar {
        height: 30px;
        background: #1e293b;
        border-radius: 15px;
        overflow: hidden;
        margin-bottom: 10px;
    }
    
    .margin-fill {
        height: 100%;
        background: linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%);
        transition: width 0.5s ease;
    }
    
    .margin-thresholds {
        display: flex;
        justify-content: space-between;
        font-size: 0.85em;
        color: #94a3b8;
    }
    
    .position-details {
        background: #0f172a;
        padding: 15px;
        border-radius: 8px;
        margin: 20px 0;
    }
    
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #1e293b;
    }
    
    .detail-row:last-child {
        border-bottom: none;
    }
    
    .house-message {
        background: #1e293b;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 20px 0;
    }
    
    .livermore-quote {
        text-align: center;
        padding: 15px;
        font-style: italic;
        color: #94a3b8;
        border-top: 1px solid #1e293b;
        margin-top: 20px;
    }
    """

if __name__ == "__main__":
    # Test the position tracker
    position = load_position()
    current_price = get_current_price()
    
    if position:
        status = calculate_position_status(position, current_price)
        print("Position Status:")
        print(f"  Current Price: ฿{status['current_price']:.2f}")
        print(f"  Net P&L: ฿{status['net_pnl']:+,.2f}")
        print(f"  Margin Level: {status['margin_level']*100:.1f}%")
    else:
        print("No active position")
