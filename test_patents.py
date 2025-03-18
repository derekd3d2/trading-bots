import requests

# ✅ API Endpoint
PATENTS_API_URL = "https://api.quiverquant.com/beta/live/allpatents"

# ✅ API Key (Replace with your actual key securely)
QUIVER_API_KEY = "07fef860afab0e1ed7ad3e8182815a8810c56b9c"

# ✅ Date Range (Ensure it's within 30 days)
params = {
    "date_from": "20250202",  # YYYYMMDD format
    "date_to": "20250302"     # YYYYMMDD format
}

# ✅ Headers with Bearer Token
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {QUIVER_API_KEY}"
}

# ✅ Sending the request
response = requests.get(PATENTS_API_URL, headers=headers, params=params)

# ✅ Checking the response
if response.status_code == 200:
    patents = response.json()
    print("✅ Recent Patents Retrieved Successfully:", patents)
else:
    print(f"❌ API Error {response.status_code}: {response.text}")
