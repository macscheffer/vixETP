import alpha_vantage
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from models import DB, Ticker, Data

ALPHAVANTAGE_API_KEY = 'SXG08DL4S2EW8SKC'

ts  = TimeSeries(key=ALPHAVANTAGE_API_KEY, output_format='pandas')

def add_ticker(symbol):

    vix = ts.get_intraday(symbol=symbol, interval='1min', outputsize='compact')[0]
    db_ticker = Ticker(ticker=symbol)
    DB.session.add(db_ticker)
    for index in range(len(vix)):
        row = vix.iloc[index]
        time = row.name
        open_, high, low, close, volume = row['1. open'], row['2. high'], row['3. low'], row['4. close'], row['5. volume']
        db_data = Data(datetime=time, open_=open_, high=high, low=low, close=close, volume=volume)
        db_ticker.datas.append(db_data)
        DB.session.add(db_data)
    
    DB.session.commit()

def update_ticker(symbol):
    pass