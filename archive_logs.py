import os
import zipfile
from datetime import date

today = date.today().strftime("%Y-%m-%d")
archive_dir = "/home/ubuntu/archives"
os.makedirs(archive_dir, exist_ok=True)

files_to_archive = [
    "main_cron.log",
    "options_cron.log",
    "ms_cron.log",
    "email_summary.log",
    "trade_history.csv",
    "option_trade_log.csv",
    f"daily_summary_{today}.txt",
    "options_positions.json"
]

archive_path = f"{archive_dir}/{today}_archive.zip"

with zipfile.ZipFile(archive_path, 'w') as zipf:
    for filename in files_to_archive:
        path = f"/home/ubuntu/trading-bots/{filename}"
        if os.path.exists(path):
            zipf.write(path, arcname=filename)

print(f"✅ Archived files to {archive_path}")
