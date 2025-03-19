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
BOT_FILES = {
    "trading_bot.py": "bot_backups/trading_bot_backup",
}
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

def fetch_new_ai_code(bot_file):
    """Fetch AI-generated improvements for the given bot file."""
    try:
        log_message(f"🔄 Fetching AI improvements for {bot_file}...")
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": f"Improve and optimize the Python code for {bot_file}. Make it more efficient, accurate, and robust for stock trading."}]
        )

        new_code = response.choices[0].message.content

        # ✅ Ensure proper UTF-8 encoding, replacing invalid characters
        clean_code = new_code.encode("utf-8", errors="replace").decode("utf-8")

        # ✅ Remove non-ASCII characters (force pure English code)
        clean_code = ''.join([c if ord(c) < 128 else '?' for c in clean_code])

        return clean_code

    except Exception as e:
        log_message(f"❌ Error fetching AI-generated code for {bot_file}: {str(e)}")
        return None

def update_bot(bot_file):
    """Fetch AI updates, test, and apply if successful."""
    new_code = fetch_new_ai_code(bot_file)
    if new_code is None:
        return

    # ✅ Save backup of old bot before overwriting
    backup_path = f"{BOT_FILES[bot_file]}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.py"
    shutil.copy(bot_file, backup_path)
    log_message(f"✅ Backup saved: {backup_path}")

    # ✅ Save new bot code to a temporary file for testing
    temp_bot_file = f"{bot_file}_temp"
    with open(temp_bot_file, "w", encoding="utf-8") as bot_file:
        bot_file.write(new_code)

    # ✅ Backtest new bot before replacing the old one
    if backtest_new_bot(temp_bot_file):
        shutil.move(temp_bot_file, bot_file)
        log_message(f"✅ {bot_file} updated successfully!")
        restart_trading_bot()
    else:
        log_message(f"❌ {bot_file} failed testing. Keeping the old version.")
        os.remove(temp_bot_file)

def backtest_new_bot(bot_file):
    """Simulated backtesting of the new bot (placeholder for real implementation)."""
    log_message(f"🔄 Running backtest on {bot_file}...")

    try:
        result = subprocess.run(["python3", bot_file, "--backtest"], capture_output=True, text=True, timeout=60)
        log_message(f"📊 Backtest Output: {result.stdout}")

        if "SUCCESS" in result.stdout:  # ✅ Placeholder success condition
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
        subprocess.run(["pkill", "-f", "trading_bot.py"], check=False)
        subprocess.Popen("nohup python3 trading_bot.py > output.log 2>&1 &", shell=True)
        log_message("✅ Trading Bot restarted successfully!")

    except Exception as e:
        log_message(f"❌ Error restarting the bot: {str(e)}")

# ✅ Run this script every 12 hours
schedule.every(12).hours.do(lambda: update_bot("day_trading_bot.py"))

if __name__ == "__main__":
    log_message("🚀 AI Auto-Update System is Running...")
    update_bot("trading_bot.py")  # Run immediately on startup

    while True:
        schedule.run_pending()
        time.sleep(43200)  # Check every 12  hours
