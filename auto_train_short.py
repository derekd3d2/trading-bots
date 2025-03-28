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
    print("🧠 ALOHA SHORT TRADE RETRAINING STARTING")
    run("label_short_trades.py", "Label Short Trades")
    run("train_model_short.py", "Train Short Trade Model")
    print("✅ Auto-retraining (Short) complete.\n")
