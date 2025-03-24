import yagmail
import os
from datetime import datetime

# ✅ Set email credentials & addresses
sender_email = "derekd3d2@gmail.com"
receiver_email = "derekd3d2@gmail.com"
email_password = os.getenv("EMAIL_PASSWORD")

# ✅ Email content
subject = f"Congress Trades Log - {datetime.now().strftime('%Y-%m-%d')}"
content = "Attached is the 12-month Congress trading CSV file."

csv_path = "/home/ubuntu/trading-bots/congress_trades_detailed.csv"

# ✅ Send the email
yag = yagmail.SMTP(sender_email, email_password)
yag.send(
    to=receiver_email,
    subject=subject,
    contents=content,
    attachments=csv_path
)

print("✅ Congress trades CSV sent successfully.")
