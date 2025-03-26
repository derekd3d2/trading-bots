import alpaca_trade_api as tradeapi

api = tradeapi.REST(
    'PKEXZJRX4DWKRGSDBBL1',
    'l8gukdWDunZkgoQheAcEWPqGUeMKb2oJaJ4Jcadz',
APCA_BASE_URL = os.getenv("APCA_PAPER_URL", "https://paper-api.alpaca.markets")
)

print(api.get_account())
