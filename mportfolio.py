from statistics import mean
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import math
import csv

st_uni = pd.DataFrame(columns=['Stock', 'Price', 'Slope', 'R_Squared', 'ATR', '100MA', 'No greater than 15%'])

input_file = open(f'../ind_niftylargemidcap250list.csv', 'r')
csv_reader = csv.reader(input_file)

try:
    for row in csv_reader:
        stock = row[2]
        # getting the data
        start = datetime.now() - timedelta(days=160)
        end = datetime.now()
        df = yf.download(f'{stock}.NS', start=start, end=end)
        price = df['Adj Close'].to_list()
        price = price[-91:]

        # preparing the data
        t = [i for i in range(len(price))]
        lnprice = [math.log(i) for i in price]
        x = np.array(t, dtype=np.float64)
        y = np.array(lnprice, dtype=np.float64)

        # getting slope and intercept
        slope = ((mean(x) * mean(y)) - mean(x*y)) / ((mean(x)**2) - mean(x*x))
        intercept = mean(y) - slope * mean(x)
        y_pred = [slope*xi + intercept for xi in x]

        # getting r squared
        s_resd = sum((y - y_pred) ** 2)
        s_tot = sum((y - mean(y)) ** 2)
        r_sq = round(1 - (s_resd/s_tot), 3)
        slope = round(slope, 5)

        # calculating atr and 100ma
        df['ATR1'] = abs(df['High'] - df['Low'])
        df['ATR2'] = abs(df['High'] - df['Close'].shift())
        df['ATR3'] = abs(df['Low'] - df['Close'].shift())
        df['TR'] = df[['ATR1', 'ATR2', 'ATR3']].max(axis=1)
        df['ATR'] = df['TR'].rolling(20).mean()
        df['100MA'] = df['Adj Close'].rolling(100).mean()
        ma = df['100MA'].to_list()[-1]
        atr = df['ATR'].to_list()[-1]

        # checking if any return is greater than 15%
        dret = [((price[i]/price[i-1]) - 1) for i in range(1, len(price))]
        ch = 1
        for ret in dret:
            if(ret >= 0.15):
                ch = 0
                break

        # Adding to universe
        st_uni.loc[len(st_uni)] = [stock, price[-1], slope, r_sq, atr, ma, ch]
        print(stock)
except:
    pass

st_uni.to_excel('portfolio.xlsx')
# print(st_uni)
