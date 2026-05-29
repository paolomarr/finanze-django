"""Provider-agnostic facade for market data.

Today this dispatches to the Yahoo Finance provider; in the future selection
can be driven by a setting (e.g. settings.FINANCE_PROVIDER). The three
functions below define the interface every provider module must expose.
"""
from django.conf import settings

from tradinglog.lib.providers import yahoo

_PROVIDERS = {
    "yahoo": yahoo,
}


def _provider():
    name = getattr(settings, "FINANCE_PROVIDER", "yahoo")
    return _PROVIDERS.get(name, yahoo)


def search(query, region="IT"):
    return _provider().search(query, region=region)


def get_latest_quote(symbol):
    return _provider().get_latest_quote(symbol)


def get_historical(symbol, from_timestamp, to_timestamp=0, interval=yahoo.ONE_DAY, region="IT"):
    return _provider().get_historical(
        symbol, from_timestamp, to_timestamp=to_timestamp,
        interval=interval, region=region)
