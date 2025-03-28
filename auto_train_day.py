#!/usr/bin/env python3

import subprocess

def run(script, desc):
    print(f"\n🔁 Running: {desc}")
    result = subprocess.run(["python3", script])
    if result.returncode != 0:
        print(f"❌ {desc} failed.")
    else:
        print(f"✅ {desc} complete.")

if __name__ == "__main__":
    print("🧠 ALOHA DAY TRADE RETRAINING STARTING")
    run("label_day_trades.py", "Label Day Trades")
    run("train_model_day.py", "Train Day Trade Model")
    print("✅ Auto-retraining (Day) complete.\n")
