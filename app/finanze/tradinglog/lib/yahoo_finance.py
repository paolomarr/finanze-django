"""Deprecated shim. Use tradinglog.lib.finance_provider instead.

Kept temporarily so any lingering imports of the old names keep working.
Remove once all call sites have been migrated.
"""
from tradinglog.lib.providers.yahoo import (
    get_historical as getQuoteForSymbol,
    get_latest_quote as getLatestQuoteForSymbol,
)


def getLatestQuoteToDateForSymbol(symbol, todate):
    from datetime import timedelta
    fromtimestamp = todate - timedelta(15)
    return getQuoteForSymbol(symbol, from_timestamp=int(fromtimestamp.timestamp()))
