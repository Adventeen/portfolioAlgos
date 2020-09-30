# portfolioAlgos
The programs of all momentum portfolios

## Libraries Required
- pandas and numpy included in yfinance
- bs4 and requests for web scraping

## [Core Equity Portfolio](https://www.quantconnect.com/tutorials/strategy-library/fundamental-factor-long-short-strategy)
- Gets different attributes of a stock categorized under **Value**(P/B ratio, P/E ratio), **Quality**(OPM, ROCE, ROA) and **Momentum**(Yearly return skipping last month)
- Calculates rank of each stock under every attribute
- Calculates avg rank in each category
- Assigns a weighted score to each stock
- Lower the score better the stock
- Rebalanced Quaterly
- Works well with small cap stocks
