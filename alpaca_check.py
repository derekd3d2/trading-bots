# test_alpaca_connection.py
import os
import requests

api_key = os.getenv("APCA_API_KEY_ID")
secret_key = os.getenv("APCA_API_SECRET_KEY")
base_url = os.getenv("APCA_API_BASE_URL")

headers = {
    "APCA-API-KEY-ID": api_key,
    "APCA-API-SECRET-KEY": secret_key
}

response = requests.get(f"{base_url}/v2/account", headers=headers)
print("Status Code:", response.status_code)
print("Response:", response.json())
