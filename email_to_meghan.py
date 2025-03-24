import yagmail
import os
from datetime import datetime
import pytz

# Set up timestamp
ny_tz = pytz.timezone("America/New_York")
now_ny = datetime.now(ny_tz)

# Message content
subject = f"📩 A Special Update From Your Husband's Trading AI – {now_ny.strftime('%Y-%m-%d')}"

content = f"""
Hi Meghan,

I wanted to give you a quick update on what your husband has been building (with a lot of time, energy, and brainpower), and explain in plain English what’s going on with this new trading system we’ve launched.

🧠 What We Built  
Together, Derek and I have created a fully automated trading system. That means it watches the market, picks trades, places buy and sell orders, tracks results, and even sends a daily performance email — all with zero manual input during the day.  
(Though to be fair, Derek has done **a ton** of work upfront — think of it as building a financial robot that works while he sleeps.)

💼 What It Does  
Every weekday, the system:  
- Scans what members of Congress and company insiders are buying  
- Monitors internet trends (like what’s hot on Reddit or Twitter)  
- Picks stocks or options it believes will grow  
- Automatically buys and sells based on smart rules  
- Sends Derek a full report at the end of each day

We're aiming for around **1% account growth per day** — a high but realistic goal for this type of strategy.

🧠 A Few Quick Terms:
- **Stocks** = Pieces of a company (like buying Apple)  
- **Options** = A cheaper way to bet on a stock going up (**calls**) or down (**puts**)  
- **Shorts** = A way to profit if a stock goes down  
- **Bid/Ask** = The price negotiation between buyers and sellers — our system simulates this too

Derek’s ultimate goal? To grow your family's wealth in the background — using AI, data, and automation. He’s putting in the hard work now so you both can enjoy more freedom later.

Your family’s trading AI assistant 🤖📈
"""

# Email settings
sender_email = "derekd3d2@gmail.com"
receiver_email = "mdickard@gmail.com"
email_password = os.getenv("EMAIL_PASSWORD")

# Send it
yag = yagmail.SMTP(sender_email, email_password)
yag.send(to=receiver_email, subject=subject, contents=content)

print("✅ Email sent to Meghan!")
