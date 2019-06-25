
from flask import Flask, render_template, request
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from models import DB, Ticker, Data
from get_data import add_ticker
from helpers import train_and_backtest

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    DB.init_app(app)

    @app.route('/')
    def root():
        symbols = Ticker.query.all()
        return render_template('base.html', symbols=symbols)

    @app.route('/symbol/<name>', methods=['POST'])
    @app.route('/symbol/<name>', methods=['GET'])
    def add_the_ticker(name=None):
        if request.method == 'POST':
            symbol = request.values['ticker_to_add']
            add_ticker(symbol)
            message = "Ticker added. "
            ticker_data = Ticker.query.get(symbol).datas
            return render_template('symbol.html', ticker_data=ticker_data, message=message)
        else:
            symbol = name
            ticker_data = Ticker.query.get(symbol).datas
            message = "Here's the ticker"
            return render_template('symbol.html', ticker_data=ticker_data, message=message)
      


    @app.route('/backtest', methods=['POST'])
    def backtest():

        prediction_symbol = request.values['predict_this_symbol']
        feature_symbols = [sym.ticker for sym in Ticker.query.all()]
        feature_symbols.remove(prediction_symbol)
        
        result = train_and_backtest(feature_symbols, prediction_symbol, num_backtests=50, test_size=.1, params = ['open', 'high', 'low', 'close', 'volume'])

        return render_template('backtest.html', accuracy=result['accuracy'])

    
    
    return app
