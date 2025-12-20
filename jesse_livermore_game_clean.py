#!/usr/bin/env python3
"""
Jesse Livermore Trading Game - Short Selling Simulator
"The game taught me the game. And it will never be finished."
"""
import json, os
from datetime import datetime

POSITION_FILE = "data/trading_position.json"

def get_current_price():
    """Fetch BMNR price from Yahoo Finance"""
    try:
        from fetch_and_generate import fetch_yahoo_finance
        data = fetch_yahoo_finance("BMNR")
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("currentPrice")
        elif isinstance(data, dict):
            return data.get("currentPrice")
    except:
        pass
    return 31.28  # Fallback price

def load_position():
    if os.path.exists(POSITION_FILE):
        with open(POSITION_FILE, 'r') as f:
            return json.load(f)
    return None

def save_position(position):
    os.makedirs("data", exist_ok=True)
    with open(POSITION_FILE, 'w') as f:
        json.dump(position, f, indent=2)

print("Game loaded successfully! Testing price fetch...")
print(f"Current BMNR: ${get_current_price():.2f}")
print("\nReady to play!")
