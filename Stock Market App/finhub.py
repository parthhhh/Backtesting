import requests
import pandas as pd


r = requests.get('https://finnhub.io/api/v1/indicator?symbol=AAPL&resolution=D&from=1613826907&to=1627042507&indicator=rsi&timeperiod=14&seriestype=c&token=c3t09p2ad3ide69ean6g')
df = pd.DataFrame(r.json())
df.to_excel('rsi14 day aapl.xlsx')