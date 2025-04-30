import time
from dataclasses import dataclass
from datetime import datetime
import yfinance as yf
import pandas as pd
import ta

@dataclass
class Signal:
    time: datetime
    asset: str
    quantity: float
    side: str
    entry: float
    take_profit: float
    stop_loss: float
    result: str = "Proceed"

class MyStrategy:
    def __init__(self, symbol="BTC-USD", risk=0.02, tp_sl_ratio=(5, 2)):
        self.symbol = symbol
        self.risk = risk
        self.tp_ratio, self.sl_ratio = tp_sl_ratio

    def get_data(self):
        df = yf.download(self.symbol, period="30d", interval="1h", auto_adjust=False, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        return df

    def calculate_indicators(self, df):
        close = df['Close']
        high = df['High']
        low = df['Low']

        df['rsi'] = ta.momentum.RSIIndicator(close=close, window=14).rsi()
        df['adx'] = ta.trend.ADXIndicator(high=high, low=low, close=close, window=14).adx()
        macd_indicator = ta.trend.MACD(close=close)
        df['macd_diff'] = macd_indicator.macd_diff()
        bb = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
        df['bb_low'] = bb.bollinger_lband()
        df['bb_high'] = bb.bollinger_hband()
        df = df.dropna()
        return df

    def create_signal(self):
        df = self.get_data()
        df = self.calculate_indicators(df)
        row = df.iloc[-1]

        price = row['Close']
        rsi = row['rsi']
        adx = row['adx']
        macd = row['macd_diff']
        bb_low = row['bb_low']
        bb_high = row['bb_high']

        side = None

        print(f"[{datetime.now()}] RSI: {rsi:.2f}, ADX: {adx:.2f}, MACD: {macd:.2f}, Price: {price:.2f}, BB_Low: {bb_low:.2f}, BB_High: {bb_high:.2f}")

        if rsi < 30 and adx > 25 and macd > 0 and price < bb_low:
            side = "BUY"
        elif rsi > 70 and adx > 25 and macd < 0 and price > bb_high:
            side = "SELL"

        if side:
            sl_pct = self.sl_ratio / 100
            tp_pct = self.tp_ratio / 100

            take_profit = round(price * (1 + tp_pct), 2) if side == "BUY" else round(price * (1 - tp_pct), 2)
            stop_loss = round(price * (1 - sl_pct), 2) if side == "BUY" else round(price * (1 + sl_pct), 2)
            quantity = round(1000 / price, 4)

            return Signal(
                time=datetime.now(),
                asset=self.symbol,
                quantity=quantity,
                side=side,
                entry=price,
                take_profit=take_profit,
                stop_loss=stop_loss
            )
        return None

def monitor(strategy):
    while True:
        try:
            signal = strategy.create_signal()
            if signal:
                print(f"[{signal.time}] Signal: {signal.side} {signal.asset} at {signal.entry} | TP: {signal.take_profit} | SL: {signal.stop_loss}")
            else:
                print(f"[{datetime.now()}] No signal.")
            time.sleep(60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    strategy = MyStrategy()
    monitor(strategy)
