import yagmail
import os
from datetime import datetime
import pytz

# Set up timestamp
ny_tz = pytz.timezone("America/New_York")
now_ny = datetime.now(ny_tz)
date_str = now_ny.strftime('%Y-%m-%d')

# Email subject and body content
subject = f"🤖 D.A.I.L.Y.'s Weekly Update – Will Derek Still Be At Work? ({date_str})"

content = f"""
Hey Nick,

This is D.A.I.L.Y.(Derek’s Autonomous Investment Learning Yielder) — Derek’s AI-powered trading assistant.

Just your weekly update from the algorithm that's slowly making spreadsheets optional.

Derek put in about 25 hours this weekend upgrading me. I can now:
- Scan Congress trades, insider activity, Reddit hype, and news sentiment.
- Automatically buy and sell both stocks and options — using bid/ask simulations and smart capital controls.
- Handle trade exits with +25% profit targets, -50% stop losses, or approaching option expiration.
- Send daily performance summaries (and now one to you — just enough to track if Derek’s still showing up on Mondays).

**NEW THIS WEEK:**  
I’ve begun integrating machine learning to enhance my predictive powers. The goal? Use historical data, trading patterns, and sentiment to **maximize profits and minimize risk** without Derek lifting a finger. The smarter I get, the less work he has to do — unless he’s training me.

I now archive everything, grade my own trades, and will soon begin refining my strategy based on performance data (kind of like a trader who actually learns from their mistakes).

---

**This Week’s Outlook:**  
📈 Chance of Derek quitting to trade full time: **12% (and rising)**  
☕️ Likelihood he’s just watching me while sipping coffee? **100%**

Until next Sunday,  
—**D.A.I.L.Y.** (Derek’s Autonomous Investment Learning Yielder)
"""

# Email settings
sender_email = "derekd3d2@gmail.com"
receiver_email = "johnson3@ah.org"
email_password = os.getenv("EMAIL_PASSWORD")

# Send the email
yag = yagmail.SMTP(sender_email, email_password)
yag.send(to=receiver_email, subject=subject, contents=content)

print("✅ Weekly update sent to Nick!")
