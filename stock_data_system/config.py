"""Configuration for Stock Data Collection System"""

# Polygon.io API credentials
POLYGON_API_KEY = "3rX37ESzYDIL4ZpP9yW9przScqyMMnQI"

# Symbols to track
SYMBOLS = [
    "SPY",   # S&P 500
    "QQQ",   # NASDAQ 100
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "GOOGL", # Google
    "TSLA",  # Tesla
    "NVDA",  # NVIDIA
    "AMZN",  # Amazon
]

# Data settings
INTERVAL = "5"       # 5-minute intervals
TIMESPAN = "minute"  # minute, hour, day, week, month
DAYS_BACK = 60       # Fetch last 60 days of data

# Rate limiting (free tier: 5 calls per minute)
API_CALLS_PER_MINUTE = 5
DELAY_BETWEEN_CALLS = 12  # seconds (60 / 5 = 12)

# Database
DB_PATH = "data/stock_data.db"

# JSON export for web viewer
JSON_PATH = "../project_pages/stock_data.json"

