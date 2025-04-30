from binance import Client
import pandas as pd
from datetime import datetime, timedelta

api_key = ''
api_secret = ''

client = Client(api_key, api_secret)

def fetch_klines(asset: str, start: str, end: str) -> pd.DataFrame:
    klines = client.get_historical_klines(
        symbol=asset,
        interval=Client.KLINE_INTERVAL_1MINUTE,
        start_str=start,
        end_str=end
    )
    df = pd.DataFrame(klines)[[0, 1, 2, 3, 4, 5]]
    df[0] = pd.to_datetime(df[0], unit='ms')
    for i in range(1, 6):
        df[i] = df[i].astype(float)
    df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    return df

def calculate_rsi(prices: pd.Series, period: int) -> pd.Series:
    delta = prices.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rsi = pd.Series(index=prices.index, dtype=float)

    rsi.iloc[period] = 100 - 100 / (1 + (avg_gain.iloc[period] / avg_loss.iloc[period]))

    for i in range(period + 1, len(prices)):
        current_gain = gain.iloc[i]
        current_loss = loss.iloc[i]

        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + current_gain) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + current_loss) / period

        rs = avg_gain.iloc[i] / avg_loss.iloc[i] if avg_loss.iloc[i] != 0 else 0
        rsi.iloc[i] = 100 - 100 / (1 + rs)

    return rsi

def get_rsi_dataframe(asset: str, periods: list) -> pd.DataFrame:
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    df = fetch_klines(
        asset=asset,
        start=str(yesterday),
        end=str(today)
    )

    for period in periods:
        df[f'RSI {period}'] = calculate_rsi(df['close'], period)

    return df[['time'] + [f'RSI {p}' for p in periods]]

rsi_df = get_rsi_dataframe("BTCUSDT", [14, 27, 100])
print(rsi_df.tail(10))  

