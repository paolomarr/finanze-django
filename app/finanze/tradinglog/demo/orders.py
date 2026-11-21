"""
Demo order history generator: pure Python, no Django/ORM imports.

A small retail-investor story over the `months` months ending on `end`:
  - a monthly savings plan on the world-equity ETF (first trading day),
  - a quarterly top-up of the bond ETF,
  - a handful of discretionary buys of single stocks,
  - occasional partial sells of a position (never more than is owned).
Prices come from the demo Market, so orders match the stored quotes.
Output is fully determined by (market, end, months, seed).
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, timedelta

from tradinglog.demo.market import Market, last_trading_day, trading_days

BUY, SELL = "BUY", "SELL"
ACCOUNT = "Demo broker"
TRANSACTION_COST = 2.0

PLAN_ETF = "GLBX.DMO"
PLAN_AMOUNT = 300.0
BOND_ETF = "BOND.DMO"
BOND_AMOUNT = 1000.0


@dataclass(frozen=True)
class GeneratedOrder:
    date: date
    code: str
    account: str
    operation: str
    symbol: str
    quantity: int
    price: float
    transaction_cost: float


def _first_trading_day(y: int, m: int) -> date:
    d = date(y, m, 1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def months_back(end: date, months: int) -> date:
    y, m = end.year, end.month - months
    while m <= 0:
        y, m = y - 1, m + 12
    return date(y, m, 1)


def generate(market: Market, end: date, months: int = 24, seed: int = 42) -> list[GeneratedOrder]:
    rng = random.Random(seed)
    end = last_trading_day(end)
    start = months_back(end, months)
    singles = [s for s in market.stocks if s not in (PLAN_ETF, BOND_ETF)]
    orders: list[tuple[date, str, str, int]] = []

    def buy(d, symbol, amount):
        qty = max(1, int(amount // market.close(symbol, d)))
        orders.append((d, BUY, symbol, qty))

    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        first = _first_trading_day(y, m)
        if start <= first <= end:
            buy(first, PLAN_ETF, PLAN_AMOUNT)
            if m % 3 == 1:
                buy(first, BOND_ETF, BOND_AMOUNT)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)

    days = list(trading_days(start, end))
    # discretionary buys: roughly one every six weeks
    for d in sorted(rng.sample(days, k=max(4, len(days) // 30))):
        buy(d, rng.choice(singles), rng.choice([500, 750, 1000, 1500, 2000]))

    # sells: a few partial exits, decided on the running position
    held: dict[str, int] = {}
    result: list[tuple[date, str, str, int]] = []
    sell_days = set(rng.sample(days[len(days) // 3:], k=max(3, len(days) // 120)))
    pending = sorted(orders)
    for d in days:
        while pending and pending[0][0] == d:
            o = pending.pop(0)
            held[o[2]] = held.get(o[2], 0) + o[3]
            result.append(o)
        if d in sell_days:
            owned = [s for s in singles if held.get(s, 0) >= 2]
            if owned:
                symbol = rng.choice(owned)
                qty = max(1, int(held[symbol] * rng.choice([0.25, 0.5, 1.0])))
                held[symbol] -= qty
                result.append((d, SELL, symbol, qty))

    return [
        GeneratedOrder(
            date=d, code=f"DEMO-{i + 1:05d}", account=ACCOUNT, operation=op,
            symbol=symbol, quantity=qty, price=market.close(symbol, d),
            transaction_cost=TRANSACTION_COST,
        )
        for i, (d, op, symbol, qty) in enumerate(result)
    ]
