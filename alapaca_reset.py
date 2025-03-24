import requests
import os

API_KEY = os.getenv("APCA_API_KEY_ID")
SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")

url = "https://paper-api.alpaca.markets/v2/account/reset"

headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
}

response = requests.post(url, headers=headers)

print("Reset status:", response.status_code, response.text)
