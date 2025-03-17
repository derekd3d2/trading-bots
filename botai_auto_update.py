import os
import subprocess
import schedule
import time
import openai
import datetime
import shutil

# ✅ Force UTF-8 encoding to avoid errors
os.environ["PYTHONIOENCODING"] = "utf-8"

# ✅ Fetch OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ File Paths
BOT_FILE = "trading_bot.py"
BACKUP_DIR = "bot_backups"
LOG_FILE = "bot_update.log"

# ✅ Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

def log_message(message):
    """Log updates to a file for debugging."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} - {message}\n")
    print(message)

def fetch_new_trading_bot_code():
    """Fetch AI-generated trading bot code from OpenAI GPT-4."""
    try:
        log_message("🔄 Fetching new trading bot code from OpenAI...")
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Generate optimized Python code for an AI stock trading bot."}]
        )

        new_code = response.choices[0].message.content

        # ✅ Ensure proper UTF-8 encoding, replacing invalid characters
        clean_code = new_code.encode("utf-8", errors="replace").decode("utf-8")

        # ✅ Remove non-ASCII characters (force pure English code)
        clean_code = ''.join([c if ord(c) < 128 else '?' for c in clean_code])


        # ✅ Ensure proper UTF-8 encoding and handle errors gracefully
        clean_code = new_code.encode("utf-8", errors="replace").decode("utf-8")

        # ✅ Save backup of old bot before overwriting
        backup_path = os.path.join(BACKUP_DIR, f"trading_bot_backup_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.py")
        shutil.copy(BOT_FILE, backup_path)
        log_message(f"✅ Backup saved: {backup_path}")

        # ✅ Save new bot code to a temporary file for testing
        temp_bot_file = "trading_bot_temp.py"
        with open(temp_bot_file, "w", encoding="utf-8") as bot_file:
            bot_file.write(clean_code)

        # ✅ Backtest new bot before replacing the old one
        if backtest_new_bot(temp_bot_file):
            shutil.move(temp_bot_file, BOT_FILE)
            log_message("✅ New bot passed backtesting and was updated successfully!")
            restart_trading_bot()
        else:
            log_message("❌ New bot failed backtesting. Keeping the old version.")
            os.remove(temp_bot_file)

    except Exception as e:
        log_message(f"❌ Error processing OpenAI response: {str(e)}")

def backtest_new_bot(bot_file):
    """Simulated backtesting of the new bot (placeholder for real implementation)."""
    log_message(f"🔄 Running backtest on {bot_file}...")

    try:
        # ✅ Run a subprocess to execute the bot's backtest function
        result = subprocess.run(["python3", bot_file, "--backtest"], capture_output=True, text=True, timeout=60)

        # ✅ Log backtest results
        log_message(f"📊 Backtest Output: {result.stdout}")

        if "SUCCESS" in result.stdout:  # ✅ This is a placeholder success condition
            log_message("✅ New bot passed backtesting!")
            return True
        else:
            log_message("❌ New bot did NOT perform better than the old one.")
            return False

    except Exception as e:
        log_message(f"❌ Backtesting error: {str(e)}")
        return False

def restart_trading_bot():
    """Restart the trading bot after a successful update."""
    try:
        subprocess.run(["pkill", "-f", BOT_FILE], check=False)
        subprocess.Popen(f"nohup python3 {BOT_FILE} > output.log 2>&1 &", shell=True)
        log_message("✅ Trading Bot restarted successfully!")

    except Exception as e:
        log_message(f"❌ Error restarting the bot: {str(e)}")

# ✅ Run this script every 12 hours
schedule.every(12).hours.do(fetch_new_trading_bot_code)

if __name__ == "__main__":
    log_message("🚀 AI Auto-Update System is Running...")
    fetch_new_trading_bot_code()  # Run immediately on startup
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour
