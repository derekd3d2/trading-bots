import yagmail
import os
import openai
from datetime import datetime
import pytz

# === Load API Key ===
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Email Config ===
sender_email = "derekd3d2@gmail.com"
receiver_email = "mdickard@gmail.com"
email_password = os.getenv("EMAIL_PASSWORD")

# === Generate Summary Content with OpenAI ===
ny_tz = pytz.timezone("America/New_York")
now_ny = datetime.now(ny_tz)

date_str = now_ny.strftime("%B %d, %Y")
prompt = f"""
Write a friendly and simple weekly update email from an AI trading assistant to Meghan, whose husband has spent the week upgrading his automated stock and options trading system. Meghan understands basic stock buying and selling but not AI, options, or APIs. Explain what the system does, that it's now fully automated, runs daily, generates reports, and that Derek's goal is to use it to eventually replace his job. Add that it's been a big week of improvements and she should be proud of his progress.
"""

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": prompt}
    ]
)

content = response["choices"][0]["message"]["content"]
subject = f"🤖 Weekly Trading System Update – {date_str}"

# === Send Email ===
yag = yagmail.SMTP(sender_email, email_password)
yag.send(
    to=receiver_email,
    subject=subject,
    contents=content
)

print("✅ Weekly update sent to Meghan!")
