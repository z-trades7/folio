"""
Stock Data Collector using Polygon.io API
Collects 5-minute interval data and stores in SQLite database
"""

import requests
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import config


class PolygonStockCollector:
    """Collects and stores intraday stock data from Polygon.io"""
    
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
        print("✓ Database initialized")
    
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
                # Accept both 'OK' and 'DELAYED' status (delayed data is still valid)
                if data.get('status') in ['OK', 'DELAYED'] and data.get('resultsCount', 0) > 0:
                    return data.get('results', [])
                else:
                    print(f"  ⚠ No data returned: {data.get('status', 'UNKNOWN')}")
                    return []
            else:
                print(f"  ✗ API Error {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            print(f"  ✗ Request failed: {e}")
            return []
    
    def collect_symbol(self, symbol):
        """Collect data for a single symbol"""
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=config.DAYS_BACK)
            
            from_str = from_date.strftime('%Y-%m-%d')
            to_str = to_date.strftime('%Y-%m-%d')
            
            print(f"Fetching {symbol} ({from_str} to {to_str})...")
            
            # Fetch data from Polygon
            results = self.fetch_aggregates(symbol, from_str, to_str)
            
            if not results:
                print(f"  ⚠ No data for {symbol}")
                return 0
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            records_added = 0
            
            for bar in results:
                try:
                    # Convert Unix timestamp (milliseconds) to datetime
                    timestamp = datetime.fromtimestamp(bar['t'] / 1000)
                    
                    conn.execute("""
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
                    records_added += 1
                except Exception as e:
                    pass  # Duplicate or error, skip
            
            conn.commit()
            conn.close()
            
            print(f"  ✓ Added {records_added:,} records")
            return records_added
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return 0
    
    def collect_all(self):
        """Collect data for all symbols"""
        print(f"\n{'='*70}")
        print(f"Polygon.io Stock Data Collection")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Period: Last {config.DAYS_BACK} days | Interval: {config.INTERVAL} {config.TIMESPAN}")
        print(f"{'='*70}\n")
        
        total = 0
        for i, symbol in enumerate(config.SYMBOLS, 1):
            print(f"[{i}/{len(config.SYMBOLS)}] {symbol}")
            total += self.collect_symbol(symbol)
            
            # Rate limiting - respect API limits
            if i < len(config.SYMBOLS):
                print(f"  ⏱ Waiting {config.DELAY_BETWEEN_CALLS}s (rate limit)...")
                time.sleep(config.DELAY_BETWEEN_CALLS)
        
        print(f"\n{'='*70}")
        print(f"Collection complete: {total:,} total records added")
        print(f"{'='*70}\n")
        
        # Export to JSON for web viewer
        self.export_to_json()
    
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
                    
                    stats['symbols'].append({
                        'symbol': symbol,
                        'records': len(df),
                        'latest': df.iloc[0]['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                        'price': float(df.iloc[0]['close'])
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
        
        conn.close()
        
        print(f"\n{'='*70}")
        print(f"Database Statistics:")
        print(f"  Total Records: {total:,}")
        print(f"  Symbols: {symbols}")
        if dates[0]:
            print(f"  Date Range: {dates[0]} to {dates[1]}")
        print(f"{'='*70}")


if __name__ == "__main__":
    collector = PolygonStockCollector()
    collector.collect_all()
    collector.get_stats()

