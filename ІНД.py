from binance.client import Client
import pandas as pd
import numpy as np
from ta import trend, momentum, volume
from dataclasses import dataclass
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

@dataclass
class Trade:
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    side: str
    profit_pct: float

class Strategy:
    def __init__(self, tp_pct=0.02, sl_pct=0.01):
        self.tp_pct = tp_pct
        self.sl_pct = sl_pct
        self.trades = []

    def generate_indicators(self, df):
        df['ema_20'] = trend.ema_indicator(df['close'], window=20)
        df['vwap'] = volume.volume_weighted_average_price(df['high'], df['low'], df['close'], df['volume'], window=20)
        df['rsi'] = momentum.rsi(df['close'], window=14)
        macd = trend.MACD(df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['rsi_prev'] = df['rsi'].shift(1)
        return df

    def check_entry_long(self, row):
        return row['macd'] > row['macd_signal'] and row['vwap'] > row['ema_20'] and row['rsi'] < 30

    def check_entry_short(self, row):
        return row['rsi_prev'] > 70 and row['rsi'] < 70 and row['vwap'] < row['ema_20']

    def backtest(self, df):
        position = None
        entry_price = 0
        entry_time = None

        for i in range(1, len(df)):
            row = df.iloc[i]
            if position is None:
                if self.check_entry_long(row):
                    position = "LONG"
                    entry_price = row['close']
                    entry_time = row['time']
                elif self.check_entry_short(row):
                    position = "SHORT"
                    entry_price = row['close']
                    entry_time = row['time']
            else:
                if position == "LONG":
                    if row['close'] >= entry_price * (1 + self.tp_pct) or row['close'] <= entry_price * (1 - self.sl_pct):
                        self.trades.append(Trade(entry_time, entry_price, row['time'], row['close'], "LONG",
                                                 (row['close'] - entry_price) / entry_price * 100))
                        position = None
                elif position == "SHORT":
                    if row['close'] <= entry_price * (1 - self.tp_pct) or row['close'] >= entry_price * (1 + self.sl_pct):
                        self.trades.append(Trade(entry_time, entry_price, row['time'], row['close'], "SHORT",
                                                 (entry_price - row['close']) / entry_price * 100))
                        position = None

    def performance(self):
        profits = [trade.profit_pct for trade in self.trades]
        win_trades = [p for p in profits if p > 0]
        loss_trades = [p for p in profits if p <= 0]
        pf = sum(win_trades) / abs(sum(loss_trades)) if loss_trades else float('inf')
        wr = len(win_trades) / len(profits) * 100 if profits else 0
        pnl = sum(profits)
        max_dd = self.calculate_max_drawdown(profits)
        return {"Profit Factor": pf, "Win Rate": wr, "PnL%": pnl, "Max Drawdown%": max_dd}

    def calculate_max_drawdown(self, profits):
        cumulative = np.cumsum(profits)
        peak = np.maximum.accumulate(cumulative)
        drawdown = (peak - cumulative) / peak
        return np.max(drawdown) * 100 if len(drawdown) > 0 else 0

def get_binance_data(symbol='BTCUSDT', interval='1m', lookback_minutes=2880):
    client = Client() 

    end_str = datetime.utcnow().strftime("%d %b %Y %H:%M:%S")
    start_str = (datetime.utcnow() - timedelta(minutes=lookback_minutes)).strftime("%d %b %Y %H:%M:%S")

    klines = client.get_historical_klines(
        symbol=symbol,
        interval=interval,
        start_str=start_str,
        end_str=end_str
    )

    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
    ])

    df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df[['time', 'open', 'high', 'low', 'close', 'volume']]

if __name__ == "__main__":
    df = get_binance_data('BTCUSDT', interval='1m', lookback_minutes=2880)
    strategy = Strategy(tp_pct=0.02, sl_pct=0.01)
    df = strategy.generate_indicators(df)
    strategy.backtest(df)
    stats = strategy.performance()
    print("📊 Performance Metrics:")
    for k, v in stats.items():
        print(f"{k}: {v:.2f}")

    plt.figure(figsize=(12,6))
    plt.plot(df['time'], df['close'], label='Close Price', color='blue', alpha=0.5)

    for trade in strategy.trades:
        color = 'green' if trade.side == 'LONG' else 'red'
        marker = '^' if trade.side == 'LONG' else 'v'
        plt.scatter(trade.entry_time, trade.entry_price, color=color, marker=marker, s=80)

    plt.title('BTCUSDT 1m - Trade Signals')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
