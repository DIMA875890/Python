import pandas as pd
import pandas_ta as ta
import numpy as np
import os

data = {
    'Date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06',
             '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10', '2023-01-11', '2023-01-12',
             '2023-01-13', '2023-01-14', '2023-01-15', '2023-01-16', '2023-01-17', '2023-01-18',
             '2023-01-19', '2023-01-20', '2023-01-21', '2023-01-22', '2023-01-23', '2023-01-24',
             '2023-01-25', '2023-01-26', '2023-01-27'],
    'Close': [100, 102, 101, 103, 105, 107, 106, 108, 110, 112, 113, 111, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95]
}

df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

df['High'] = df['Close'] + 1
df['Low'] = df['Close'] - 1

df['RSI'] = ta.rsi(df['Close'], length=14)
df['CCI'] = ta.cci(df['High'], df['Low'], df['Close'], length=20)

ema_12 = ta.ema(df['Close'], length=12)
ema_26 = ta.ema(df['Close'], length=26)
df['MACD'] = ema_12 - ema_26

df.dropna(subset=['RSI', 'CCI', 'MACD'], inplace=True)

def interpret(row):
    rsi = row['RSI']
    cci = row['CCI']
    macd_val = row['MACD']
    
    rsi_signal = 'neutral'
    if rsi < 30:
        rsi_signal = 'oversold'
    elif rsi > 70:
        rsi_signal = 'overbought'
        
    cci_signal = 'neutral'
    if cci < -100:
        cci_signal = 'oversold'
    elif cci > 100:
        cci_signal = 'overbought'

    macd_index = df.index.get_loc(row.name)
    macd_cross = 'neutral'
    if macd_index > 0:
        prev_macd = df.iloc[macd_index - 1]['MACD']
        if prev_macd < 0 and macd_val > 0:
            macd_cross = 'buy'
        elif prev_macd > 0 and macd_val < 0:
            macd_cross = 'sell'

    if (rsi_signal == 'oversold' or cci_signal == 'oversold') and macd_cross == 'buy':
        return 'ціна буде рости'
    elif (rsi_signal == 'overbought' or cci_signal == 'overbought') and macd_cross == 'sell':
        return 'ціна буде падати'
    else:
        return 'ціна не зміниться'

df['meaning'] = df.apply(interpret, axis=1)

result_df = df[['meaning', 'RSI', 'CCI', 'MACD']].copy()
result_df.columns = ['meaning', 'rsi', 'cci', 'macd']

csv_path = os.path.join(os.getcwd(), "123.csv")
result_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

print(f" Файл збережено: {csv_path}")
