import requests
from bs4 import BeautifulSoup
import csv
import statistics as st
import time

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
'referer': 'https://www.screener.in/'}

# input_file = open(f'../ind_niftylargemidcap250list.csv', 'r')
input_file = open(f'../ind_nifty500list.csv', 'r')
csv_reader = csv.reader(input_file)

# output_file = open(f'fundamentalPortfolio.csv', 'w')
output_file = open(f'nifty500.csv', 'w')
csv_writer = csv.writer(output_file)
csv_writer.writerow(['Symbol', 'Industry', 'Price', 'SUE'])


# for row in ['TCS', 'INFY', '3MINDIA']:
for row in csv_reader:
    try:
        stock = row[2]
        # stock = row
        print(stock)
        try:
            url = f'https://www.screener.in/company/{ stock }/consolidated/'
            source = requests.get(url, headers)
            soup = BeautifulSoup(source.text, "lxml")

            # getting lastest price
            price = soup.find_all('span', class_='number')[1].text
            price = price.replace(',', '')
            price = float(price)

        except Exception as e:
            url = f'https://www.screener.in/company/{ stock }/'
            source = requests.get(url, headers)
            soup = BeautifulSoup(source.text, "lxml")

            # getting lastest price
            price = soup.find_all('span', class_='number')[1].text
            price = price.replace(',', '')
            price = float(price)

        # getting eps data
        section = soup.find('section', id="quarters")
        table_rows = section.find_all('tr')
        cells = table_rows[11].find_all('td')[1:]
        cells = [float(cell.text.replace(',', '')) for cell in cells]

        cells = [0] * (12 - len(cells)) + cells # for taking care of missing data

        eps_change = cells[-1] - cells[-5]
        change = [cells[-i] - cells[-(i + 4)] for i in range(1, 5)]
        sigma = st.stdev(change)

        if(sigma != 0):
            SUE = eps_change / sigma
            csv_writer.writerow([stock, row[1], price, round(SUE, 2)])
            print(stock)

    except Exception as e:
        print(f'{ row[0] } not added as {e}')

    time.sleep(1)


output_file.close()
input_file.close()
