"""
Fictional market for the demo instance: pure Python, no Django/ORM imports.

Each stock in stocks.yaml fluctuates over trading days (Mon-Fri) around an
exponential trend line start_price * exp(drift * years since EPOCH): the log
deviation from the trend is a mean-reverting random walk (Ornstein-Uhlenbeck),
so prices wiggle realistically but long-run returns follow `drift` in any
window, wherever "today" falls. The walk of a symbol is seeded by the symbol
alone, so the close of a given (symbol, day) never changes: prices computed
today, tomorrow or in another process all agree, and the series simply keeps
growing as time passes ("running" prices without storing any state).
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import yaml

SPEC_FILE = Path(__file__).resolve().parent / "stocks.yaml"
EPOCH = date(2020, 1, 1)
TRADING_DAYS_PER_YEAR = 252
# how strongly prices are pulled back to the trend (per year); with this value
# the typical deviation from trend is about volatility / 3
MEAN_REVERSION = 4.0


@dataclass(frozen=True)
class DemoStock:
    symbol: str
    name: str
    market: str
    currency: str
    start_price: float
    drift: float
    volatility: float


def load_stocks(spec_file: Path = SPEC_FILE) -> dict[str, DemoStock]:
    with open(spec_file) as f:
        spec = yaml.safe_load(f)
    return {
        s["symbol"]: DemoStock(
            symbol=s["symbol"], name=s["name"],
            market=s.get("market", spec["market"]),
            currency=s.get("currency", spec["currency"]),
            start_price=float(s["start_price"]),
            drift=float(s["drift"]), volatility=float(s["volatility"]),
        )
        for s in spec["stocks"]
    }


def is_trading_day(d: date) -> bool:
    return d.weekday() < 5


def last_trading_day(d: date) -> date:
    while not is_trading_day(d):
        d -= timedelta(days=1)
    return d


def trading_days(start: date, end: date):
    d = max(start, EPOCH)
    while d <= end:
        if is_trading_day(d):
            yield d
        d += timedelta(days=1)


class Market:
    """Lazily extends and caches each symbol's close series from EPOCH."""

    def __init__(self, stocks: dict[str, DemoStock] | None = None):
        self.stocks = stocks if stocks is not None else load_stocks()
        self._series: dict[str, tuple[random.Random, list[float]]] = {}
        self._epoch_index: dict[date, int] = {}

    def _index(self, d: date) -> int:
        """Number of trading days strictly between EPOCH and last_trading_day(d)."""
        d = last_trading_day(d)
        weeks, rest = divmod((d - EPOCH).days, 7)
        n = weeks * 5
        for i in range(rest):
            if is_trading_day(EPOCH + timedelta(days=i)):
                n += 1
        return n

    def close(self, symbol: str, d: date) -> float:
        """Close of `symbol` on the last trading day on or before `d`."""
        stock = self.stocks[symbol]
        if d < EPOCH:
            raise ValueError(f"no prices before {EPOCH}")
        # series holds the log deviation from trend, one value per trading day
        rng, series = self._series.setdefault(
            symbol, (random.Random(f"demo-market:{symbol}"), [0.0]))
        idx = self._index(d)
        dt = 1 / TRADING_DAYS_PER_YEAR
        while len(series) <= idx:
            series.append(series[-1] * (1 - MEAN_REVERSION * dt)
                          + stock.volatility * math.sqrt(dt) * rng.gauss(0, 1))
        trend = stock.start_price * math.exp(stock.drift * idx * dt)
        return round(trend * math.exp(series[idx]), 4)

    def search(self, query: str) -> list[DemoStock]:
        q = query.strip().lower()
        return [s for s in self.stocks.values()
                if q in s.symbol.lower() or q in s.name.lower()]
