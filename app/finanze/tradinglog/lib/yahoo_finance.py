import requests
from . import yf_secrets
from os.path import join as pjoin
from datetime import datetime, timedelta
import time
import logging

APIDOJO_BASEURL = 'https://apidojo-yahoo-finance-v1.p.rapidapi.com'
GET_CHART_API = "/stock/v3/get-chart"

ONE_MINUTE = "1m"
TWO_MINUTE = "2m"
FIVE_MINUTE = "5m"
FIFTEEN_MINUTE = "15m"
THIRTY_MINUTE = "30m"
SIXTY_MINUTE = "60m"
ONE_DAY = "1d"
ONE_WEEK = "1wk"
ONE_MONTH = "1mo"


def getQuoteForSymbol(symbol, fromTimestamp, toTimestamp=0, interval=ONE_DAY, region="IT"):

    url = APIDOJO_BASEURL + GET_CHART_API

    if toTimestamp is 0:
        toTimestamp = int(time.time())

    querystring = {
        "interval": interval,
        "symbol": symbol,
        "period1": fromTimestamp,
        "period2": toTimestamp,
        "region": region,
        "includePrePost": "false",
        "useYfid": "true",
        "includeAdjustedClose": "true",
        "events": ""
    }

    headers = yf_secrets.APIDOJO_APIKEYS

    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=querystring)

    myresponse = {}
    if response.status_code == 200:
        rj = response.json()
        result = rj['chart']['result']
        if not len(result) > 0:
            logging.warning("[YAHOOFINANCE] No data fetched from \
YF API for symbol {}".format(symbol))
            return {'error': ["no data"]}

        meta = result[0]['meta']
        timestamps = result[0]['timestamp']
        indicators = result[0]['indicators']
        if not len(timestamps) > 0:
            logging.warning("[YAHOOFINANCE] No data fetched from \
YF API for symbol {}".format(symbol))
            return {'error': ["no data"]}

        lastts = None
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

        myresponse['regular_market_time'] = meta['regularMarketTime']
        myresponse['regular_market_price'] = meta['regularMarketPrice']
        myresponse['close_val'] = lastclose
        myresponse['close_timestamp'] = lastclosedate.timestamp()
    else:
        logging.error("[YAHOOFINANCE] HTTP request failed: {}\
".format(response.status_code))
        logging.debug("[YAHOOFINANCE] Original request: {}\
".format(response.request.url))
        return {'error': "http: %d" % response.status_code}

    return myresponse


def getLatestQuoteToDateForSymbol(symbol, todate):
    fromtimestamp = todate - timedelta(15)
    return getQuoteForSymbol(
        symbol,
        fromTimestamp=int(fromtimestamp.timestamp()))


def getLatestQuoteForSymbol(symbol):
    return getLatestQuoteToDateForSymbol(symbol, datetime.today())
