# Stock Data Collection System

A Python-based system that collects 5-minute interval stock data using Polygon.io API and provides a clean web interface for viewing and downloading the data.

## Features

- **Real Historical Data**: 60 days of 5-minute interval OHLCV data from Polygon.io
- **8 Major Symbols**: SPY, QQQ, AAPL, MSFT, GOOGL, TSLA, NVDA, AMZN
- **SQLite Database**: Efficient local storage with indexed queries
- **Web Viewer**: Clean HTML/JS interface to browse and filter data
- **CSV Export**: Download any time period for analysis

## Data Stats

- **Total Records**: 63,232+
- **Interval**: 5-minute bars
- **Period**: Last 60 days
- **Date Range**: August 11, 2025 - October 9, 2025

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Automated Collection (Recommended)

The scheduler is now running automatically in the background!

```bash
# Check if running
ps aux | grep daily_scheduler

# View logs
tail -f scheduler.log

# Stop scheduler (if needed)
./stop_scheduler.sh

# Restart scheduler (if needed)
./start_scheduler.sh
```

The scheduler:
- ✅ **Running now** - Started automatically
- ✅ **Collects daily at 5:30 PM ET** (after market close)
- ✅ **Only fetches new data** (incremental updates)
- ✅ **Skips weekends** automatically
- ✅ **Hands-off** - no manual intervention needed

### Manual Collection (Optional)

```bash
# Force an update now
python incremental_collector.py

# Re-fetch full 60 days (if needed)
python polygon_collector.py
```

### How It Works

1. **First Run**: Fetches 60 days of historical data
2. **Subsequent Runs**: Only fetches new data since last collection
3. **Growing Dataset**: Data accumulates over time (not replaced)
4. **Duplicate Prevention**: UNIQUE constraint prevents duplicate records

The web viewer updates automatically with each collection run.

## Files

- `polygon_collector.py` - Main data collection script
- `config.py` - API key and configuration
- `data/stock_data.db` - SQLite database
- `../project_pages/stock_data.json` - Web viewer data export

