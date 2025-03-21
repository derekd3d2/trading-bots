# 🚀 To-Do List

## Immediate Tasks- [ ] make sure twitter threshold is updated for trading bot
- [ ] try to find out how to have AI self learning on  
      fix daily updates emails
      fkx crontab -e
main marker researxh bor needed 
find kut why main isnt running on auto, but running trading bot manually is woeking  

## Improvements
- [ ] Enhance AI self-updating script logging.
- [ ] Optimize backtesting bot for strategy tuning.
- [ ] purchase https://polygon.io/pricing?product=stocks for fastest real time dats for day trading. 




## Later Tasks
- [ ] Expand datasets: Patents, Insider Trading.

## Completed
- [x] Set up automated GitHub to server workflow.


this needs to be in each bot i buy

cursor.execute("""
INSERT INTO trades (ticker, bot_strategy, buy_date, buy_price, shares, status)
VALUES (?, ?, ?, ?, ?, ?)
""", (ticker, "LONG", buy_date, buy_price, shares, "OPEN"))
conn.commit()


# ✅ Create Table for Patents
cursor.execute("""
CREATE TABLE IF NOT EXISTS patents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    patent_number TEXT,
    title TEXT,
    ipc_code TEXT,
    claims INTEGER,
    abstract TEXT,
    publication_date TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
