import requests
from bs4 import BeautifulSoup
import csv
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# these portfolio works well on small cap stocks
# lower the score better the stock
# rebalance in 3 months

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
'referer': 'https://www.screener.in/'}

# input_file = open(f'../ind_niftylargemidcap250list.csv', 'r')
input_file = open(f'../ind_niftysmallcap250list.csv', 'r')
csv_reader = csv.reader(input_file)

df = pd.DataFrame(columns=['Stock', 'Price', 'B/P', 'E/P', 'ROCE', 'OPM', 'ROA', 'ret'])

for row in csv_reader:
    time.sleep(1)
# for stock in ['HDFCBANK', 'ITC', 'CROMPTON']:
    try:
        stock = row[2]
        try:
            url = f'https://www.screener.in/company/{ stock }/consolidated/'
            source = requests.get(url, headers)
            soup = BeautifulSoup(source.text, "lxml")

            # getting lastest price
            span_list = soup.find_all('span', class_='number')
            price = span_list[1].text
            price = price.replace(',', '')
            price = float(price)

            # getting roce
            roce = span_list[6].text
            roce = roce.replace('%', '')
            roce = float(roce)

        except Exception as e:
            url = f'https://www.screener.in/company/{ stock }/'
            source = requests.get(url, headers)
            soup = BeautifulSoup(source.text, "lxml")

            # getting lastest price
            span_list = soup.find_all('span', class_='number')
            price = span_list[1].text
            price = price.replace(',', '')
            price = float(price)

            # getting roce
            roce = span_list[6].text
            roce = roce.replace('%', '')
            roce = float(roce)

        # Value
        # getting lastest book value
        book = span_list[3].text
        book = book.replace(',', '')
        book = float(book)

        book_price = book/price

        # getting lastest book value
        pe = span_list[4].text
        pe = pe.replace(',', '')
        pe = float(pe)

        earning_price = pe ** -1

        # Quality
        # getting opm
        section = soup.find('section', id="profit-loss")
        table_rows = section.find_all('tr')
        try:
            opm = table_rows[4].find_all('td')[-1].text
            opm = opm.replace('%', '')
            opm = float(opm)
        except ValueError:
            opm = table_rows[5].find_all('td')[-1].text
            opm = opm.replace('%', '')
            opm = float(opm)

        # getting net profit
        net_profit = table_rows[10].find_all('td')[-1].text
        net_profit = net_profit.replace(',', '')
        net_profit = float(net_profit)

        # getting average assests
        section = soup.find('section', id="balance-sheet")
        table_rows = section.find_all('tr')
        a1 = table_rows[10].find_all('td')[-1].text
        a1 = a1.replace(',', '')
        a1 = float(a1)
        a2 = table_rows[10].find_all('td')[-2].text
        a2 = a2.replace(',', '')
        a2 = float(a2)

        roa = net_profit * 2 / (a1 + a2)

        # momentum
        end = datetime.now() - timedelta(days=30)
        start = end - timedelta(days=365)
        price_data = yf.download(f'{stock}.NS', start=start, end=end)
        price_list = price_data['Adj Close'].to_list()
        ret = (price_list[-1]/price_list[0]) - 1

        df.loc[len(df)] = [stock, price, book_price, earning_price, roce, opm, roa, ret]
        print(stock)

    except Exception as e:
        print(f'{ stock } not added as {e}')

print('Sorting...')
# ranking on basis of different props
for col in ['B/P', 'E/P', 'ROCE', 'OPM', 'ROA', 'ret']:
    df = df.sort_values(by=[col], ascending=False, ignore_index=True)
    df[f'{ col }_rank'] = df.index + 1

# averaging the props under same category
df['Value'] = (df['B/P_rank'] + df['E/P_rank']) / 2
df['Quality'] = (df['ROCE_rank'] + df['OPM_rank'] + df['ROA_rank'])/ 3

df = df.drop(df.loc[:, 'B/P':'ROA_rank'].columns, axis = 1)

print('Calculating score...')
# ranking on basis of categories
for col in ['Value', 'Quality']:
    df = df.sort_values(by=[col], ascending=True, ignore_index=True)
    df[f'{ col }_rank'] = df.index + 1

# final score
df['score'] = 0.4 * df['Value_rank'] + 0.4 * df['ret_rank'] + 0.2 * df['Quality_rank']
df = df.drop(df.loc[:, 'ret_rank':'Quality_rank'].columns, axis = 1)
print('Completed...')
# print(df)
df.to_excel('coreport.xlsx')
# df.to_excel('smallport.xlsx')
input_file.close()
