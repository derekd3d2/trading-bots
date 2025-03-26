import subprocess
import time
from datetime import datetime

def log(msg):
    with open("/home/ubuntu/trading-bots/ms_main.log", "a") as f:
        f.write(f"{datetime.now()} - {msg}\n")

# ✅ List of MS scripts to run
script_names = [
    "ms_congress.py",
    "ms_daytrading_signals.py",
    "ms_insider_trading.py",
    "ms_wsb.py",
    "ms_gov.py"
]

# ✅ Launch each script and simulate terminal command
results = {}

for script in script_names:
    print(f"\nubuntu@ip-172-31-5-132:~/trading-bots$ python3 {script}")
    try:
        proc = subprocess.Popen(
            ["python3", f"/home/ubuntu/trading-bots/{script}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        results[script] = proc
    except Exception as e:
        results[script] = f"❌ Failed to start {script}: {e}"
        log(results[script])

# ✅ Wait 10 seconds before collecting output
time.sleep(10)

# ✅ Display results
for script, proc in results.items():
    if isinstance(proc, str):
        print(proc)
        continue

    stdout, stderr = proc.communicate()

    if stdout:
        print(stdout.strip())
    if stderr:
        print(f"❌ {stderr.strip()}")

    log(f"{script} finished:\n{stdout}\n{stderr}")
