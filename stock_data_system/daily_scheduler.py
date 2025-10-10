"""
Daily Scheduler for Stock Data Collection
Run this script to automatically collect data every day during market hours
"""

import schedule
import time
from datetime import datetime
import pytz
from incremental_collector import IncrementalStockCollector


def is_market_day():
    """Check if today is a market day (weekday)"""
    return datetime.now().weekday() < 5  # Monday=0, Friday=4


def collect_data():
    """Run the data collection"""
    if is_market_day():
        print(f"\n{'='*70}")
        print(f"Scheduled Collection Started: {datetime.now()}")
        print(f"{'='*70}\n")
        
        collector = IncrementalStockCollector()
        collector.collect_all()
        collector.get_stats()
    else:
        print(f"[{datetime.now()}] Skipping - Market closed (weekend)")


def main():
    """Main scheduler loop"""
    print(f"\n{'='*70}")
    print(f"Stock Data Collection Scheduler Started")
    print(f"{'='*70}")
    print(f"Time: {datetime.now()}")
    print(f"Schedule: Daily at 5:30 PM ET (after market close)")
    print(f"Press Ctrl+C to stop")
    print(f"{'='*70}\n")
    
    # Schedule daily collection at 5:30 PM ET (after market close at 4 PM)
    schedule.every().day.at("17:30").do(collect_data)
    
    # Run once immediately on start
    print("Running initial collection...\n")
    collect_data()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")

