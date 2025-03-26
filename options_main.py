import subprocess
import time

# === MAIN PIPELINE RUNNER ===
print("\n🚀 Running full Aloha Options Bot pipeline...")

# === Step 1: Generate Signals ===
signal_creators = [
    "options_signal_creator_congress.py",
    "options_signal_creator_insider.py",
    "options_signal_creator_gov.py",
    "options_signal_creator_wsb.py"
]

for script in signal_creators:
    print(f"\n📥 Running: {script}")
    subprocess.run(["python3", script])
    time.sleep(1)

# === Step 2: Convert Signals to Options ===
signal_converters = [
    "options_signals_congress.py",
    "options_signals_insider.py",
    "options_signals_gov.py",
    "options_signals_wsb.py"
]

for script in signal_converters:
    print(f"\n🔁 Converting signals with: {script}")
    subprocess.run(["python3", script])
    time.sleep(1)

# === Step 3: Merge All Signals ===
print("\n📦 Merging signals into options_signals.json")
subprocess.run(["python3", "options_merge_signals.py"])

# === Step 4: Run AI Filter (ML) ===
#print("\n🧠 Filtering trades using trained AI model...")
#subprocess.run(["python3", "predict_option_trades.py"])

# === Step 5: Execute Trades ===
print("\n💥 Executing trades...")
subprocess.run(["python3", "options_trading_bot.py"])

print("\n✅ Aloha Options Bot run complete.")
