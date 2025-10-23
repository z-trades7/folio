"""
Incremental Stock Data Collector
Only fetches new data since the last collection, building the dataset over time
"""

import requests
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import subprocess
import os
import config


class IncrementalStockCollector:
    """Collects only new data, building a growing historical dataset"""
    
    def __init__(self):
        self.db_path = config.DB_PATH
        self.api_key = config.POLYGON_API_KEY
        self.base_url = "https://api.polygon.io"
        self.create_database()
    
    def create_database(self):
        """Create database table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_symbol_time 
            ON stock_data(symbol, timestamp DESC)
        """)
        
        conn.commit()
        conn.close()
    
    def get_last_timestamp(self, symbol):
        """Get the most recent timestamp for a symbol"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT MAX(timestamp) FROM stock_data WHERE symbol = ?
        """, (symbol,))
        
        result = cursor.fetchone()[0]
        conn.close()
        
        if result:
            return datetime.strptime(result, '%Y-%m-%d %H:%M:%S')
        return None
    
    def fetch_aggregates(self, symbol, from_date, to_date):
        """Fetch aggregate bars from Polygon.io"""
        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/{config.INTERVAL}/{config.TIMESPAN}/{from_date}/{to_date}"
        params = {
            'adjusted': 'true',
            'sort': 'asc',
            'limit': 50000,
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK' and data.get('resultsCount', 0) > 0:
                    return data.get('results', [])
                else:
                    return []
            else:
                print(f"  ✗ API Error {response.status_code}")
                return []
                
        except Exception as e:
            print(f"  ✗ Request failed: {e}")
            return []
    
    def collect_symbol(self, symbol, initial_days=60):
        """Collect data for a single symbol (incremental or initial)"""
        try:
            # Check for existing data
            last_timestamp = self.get_last_timestamp(symbol)
            
            if last_timestamp:
                # Incremental update: fetch from last timestamp to now
                # Add 1 day buffer to ensure we don't miss any data
                from_date = last_timestamp - timedelta(days=1)
                to_date = datetime.now()
                mode = "incremental"
                print(f"Updating {symbol} (from {from_date.strftime('%Y-%m-%d')})...")
            else:
                # Initial load: fetch full history
                to_date = datetime.now()
                from_date = to_date - timedelta(days=initial_days)
                mode = "initial"
                print(f"Initial load for {symbol} ({initial_days} days)...")
            
            from_str = from_date.strftime('%Y-%m-%d')
            to_str = to_date.strftime('%Y-%m-%d')
            
            # Fetch data from Polygon
            results = self.fetch_aggregates(symbol, from_str, to_str)
            
            if not results:
                print(f"  ⚠ No new data")
                return 0
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            records_added = 0
            records_skipped = 0
            
            for bar in results:
                try:
                    timestamp = datetime.fromtimestamp(bar['t'] / 1000)
                    
                    cursor = conn.execute("""
                        INSERT OR IGNORE INTO stock_data 
                        (symbol, timestamp, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        symbol,
                        timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        float(bar['o']),
                        float(bar['h']),
                        float(bar['l']),
                        float(bar['c']),
                        int(bar['v'])
                    ))
                    
                    if cursor.rowcount > 0:
                        records_added += 1
                    else:
                        records_skipped += 1
                        
                except Exception as e:
                    records_skipped += 1
            
            conn.commit()
            conn.close()
            
            print(f"  ✓ Added: {records_added:,} new | Skipped: {records_skipped:,} duplicates")
            return records_added
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return 0
    
    def collect_all(self, initial_days=60):
        """Collect data for all symbols (incremental where possible)"""
        print(f"\n{'='*70}")
        print(f"Incremental Stock Data Collection")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        total = 0
        for i, symbol in enumerate(config.SYMBOLS, 1):
            print(f"[{i}/{len(config.SYMBOLS)}] {symbol}")
            total += self.collect_symbol(symbol, initial_days)
            
            # Rate limiting
            if i < len(config.SYMBOLS):
                print(f"  ⏱ Rate limit delay ({config.DELAY_BETWEEN_CALLS}s)...\n")
                time.sleep(config.DELAY_BETWEEN_CALLS)
        
        print(f"\n{'='*70}")
        print(f"Collection complete: {total:,} new records added")
        print(f"{'='*70}\n")
        
        # Export to JSON for web viewer
        self.export_to_json()
        
        # Automatically push to GitHub
        self.git_push_changes()
    
    def export_to_json(self):
        """Export latest data to JSON for web viewer"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            data = {}
            stats = {
                'last_updated': datetime.now().isoformat(),
                'symbols': []
            }
            
            for symbol in config.SYMBOLS:
                # Get all available records
                df = pd.read_sql_query("""
                    SELECT timestamp, open, high, low, close, volume
                    FROM stock_data
                    WHERE symbol = ?
                    ORDER BY timestamp DESC
                """, conn, params=(symbol,))
                
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.sort_values('timestamp', ascending=False)
                    
                    # Convert to dict with string timestamps
                    records = []
                    for _, row in df.iterrows():
                        records.append({
                            'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                            'open': float(row['open']),
                            'high': float(row['high']),
                            'low': float(row['low']),
                            'close': float(row['close']),
                            'volume': int(row['volume'])
                        })
                    
                    data[symbol] = records
                    
                    # Get date range
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT MIN(timestamp), MAX(timestamp), COUNT(*)
                        FROM stock_data WHERE symbol = ?
                    """, (symbol,))
                    min_date, max_date, count = cursor.fetchone()
                    
                    stats['symbols'].append({
                        'symbol': symbol,
                        'records': count,
                        'latest': df.iloc[0]['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                        'oldest': min_date,
                        'price': float(df.iloc[0]['close']),
                        'days_of_data': (pd.to_datetime(max_date) - pd.to_datetime(min_date)).days
                    })
            
            conn.close()
            
            # Save to JSON
            output = {
                'stats': stats,
                'data': data
            }
            
            with open(config.JSON_PATH, 'w') as f:
                json.dump(output, f)
            
            print("✓ Exported data to JSON for web viewer")
            
        except Exception as e:
            print(f"✗ Export error: {e}")
    
    def git_push_changes(self):
        """Automatically commit and push changes to GitHub"""
        try:
            # Save current directory
            original_dir = os.getcwd()
            
            # Change to project root directory
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            os.chdir(project_root)
            
            # Check if there are changes to commit
            result = subprocess.run(
                ['git', 'status', '--porcelain', 'project_pages/stock_data.json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if not result.stdout.strip():
                print("ℹ No changes to push (data already up to date)")
                return True
            
            print("\n📤 Pushing changes to GitHub...")
            
            # Add the JSON file
            subprocess.run(
                ['git', 'add', 'project_pages/stock_data.json'],
                check=True,
                timeout=10
            )
            
            # Commit with timestamp
            commit_msg = f"Auto-update stock data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                check=True,
                timeout=10
            )
            
            # Push to remote
            subprocess.run(
                ['git', 'push', 'origin', 'main'],
                check=True,
                timeout=30
            )
            
            print("✓ Successfully pushed to GitHub!")
            print("  Your GitHub Pages site will update in 1-2 minutes")
            
            # Restore original directory
            os.chdir(original_dir)
            return True
            
        except subprocess.TimeoutExpired:
            print("✗ Git operation timed out")
            os.chdir(original_dir)
            return False
        except subprocess.CalledProcessError as e:
            print(f"✗ Git error: {e}")
            os.chdir(original_dir)
            return False
        except Exception as e:
            print(f"✗ Push failed: {e}")
            try:
                os.chdir(original_dir)
            except:
                pass
            return False
    
    def get_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM stock_data")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_data")
        symbols = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM stock_data")
        dates = cursor.fetchone()
        
        print(f"\n{'='*70}")
        print(f"Database Statistics:")
        print(f"  Total Records: {total:,}")
        print(f"  Symbols: {symbols}")
        if dates[0]:
            date_range_days = (datetime.strptime(dates[1], '%Y-%m-%d %H:%M:%S') - 
                             datetime.strptime(dates[0], '%Y-%m-%d %H:%M:%S')).days
            print(f"  Date Range: {dates[0]} to {dates[1]}")
            print(f"  Coverage: {date_range_days} days")
        
        # Per-symbol stats
        print(f"\n  Per Symbol:")
        for symbol in config.SYMBOLS:
            cursor.execute("""
                SELECT COUNT(*), MIN(timestamp), MAX(timestamp)
                FROM stock_data WHERE symbol = ?
            """, (symbol,))
            count, min_date, max_date = cursor.fetchone()
            if count > 0:
                days = (datetime.strptime(max_date, '%Y-%m-%d %H:%M:%S') - 
                       datetime.strptime(min_date, '%Y-%m-%d %H:%M:%S')).days
                print(f"    {symbol}: {count:,} records ({days} days)")
        
        print(f"{'='*70}")
        conn.close()


if __name__ == "__main__":
    collector = IncrementalStockCollector()
    collector.collect_all()
    collector.get_stats()

