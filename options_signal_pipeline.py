import subprocess
import time

print("\n🧠 Running Options Signal Pipeline (NO trade execution)...")

# === Step 1: Generate Raw Signals ===
signal_creators = [
    "options_signal_creator_congress.py",
    "options_signal_creator_insider.py",
    "options_signal_creator_gov.py",
    "options_signal_creator_wsb.py"
]

for script in signal_creators:
    print(f"\n📥 Generating: {script}")
    subprocess.run(["python3", script])
    time.sleep(1)

# === Step 2: Convert to Options Format ===
signal_converters = [
    "options_signals_congress.py",
    "options_signals_insider.py",
    "options_signals_gov.py",
    "options_signals_wsb.py"
]

for script in signal_converters:
    print(f"\n🔁 Converting: {script}")
    subprocess.run(["python3", script])
    time.sleep(1)

# === Step 3: Merge and Validate ===
print("\n📦 Merging signals into options_signals.json")
subprocess.run(["python3", "options_merge_signals.py"])

# === Step 4: AI Filtering (ML Prediction) ===
print("\n🧠 Filtering with AI model...")
subprocess.run(["python3", "predict_option_trades.py"])

print("\n✅ Options Signal Pipeline Complete. Signals ready for execution.")
