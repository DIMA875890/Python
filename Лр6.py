import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

data = {
    'time': [
        '2025-04-24 23:51:00', '2025-04-24 23:52:00', '2025-04-24 23:53:00',
        '2025-04-24 23:54:00', '2025-04-24 23:55:00', '2025-04-24 23:56:00',
        '2025-04-24 23:57:00', '2025-04-24 23:58:00', '2025-04-24 23:59:00',
        '2025-04-25 00:00:00'
    ],
    'RSI 14': [60.444481, 54.819124, 55.808565, 52.087187, 50.966980, 56.037016, 56.351634, 64.620248, 68.974059, 57.699181],
    'RSI 27': [62.057532, 59.100853, 59.547962, 57.568143, 56.966155, 59.173691, 59.313986, 63.286907, 65.680711, 59.718471],
    'RSI 100': [56.681147, 55.944096, 56.072989, 55.575452, 55.423414, 56.028444, 56.067432, 57.229065, 58.000652, 56.483037]
}

df = pd.DataFrame(data)
df['time'] = pd.to_datetime(df['time'])  

plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.bar(df['time'], df['RSI 27'], color='skyblue')
plt.title('bar - RSI 27')
plt.xticks(rotation=45)

plt.subplot(1, 3, 2)
plt.scatter(df['time'], df['RSI 14'], color='green')
plt.title('scatter - RSI 14')
plt.xticks(rotation=45)

plt.subplot(1, 3, 3)
plt.plot(df['time'], df['RSI 100'], color='red', marker='o')
plt.title('plot - RSI 100')
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('RSI.png') 
plt.show()  

