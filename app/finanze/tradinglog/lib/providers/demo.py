"""Offline market-data provider backed by the fictional demo market.

Selected with settings.FINANCE_PROVIDER = "demo" (see settings/demo.py).
Same interface and return shapes as the yahoo provider; no network access.
"""
from datetime import date, datetime, time as dtime, timedelta

from tradinglog.demo.market import EPOCH, Market, last_trading_day

ONE_DAY = "1d"
CLOSE_TIME = dtime(17, 30)

_market = None


def market() -> Market:
    global _market
    if _market is None:
        _market = Market()
    return _market


def close_datetime(d: date) -> datetime:
    return datetime.combine(d, CLOSE_TIME)


def get_historical(symbol, from_timestamp, to_timestamp=0, interval=ONE_DAY, region="IT"):
    m = market()
    if symbol not in m.stocks:
        return {'error': ["no data"]}
    now = datetime.now()
    to_dt = datetime.fromtimestamp(to_timestamp) if to_timestamp else now
    # today's close only counts once the (fictional) market has closed
    last = to_dt.date() if to_dt.time() >= CLOSE_TIME else to_dt.date() - timedelta(days=1)
    last = last_trading_day(last)
    if last < max(EPOCH, datetime.fromtimestamp(from_timestamp).date()):
        return {'error': ["no data"]}
    close_val = m.close(symbol, last)
    return {
        'regular_market_time': int(min(to_dt, now).timestamp()),
        'regular_market_price': close_val,
        'close_val': close_val,
        'close_timestamp': close_datetime(last).timestamp(),
    }


def get_latest_quote(symbol):
    fromtimestamp = datetime.today() - timedelta(15)
    return get_historical(symbol, from_timestamp=int(fromtimestamp.timestamp()))


def search(query, region="IT"):
    return [
        {"symbol": s.symbol, "name": s.name, "currency": s.currency, "market": s.market}
        for s in market().search(query)
    ]
