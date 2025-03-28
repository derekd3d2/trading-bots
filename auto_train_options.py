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
    print("🧠 ALOHA OPTIONS RETRAINING STARTING")
    run("label_option_trades.py", "Label Option Trades")
    run("train_model_options.py", "Train Options Model")
    print("✅ Auto-retraining (Options) complete.\n")
