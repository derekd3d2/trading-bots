import os
import sys

REQUIRED_VARS = [
    "ALPACA_ENV",
    "APCA_PAPER_KEY",
    "APCA_PAPER_SECRET",
    "APCA_PAPER_URL",
    "APCA_LIVE_KEY",
    "APCA_LIVE_SECRET",
    "APCA_LIVE_URL",
    "QUIVER_API_KEY"
]

missing = [var for var in REQUIRED_VARS if not os.getenv(var)]

if missing:
    print("❌ Missing environment variables:")
    for var in missing:
        print(f" - {var}")
    sys.exit(1)
else:
    print("✅ All required environment variables are set.")
