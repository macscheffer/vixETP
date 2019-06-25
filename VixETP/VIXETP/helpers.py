
import pandas as pd
from models import DB, Ticker, Data
from functools import reduce
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

def make_dataframe(symbols):

    dfs = []

    for symbol in symbols:
        data_list = Ticker.query.get(symbol).datas

        df = pd.DataFrame(data_list[0].to_dict(), index=data_list[0].to_dict().keys())

        df = df.reset_index().drop(columns=['index']).append(data_list[1].to_dict(), ignore_index=True).drop_duplicates().reset_index().drop(columns=['index'])
        for i in range(len(data_list)-2):
            i = i + 2
            df = df.append(data_list[i].to_dict(), ignore_index=True)
            dfs.append(df)

    final_df = pd.concat(dfs).drop_duplicates()
    final_df = final_df.set_index(['datetime', 'ticker']).sort_index()
    return final_df


def makeFeaturesLabel(feature_symbols, prediction_symbol, params = ['open', 'high', 'low', 'close', 'volume']):

    symbols = [prediction_symbol] + feature_symbols
    df = make_dataframe(symbols)
    
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

    df_final = reduce(lambda left,right: pd.merge(left,right,on='datetime'), temps)

    features = df_final.columns[df_final.columns.str.contains('|'.join(params))].values
    df_final = df_final.dropna()
    df_final[str(prediction_symbol) + 'next_minute_return'] = (df_final[str(prediction_symbol) + 'close'] - df_final[str(prediction_symbol) + 'open']).shift(-1)
    df_final[str(prediction_symbol) + 'next_minute_positive'] = df_final[str(prediction_symbol) + 'next_minute_return'] > 0

    X = df_final.dropna()[features]
    y = df_final.dropna()[str(prediction_symbol) + 'next_minute_positive']

    return (X, y)

def train_and_backtest(feature_symbols, prediction_symbol, num_backtests=10, test_size=.1, params = ['open', 'high', 'low', 'close', 'volume']):

    X, y = makeFeaturesLabel(feature_symbols=feature_symbols, prediction_symbol=prediction_symbol, params=params)

    accuracy_scores = []
    for i in range(num_backtests):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
        std_scaler = StandardScaler().fit(X_train)
        X_train = std_scaler.transform(X_train)
        X_test = std_scaler.transform(X_test)
        lr = LogisticRegression()

        lr.fit(X_train, y_train)
        accuracy_scores.append(accuracy_score(y_test, lr.predict(X_test)))
    features = X.columns
    coefficients = lr.coef_

    return {
        'accuracy': pd.Series(accuracy_scores).mean(),
        'features': features,
        'coefficients': coefficients,
        'rows': len(y)
        }
    

def min_max_time(series):
    """
    Series of values where the time is a string.
    """
    return (min(pd.to_datetime(series)), max(pd.to_datetime(series)))

def find_first_comparable_time(df):
    """
    Takes in multilevel indexed df by date, ticker
    returns the first comparable date.
    """
    for date in df.index.levels[0].tolist():
        if len(df.loc[date]) == 5:
            return date


