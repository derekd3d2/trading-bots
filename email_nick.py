import yagmail
import os
import openai
from datetime import datetime
import pytz

# === Load API Key ===
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Email Config ===
sender_email = "derekd3d2@gmail.com"
receiver_email = "nick@example.com"  # Replace with Nick's actual email if needed
email_password = os.getenv("EMAIL_PASSWORD")

# === Generate Weekly Progress Update ===
ny_tz = pytz.timezone("America/New_York")
now_ny = datetime.now(ny_tz)

date_str = now_ny.strftime("%B %d, %Y")
prompt = f"""
Write a humorous and friendly progress update email from Daily, an AI trading assistant built by Derek, to Nick, the CFO at Derek's workplace. Daily should refer to itself in the first person and explain what it has accomplished this week in simple terms. Mention that it now runs a full trading system automatically (stocks, options, research, auto-selling, and email reporting). Joke that Derek's job is still safe for now, but the bot is getting smarter. End with something fun like 'Chance of replacing Derek this year: 12% (and rising).'"""

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are Daily, a friendly and witty AI trading bot assistant built by Derek."},
        {"role": "user", "content": prompt}
    ]
)

content = response["choices"][0]["message"]["content"]
subject = f"🤖 Weekly Trading Bot Progress Report – {date_str}"

# === Send Email ===
yag = yagmail.SMTP(sender_email, email_password)
yag.send(
    to=receiver_email,
    subject=subject,
    contents=content
)

print("✅ Weekly update sent to Nick!")
