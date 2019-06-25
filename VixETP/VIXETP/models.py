
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


DB = SQLAlchemy()

class Ticker(DB.Model):

    ticker = DB.Column(DB.String(25), primary_key=True)

    def __repr__(self):
        return '[Ticker Object: {}]'.format(self.ticker)

class Data(DB.Model):

    id = DB.Column(DB.Integer, primary_key=True)
    ticker = DB.Column(DB.String(25), DB.ForeignKey(Ticker.ticker), nullable=False)
    datetime = DB.Column(DB.String(50))
    open_ = DB.Column(DB.Integer)
    high = DB.Column(DB.Integer)
    low = DB.Column(DB.Integer)
    close = DB.Column(DB.Integer)
    volume = DB.Column(DB.Integer)
    data = DB.relationship('Ticker', backref=DB.backref('datas', lazy=True))

    def __repr__(self):
        return '[Ticker Object: {}]'.format(self.ticker)

    def to_dict(self):
        return ({'ticker': self.ticker,
                'datetime': self.datetime,
                'open': self.open_,
                'high': self.high,
                'low': self.low,
                'close': self.close,
                'volume': self.volume})
