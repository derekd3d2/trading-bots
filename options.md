🔹 1. Signal Generation Bots (Pull data from QuiverQuant)
File Name	Purpose	Output File
gov_signals.py	Pulls government contract wins	gov_signals.json
insider_signal_bot.py	Pulls insider buying transactions	insider_signals.json
congress_signal_bot.py (assumed name)	Pulls Congress trades	congress_signals.json
🔹 2. Signal → Options Conversion Bots
File Name	Converts From	Converts To
Options_gov_signals.py	gov_signals.json	options_signals.json (✅ should be → options_gov_signals.json)
insider_signals_to_options.py	insider_signals.json	options_signals.json (✅ should be → options_insider_signals.json)
🔹 3. Master Options Trading Bot
File Name	Purpose
options_trading_bot.py	Reads from options_signals.json and places trades (simulated paper trades with contract sizing and expiration logic)
🔹 4. Sell Management & Summary
File Name	Purpose
options_sell_bot.py	Enforces take-profit / stop-loss / expiry rules
options_daily_summary.py	Shows dashboard of open/closed positions


🔁 Congress Pipeline Verified:
Step	✅ Result
options_signal_creator_congress.py	Pulled & filtered top 25 profitable reps
congress_signals.json	✅ Created (65 trades)
options_signals_congress.py	✅ Converted to options_congress_signals.json
