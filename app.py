import os, csv
import pandas as pd
import talib
from flask import Flask, render_template, request
from binance import Client
from patterns import candlestick_patterns
from credentials import api_key
from credentials import api_secret

client = Client(api_key, api_secret)

app = Flask(__name__)

@app.route('/')
def index():
    pattern = request.args.get('pattern', None)
    stocks = {}

    with open ('datasets/crypto.csv') as f:
        for row in csv.reader(f):
            stocks[row[0]] = {'symbol': row[0]}

    if pattern:
        datafiles = os.listdir('datasets/Crypto_Intervals')
        for filename in datafiles:
            df = pd.read_csv('datasets/Crypto_Intervals/{}'.format(filename))
            pattern_function = getattr(talib, pattern)
            symbol = filename.split('.')[0]

            try:
                result = pattern_function(df['open'], df['high'], df['low'], df['close'])
                last = result.tail(1).values[0]
                #print(last)
                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    stocks[symbol][pattern] = None
            except:
                pass

    return render_template('index.html', candlestick_patterns=candlestick_patterns, stocks=stocks, pattern = pattern)

@app.route('/snapshot')
def snapshot():
    with open('datasets/crypto.csv') as f:
        companies = f.read().splitlines()
        for company in companies:
            symbol = company
            bars = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "1 Jan, 2021")
            for line in bars:
                del line[5:]
            df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])
            df.to_csv('datasets/Crypto_Intervals/{}.csv'.format(symbol), index=False)
    return{
        'code': 'success'
    }