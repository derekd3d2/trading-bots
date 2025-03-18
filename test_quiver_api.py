import http.client

# ✅ Set up connection
conn = http.client.HTTPSConnection("api.quiverquant.com")

# ✅ Define headers
headers = {
    "Accept": "application/json",
    "Authorization": "Bearer 07fef860afab0e1ed7ad3e8182815a8810c56b9c"
}

# ✅ Send request
conn.request("GET", "/beta/live/twitter?date=2025-03-20", headers=headers)

# ✅ Get response
res = conn.getresponse()
data = res.read()

# ✅ Print output
print(data.decode("utf-8"))
