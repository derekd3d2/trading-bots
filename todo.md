# 🚀 To-Do List

## Immediate Tasks- [ ] make sure twitter threshold is updated for trading bot
- [ ] try to find out how to have AI self learning on  
      update options to not buy so many, create a stronger algrathyum

      fix daily updates emails
  X    fkx crontab -e
X main marker researxh bor needed 
X find kut why main isnt running on auto, but running trading bot manually is woeking  

## Improvements
- [ ] Enhance AI self-updating script logging.
- [ ] Optimize backtesting bot for strategy tuning.
- [ ] purchase https://polygon.io/pricing?product=stocks for fastest real time dats for day trading. 
🧠 What This Means
This is a QuiverQuant data limitation, not your code.

Their /beta/live/twitter endpoint is outdated or no longer maintained.

It’s not usable for live trading decisions in its current state.

We’ll either need to:

Pause Twitter strategy until data resumes

Build our own Twitter crawler (not hard with X API + sentiment lib)

Focus on Insider, Congress, WSB, and Options for now





## Later Tasks
- [X ] Expand datasets: Patents, Insider Trading.

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

✅ What to Do:
You’re fully ready — just wait until:

A few of your day trades are 7+ days old

Then run:

bash
Copy
Edit
python3 label_day_trades.py
Once it prints:

mathematica
Copy
Edit
✅ Labeled 4 trades → day_trade_labels.csv
You can then run:

bash
Copy
Edit
python3 train_model_day.py
✅ Optional: Prep a Cron Job to Auto-Label Daily
Want me to give you a simple cron job line or main.py hook to run the labeler every morning before market open?

Or ready for me to create:

train_model_options.py

predict_day_trades.py

Let’s keep building this AI beast.


✅ Final To-Do List for Today:
1️⃣ Auto-Label Options Trades for Win/Loss
Use option_trade_log.csv

Fetch price 7 days after entry (if available)

Calculate % gain/loss

Label: WIN / LOSS / NEUTRAL

➡️ Will update label_option_trades.py to work with new fill logic

2️⃣ Track Prediction Success
Cross-reference:

filtered_option_signals.json

option_trade_log.csv

Output ML accuracy:

Wins vs losses per source (Congress, Insider, etc.)

Per ticker summary

➡️ We’ll create evaluate_option_predictions.py

3️⃣ Backtest Visualization
Generate P&L curve and win/loss charts

Based on historical option_trade_log.csv

Output simple .png or HTML plot

➡️ Will create plot_options_performance.py

