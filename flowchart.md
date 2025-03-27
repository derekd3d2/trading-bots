     +--------------------+
     | manager.py (NEW)   |
     | 1) fetch data      |
     | 2) aggregate       |
     | 3) ML filters      |
     | 4) sentiment       |
     | 5) run bots        |
     +---------+----------+
               |
               v
+--------------------------+
| GATHERERS (ms_ scripts) |
|  ms_congress.py          |
|  ms_insider_trading.py   |
|  ms_wsb.py               |
|  ms_gov.py               |
|  ...                     |
+------------+-------------+
             |
             v
+---------------------------+
| AGGREGATOR / aggregator.py|
| - merges data from gather |
| - produce day_trading_signals.json     |
| - produce short_signals.json           |
|   (or do it all in one)                |
+------------+-------------+
             |
             +-----> (Optional: ML) predict_day_trades.py
             |            - reads day_trading_signals.json
             |            - saves filtered_day_signals.json
             |
             v
+--------------------------+
| market_sentiment.py      |
| -> market_sentiment.json |
+------------+-------------+
             |
             v
+--------------------------+
| day_trading_bot.py       |
| short_trading_bot.py     |
| (momentum_*_bot.py?)     |
+------------+-------------+

Options Pipeline (could be in manager.py or separate):
               |
               v
+--------------------------+
| options_main.py          |
| -> runs options gatherers |
| -> merges into options_signals.json
| (Optional: predict_option_trades.py)
| -> runs options_trading_bot.py
+--------------------------+


OR 

trading-bots/
  ├── manager.py                        <-- Single "master" pipeline script
  ├── market_sentiment.py               <-- Still a dedicated sentiment script
  ├── aggregator/
  │     ├── aggregator.py               <-- Merges signals for day & short
  │     └── options_aggregator.py       <-- If you want a separate aggregator for options
  ├── gatherers/
  │     ├── ms_congress.py
  │     ├── ms_insider_trading.py
  │     ├── ms_gov.py
  │     ├── ms_wsb.py
  │     └── (any others fetching data)
  ├── day_trading_bot.py
  ├── short_trading_bot.py
  ├── options_main.py
  ├── options_trading_bot.py
  ├── (momentum_long_bot.py, momentum_short_bot.py) [Optional or integrated]
  ├── ML/
  │     ├── train_model_day.py
  │     ├── train_model_options.py
  │     ├── predict_day_trades.py
  │     └── predict_option_trades.py
  ├── logs/
  ├── config.py
  └── .env or .bashrc_custom

