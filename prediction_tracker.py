#!/usr/bin/env python3
"""
Prediction Tracker
Log and measure accuracy of external predictions about BMNR
"""

import json
import os
from datetime import datetime
import urllib.request
import logging

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/prediction_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

PREDICTIONS_FILE = "data/predictions.json"

def load_predictions():
    """Load existing predictions"""
    if os.path.exists(PREDICTIONS_FILE):
        with open(PREDICTIONS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_predictions(predictions):
    """Save predictions to file"""
    os.makedirs(os.path.dirname(PREDICTIONS_FILE), exist_ok=True)
    with open(PREDICTIONS_FILE, 'w') as f:
        json.dump(predictions, f, indent=2)

def get_current_price():
    """Fetch current BMNR price"""
    logger.info("Fetching current BMNR price")
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/BMNR?interval=1d&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            result = data['chart']['result'][0]
            price = result['meta']['regularMarketPrice']
            logger.info(f"Current price: ${price:.2f}")
            return price
    except Exception as e:
        logger.error(f"Error fetching current price: {e}", exc_info=True)
        return None

def add_prediction(statement, target_price, timeframe, source="Manual", notes=""):
    """Add a new prediction"""
    logger.info(f"Adding new prediction: target=${target_price}, timeframe={timeframe}")
    predictions = load_predictions()
    
    prediction = {
        "id": len(predictions) + 1,
        "timestamp": datetime.now().isoformat(),
        "statement": statement,
        "target_price": target_price,
        "initial_price": get_current_price(),
        "timeframe": timeframe,
        "source": source,
        "notes": notes,
        "status": "active",
        "result": None,
        "accuracy_score": None
    }
    
    predictions.append(prediction)
    save_predictions(predictions)
    
    logger.info(f"Prediction #{prediction['id']} added successfully")
    print(f"✓ Prediction #{prediction['id']} added")
    return prediction

def check_predictions():
    """Check status of all predictions"""
    predictions = load_predictions()
    current_price = get_current_price()
    
    if not current_price:
        print("✗ Could not fetch current price")
        return
    
    print(f"\n💰 Current BMNR Price: ${current_price:.2f}\n")
    print("=" * 80)
    print("PREDICTION TRACKING")
    print("=" * 80)
    
    active = [p for p in predictions if p['status'] == 'active']
    completed = [p for p in predictions if p['status'] in ['hit', 'missed', 'expired']]
    
    if active:
        print(f"\n📊 ACTIVE PREDICTIONS ({len(active)}):")
        print("-" * 80)
        
        for pred in active:
            initial = pred['initial_price']
            target = pred['target_price']
            
            move_needed = target - current_price
            pct_needed = (move_needed / current_price) * 100
            
            progress_so_far = current_price - initial
            total_move = target - initial
            progress_pct = (progress_so_far / total_move * 100) if total_move != 0 else 0
            
            print(f"\n#{pred['id']}: {pred['statement'][:60]}...")
            print(f"   Source: {pred['source']} | Date: {pred['timestamp'][:10]}")
            print(f"   Target: ${target:.2f} | Initial: ${initial:.2f}")
            print(f"   Current: ${current_price:.2f}")
            print(f"   Progress: {progress_pct:.1f}% of predicted move")
            print(f"   Remaining: ${move_needed:.2f} ({pct_needed:+.1f}%)")
            print(f"   Timeframe: {pred['timeframe']}")
            
            if pred['notes']:
                print(f"   Notes: {pred['notes']}")
    
    if completed:
        print(f"\n📈 COMPLETED PREDICTIONS ({len(completed)}):")
        print("-" * 80)
        
        for pred in completed:
            print(f"\n#{pred['id']}: {pred['statement'][:60]}...")
            print(f"   Status: {pred['status'].upper()}")
            print(f"   Target: ${pred['target_price']:.2f}")
            print(f"   Result: {pred['result']}")
            if pred['accuracy_score']:
                print(f"   Accuracy: {pred['accuracy_score']}")
    
    if not active and not completed:
        print("\n📝 No predictions tracked yet.")
        print("   Use --add to create a new prediction")
    
    print("\n" + "=" * 80)

def mark_prediction(pred_id, status, result_price=None):
    """Mark a prediction as hit/missed/expired"""
    predictions = load_predictions()
    
    for pred in predictions:
        if pred['id'] == pred_id:
            pred['status'] = status
            
            if result_price:
                target = pred['target_price']
                initial = pred['initial_price']
                
                # Calculate accuracy
                target_move = target - initial
                actual_move = result_price - initial
                
                if target_move != 0:
                    accuracy = (actual_move / target_move) * 100
                    pred['accuracy_score'] = f"{accuracy:.1f}%"
                
                pred['result'] = f"Price reached ${result_price:.2f}"
            
            save_predictions(predictions)
            print(f"✓ Prediction #{pred_id} marked as {status}")
            return
    
    print(f"✗ Prediction #{pred_id} not found")

def main():
    import sys
    
    if len(sys.argv) < 2:
        check_predictions()
        return
    
    command = sys.argv[1]
    
    if command == "--add":
        if len(sys.argv) < 4:
            print("Usage: python3 prediction_tracker.py --add <target_price> <timeframe> [statement]")
            print("Example: python3 prediction_tracker.py --add 53.63 '2-4 weeks' 'Next target is 53.63 at 618 fib'")
            return
        
        target = float(sys.argv[2])
        timeframe = sys.argv[3]
        statement = sys.argv[4] if len(sys.argv) > 4 else f"Target ${target}"
        
        add_prediction(statement, target, timeframe)
        check_predictions()
    
    elif command == "--hit":
        if len(sys.argv) < 4:
            print("Usage: python3 prediction_tracker.py --hit <id> <price_reached>")
            return
        
        pred_id = int(sys.argv[2])
        price = float(sys.argv[3])
        mark_prediction(pred_id, "hit", price)
        check_predictions()
    
    elif command == "--miss":
        if len(sys.argv) < 3:
            print("Usage: python3 prediction_tracker.py --miss <id>")
            return
        
        pred_id = int(sys.argv[2])
        mark_prediction(pred_id, "missed")
        check_predictions()
    
    elif command == "--list":
        check_predictions()
    
    else:
        print("Commands:")
        print("  --add <target> <timeframe> [statement]  - Add new prediction")
        print("  --hit <id> <price>                      - Mark prediction as hit")
        print("  --miss <id>                             - Mark prediction as missed")
        print("  --list                                  - Show all predictions")
        print("\nDefault (no args): Show current status")

if __name__ == "__main__":
    main()
