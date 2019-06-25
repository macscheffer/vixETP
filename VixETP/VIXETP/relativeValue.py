
from helpers import makeFeaturesLabel, make_dataframe
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd
from models import DB, Ticker, Data
from functools import reduce

def train_model(feature_symbols, prediction_symbol, params = ['open', 'high', 'low', 'close', 'volume']):
    
    

    X, y = makeFeaturesLabel(feature_symbols=feature_symbols, prediction_symbol=prediction_symbol, params=params)
    
    pipe = make_pipeline(StandardScaler(), LogisticRegression())

    model = pipe.fit(X, y)
    probabilities = model.predict_proba(X)[:,1]
    return {'prediction_symbol': prediction_symbol, 'model': model, 'probabilities': probabilities}

def universePredictions(universe = ['SVXY', 'UVXY', 'TVIX', 'VXX', 'SPY']):

    universe_predictions = {'datetimes': get_universe_dates(universe)[:-1]}

    X = makeFeaturesLabel(feature_symbols=feature_symbols, prediction_symbol=prediction_symbol, params=params)[0]

    for symbol in universe:
        temp_universe = universe
        temp_universe.remove(symbol)
        X, y = makeFeaturesLabel(feature_symbols=feature_symbols, prediction_symbol=prediction_symbol, params=params)
        model = getLabelValues(feature_symbols=temp_universe, prediction_symbol=symbol)
        universe_predictions[symbol + 'Probabilities'] = model['probabilities']

    return universe_predictions


def get_universe_dataframe(universe = ['SVXY', 'UVXY', 'TVIX', 'VXX', 'SPY']):

    df = make_dataframe(universe)

    universe_size = len(universe)

    good_dates = []
    all_dates = df.index.levels[0]
    for date in all_dates:
        if len(df.loc[date]) == universe_size:
            good_dates.append(date)
    
    return df.loc[good_dates]


def make_universe_df(universe = ['SVXY', 'UVXY', 'TVIX', 'VXX', 'SPY'], params = ['open', 'high', 'low', 'close', 'volume']):
    
    
    df = get_universe_dataframe(universe = ['SVXY', 'UVXY', 'TVIX', 'VXX', 'SPY'])
    symbols = universe
    temps = []
    for symbol in symbols:
        temp = df.reset_index()[df.reset_index().ticker == symbol]
        temp = temp.rename({
            'open': str(symbol) + 'open', 
            'high': str(symbol) + 'high',
            'low': str(symbol) + 'low',
            'close': str(symbol)+ 'close',
            'volume': str(symbol) + 'volume'}, axis=1)
        temps.append(temp)

    df = reduce(lambda left,right: pd.merge(left,right,on='datetime'), temps)

    df = df.dropna()

    for symbol in symbols:
        temp = df.reset_index()[df.reset_index().ticker == symbol]
        temp[str(symbol) + 'next_minute_return'] = (temp[str(symbol) + 'close'] - temp[str(symbol) + 'open']).shift(-1)
        temp[str(symbol) + 'next_minute_positive'] = temp[str(symbol) + 'next_minute_return'] > 0
        
    
    features = df.columns[df.columns.str.contains('|'.join(params))].values

    return (df, features)
    
def getLabelValues(df_final, prediction_symbol, feature_sy):

    # pass in all the features

    df_final[str(prediction_symbol) + 'next_minute_return'] = (df_final[str(prediction_symbol) + 'close'] - df_final[str(prediction_symbol) + 'open']).shift(-1)
    df_final[str(prediction_symbol) + 'next_minute_positive'] = df_final[str(prediction_symbol) + 'next_minute_return'] > 0

    return df_final.dropna()[str(prediction_symbol) + 'next_minute_positive']