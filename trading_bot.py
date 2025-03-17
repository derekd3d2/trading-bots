import ib_insync
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to IB Gateway
ib = ib_insync.IB()
ib.connect('127.0.0.1', 7497, clientId=1)

class TradingBot:
    def __init__(self):
        self.account = ib.accountSummary()
        logging.info("Trading bot initialized and connected to IB Gateway.")
    
    def get_market_data(self, symbol):
        contract = ib_insync.Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(contract)
        market_data = ib.reqMktData(contract)
        ib.sleep(1)  # Give time for market data to update
        return market_data
    
    def place_order(self, symbol, action, quantity, order_type='MKT', limit_price=None):
        contract = ib_insync.Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(contract)
        
        if order_type == 'MKT':
            order = ib_insync.MarketOrder(action, quantity)
        elif order_type == 'LMT' and limit_price:
            order = ib_insync.LimitOrder(action, quantity, limit_price)
        else:
            logging.error("Invalid order type or missing limit price.")
            return
        
        trade = ib.placeOrder(contract, order)
        logging.info(f"Order placed: {action} {quantity} {symbol} at {datetime.now()}.")
        return trade
    
    def get_open_positions(self):
        positions = ib.positions()
        return positions
    
    def close_position(self, symbol):
        positions = self.get_open_positions()
        for position in positions:
            if position.contract.symbol == symbol:
                action = 'SELL' if position.position > 0 else 'BUY'
                self.place_order(symbol, action, abs(position.position))
                logging.info(f"Closed position: {symbol}")
    
    def stop_loss_take_profit(self, symbol, stop_loss_price, take_profit_price):
        contract = ib_insync.Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(contract)
        
        stop_order = ib_insync.StopOrder('SELL', 1, stop_loss_price)
        take_profit_order = ib_insync.LimitOrder('SELL', 1, take_profit_price)
        
        ib.placeOrder(contract, stop_order)
        ib.placeOrder(contract, take_profit_order)
        logging.info(f"Stop-loss at {stop_loss_price} and take-profit at {take_profit_price} set for {symbol}.")

# Example usage
if __name__ == "__main__":
    bot = TradingBot()
    data = bot.get_market_data('AAPL')
    print(f"AAPL Price: {data.last}")
    bot.place_order('AAPL', 'BUY', 1)
    bot.stop_loss_take_profit('AAPL', 170, 190)

