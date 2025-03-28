#!/usr/bin/env python3

import os
import subprocess
import logging
import time
from datetime import datetime

# ------------------------------------------------------------------------------
# 1. CONFIGURE LOGGING
# ------------------------------------------------------------------------------
LOG_FILE = os.path.join(os.getcwd(), "manager.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(console_formatter)
logging.getLogger().addHandler(console_handler)

def log(msg, level=logging.INFO):
    logging.log(level, msg)


# ------------------------------------------------------------------------------
# 2. SCRIPT RUNNER HELPER
# ------------------------------------------------------------------------------
def run_script(script_path, description=""):
    """
    Runs a Python script via subprocess, logs output, and raises an exception if it fails.
    """
    if not os.path.exists(script_path):
        log(f"⚠️ Script not found: {script_path}. Skipping...", logging.WARNING)
        return

    log(f"🚀 Running: {script_path} {f'({description})' if description else ''}")
    try:
        result = subprocess.run(["python3", script_path], capture_output=True, text=True, check=True)
        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                log(f"{script_path} | {line}")
        if result.stderr:
            for line in result.stderr.strip().split("\n"):
                log(f"{script_path} [stderr] {line}", logging.WARNING)
        log(f"✅ Finished: {script_path}")
    except subprocess.CalledProcessError as e:
        log(f"❌ Error running {script_path}:\n{e.stdout}\n{e.stderr}", logging.ERROR)
        raise e
    except Exception as e:
        log(f"❌ Exception running {script_path}: {str(e)}", logging.ERROR)
        raise e


# ------------------------------------------------------------------------------
# 3. MAIN PIPELINE
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    start_time = datetime.now()
    log("============================================")
    log("  ALOHA TRADING - MANAGER PIPELINE STARTED  ")
    log("============================================\n")

    # 3A. Gatherers: Pull data from QuiverQuant / other sources
    # Adjust the file paths if you've placed these scripts in a 'gatherers/' folder.
    gatherers = [
        ("ms_congress.py",        "Fetch Congress trades"),
        ("ms_insider_trading.py", "Fetch Insider trades"),
        ("ms_wsb.py",             "Fetch WSB sentiment"),
        ("ms_gov.py",             "Fetch Gov contracts"),
        # If you have other gatherers like ms_patent_trading.py, add them here
    ]
    for script, desc in gatherers:
        script_path = os.path.join(os.getcwd(), script)  # or "gatherers/" + script if you moved them
        run_script(script_path, desc)
        time.sleep(1)  # brief pause so logs don’t jumbled

    # 3B. Aggregator: merges the gatherers’ outputs into day_trading_signals.json & short_signals.json
    aggregator_script = os.path.join(os.getcwd(), "aggregator.py")
    run_script(aggregator_script, "Aggregating signals for Day & Short")
    time.sleep(1)

    # 3C. Market Sentiment
    market_sentiment_path = os.path.join(os.getcwd(), "market_sentiment.py")
    run_script(market_sentiment_path, "Compute Market Sentiment")
    time.sleep(1)

    # 3D. Run Day & Short Trading Bots
    run_script(os.path.join(os.getcwd(), "day_trading_bot.py"), "Execute Day Trading Bot")
    time.sleep(1)
    run_script(os.path.join(os.getcwd(), "short_trading_bot.py"), "Execute Short Trading Bot")
    time.sleep(1)

    # 3E. Run Options Pipeline (runs gatherers, converters, merger, and trading bot)
    options_script = os.path.join(os.getcwd(), "options_main.py")
    if os.path.exists(options_script):
        run_script(options_script, "Run Options Pipeline")
        time.sleep(1)

    # 3F. ML Prediction Filter for Options
    ml_options_script = os.path.join(os.getcwd(), "predict_option_trades.py")
    if os.path.exists(ml_options_script):
        run_script(ml_options_script, "ML filter for Options")
        time.sleep(1)

    # 3F-2. ML Filter for Day Trades
    ml_day_script = os.path.join(os.getcwd(), "predict_day_trades.py")
    if os.path.exists(ml_day_script):
        run_script(ml_day_script, "ML filter for Day Trades")
        time.sleep(1)

    # 3F-3. ML Filter for Short Trades
    ml_short_script = os.path.join(os.getcwd(), "predict_short_trades.py")
    if os.path.exists(ml_short_script):
        run_script(ml_short_script, "ML filter for Short Trades")
        time.sleep(1)

    # 3G. Wrap up
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    log(f"✅ Aloha Trading Pipeline Complete. Total time: {elapsed:.1f} sec.\n")

