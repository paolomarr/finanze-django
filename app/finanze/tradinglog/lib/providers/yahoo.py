import requests
from datetime import datetime, timedelta
import time
import logging

from tradinglog.lib import yf_secrets

APIDOJO_BASEURL = 'https://apidojo-yahoo-finance-v1.p.rapidapi.com'
GET_CHART_API = "/stock/v3/get-chart"
AUTO_COMPLETE_API = "/auto-complete"

ONE_MINUTE = "1m"
TWO_MINUTE = "2m"
FIVE_MINUTE = "5m"
FIFTEEN_MINUTE = "15m"
THIRTY_MINUTE = "30m"
SIXTY_MINUTE = "60m"
ONE_DAY = "1d"
ONE_WEEK = "1wk"
ONE_MONTH = "1mo"

EXCHANGE_CURRENCY = {
    "MIL": "EUR", "MI": "EUR",
    "PAR": "EUR", "PA": "EUR",
    "GER": "EUR", "FRA": "EUR", "DE": "EUR",
    "AMS": "EUR", "AS": "EUR",
    "MCE": "EUR", "MA": "EUR",
    "LON": "GBP", "L": "GBP",
    "NYQ": "USD", "NMS": "USD", "PCX": "USD", "NGM": "USD", "ASE": "USD",
    "TOR": "CAD", "TSX": "CAD",
    "TYO": "JPY",
    "SWX": "CHF", "VTX": "CHF",
}

EQUITY_QUOTE_TYPES = {"EQUITY", "ETF", "MUTUALFUND"}


def get_historical(symbol, from_timestamp, to_timestamp=0, interval=ONE_DAY, region="IT"):
    url = APIDOJO_BASEURL + GET_CHART_API
    if to_timestamp == 0:
        to_timestamp = int(time.time())

    querystring = {
        "interval": interval,
        "symbol": symbol,
        "period1": from_timestamp,
        "period2": to_timestamp,
        "region": region,
        "includePrePost": "false",
        "useYfid": "true",
        "includeAdjustedClose": "true",
        "events": ""
    }

    response = requests.request(
        "GET", url, headers=yf_secrets.APIDOJO_APIKEYS, params=querystring)

    if response.status_code != 200:
        logging.error("[YAHOOFINANCE] HTTP request failed: %d" % response.status_code)
        logging.debug("[YAHOOFINANCE] Original request: %s" % response.request.url)
        return {'error': "http: %d" % response.status_code}

    rj = response.json()
    result = rj['chart']['result']
    if not result:
        logging.warning("[YAHOOFINANCE] No data fetched from YF API for symbol %s" % symbol)
        return {'error': ["no data"]}

    meta = result[0]['meta']
    timestamps = result[0].get('timestamp') or []
    indicators = result[0]['indicators']
    if not timestamps:
        logging.warning("[YAHOOFINANCE] No timestamps for symbol %s" % symbol)
        return {'error': ["no data"]}

    lastts = None
    lastclose = None
    for index in reversed(range(len(timestamps))):
        if indicators['quote'][0]['close'][index] is not None:
            lastts = timestamps[index]
            lastclose = indicators['quote'][0]['close'][index]
            break

    if not lastts:
        logging.warning("[YAHOOFINANCE] No valid value")
        return {'error': ["no data"]}

    lastdate = datetime.fromtimestamp(lastts)
    lastclosedate = lastdate.replace(hour=17, minute=30, second=0)

    return {
        'regular_market_time': meta['regularMarketTime'],
        'regular_market_price': meta['regularMarketPrice'],
        'close_val': lastclose,
        'close_timestamp': lastclosedate.timestamp(),
    }


def get_latest_quote(symbol):
    fromtimestamp = datetime.today() - timedelta(15)
    return get_historical(symbol, from_timestamp=int(fromtimestamp.timestamp()))


def search(query, region="IT"):
    url = APIDOJO_BASEURL + AUTO_COMPLETE_API
    querystring = {"q": query, "region": region}

    response = requests.request(
        "GET", url, headers=yf_secrets.APIDOJO_APIKEYS, params=querystring)

    if response.status_code != 200:
        logging.error("[YAHOOFINANCE][search] HTTP %d for q=%s" % (response.status_code, query))
        return []

    rj = response.json()
    quotes = rj.get("quotes") or []
    results = []
    for q in quotes:
        if q.get("quoteType") not in EQUITY_QUOTE_TYPES:
            continue
        symbol = q.get("symbol")
        if not symbol:
            continue
        exchange = q.get("exchange") or q.get("exchDisp")
        results.append({
            "symbol": symbol,
            "name": q.get("longname") or q.get("shortname") or symbol,
            "currency": EXCHANGE_CURRENCY.get(exchange),
            "market": exchange or "UNKNOWN",
        })
    return results
