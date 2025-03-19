import sqlite3

# ✅ Create a centralized database for all trades
conn = sqlite3.connect('trades.db')
cursor = conn.cursor()

# ✅ Unified Trades Table Creation
cursor.execute("""
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    bot_strategy TEXT,   -- DayTrading, Shorts, Options, Bids, Long
    buy_date TEXT,
    sell_date TEXT,
    buy_price REAL,
    sell_price REAL,
    shares INTEGER,
    status TEXT,         -- OPEN, CLOSED
    additional_info TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("✅ Centralized trades database setup complete!")
