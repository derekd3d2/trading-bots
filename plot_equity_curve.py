import pandas as pd
import matplotlib.pyplot as plt

# Load trade history
trade_history = pd.read_csv('trade_history.csv', parse_dates=['date'])

# Sort by date
trade_history.sort_values('date', inplace=True)

# Calculate cumulative equity
trade_history['cumulative_pnl'] = trade_history['profit_loss'].cumsum()

# Plot Equity Curve
plt.figure(figsize=(12, 6))
plt.plot(trade_history['date'], trade_history['cumulative_pnl'], marker='o')
plt.title('Equity Curve - Cumulative P&L Over Time')
plt.xlabel('Date')
plt.ylabel('Cumulative Profit/Loss ($)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Save and display the plot
plt.savefig('equity_curve.png')
plt.show()
