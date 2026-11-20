"""ORM side of the trading demo data, used by the seed_demo command."""
from datetime import date, datetime, timedelta

from django.db.models import Max
from django.utils import timezone

from tradinglog.demo import orders as demo_orders
from tradinglog.demo.market import Market, trading_days
from tradinglog.lib.providers.demo import CLOSE_TIME
from tradinglog.models import Currency, Market as MarketModel, Order, OrderOperation, Stock, StockQuote

# stored quotes start a little before the first order, so charts have a lead-in
QUOTES_LEAD_DAYS = 30


def _aware_close(d: date) -> datetime:
    return timezone.make_aware(datetime.combine(d, CLOSE_TIME))


def last_closed_day(now: datetime) -> date:
    """Last day whose close is already known at `now` (aware)."""
    local = timezone.localtime(now)
    return local.date() if local.time() >= CLOSE_TIME else local.date() - timedelta(days=1)


def ensure_stocks(market: Market) -> dict[str, Stock]:
    for op in (demo_orders.BUY, demo_orders.SELL):
        OrderOperation.objects.get_or_create(operation=op)
    stocks = {}
    now = timezone.now()
    for s in market.stocks.values():
        currency, _ = Currency.objects.get_or_create(symbol=s.currency)
        mkt, _ = MarketModel.objects.get_or_create(name=s.market)
        stocks[s.symbol], _ = Stock.objects.get_or_create(
            symbol=s.symbol,
            defaults={"name": s.name, "currency": currency, "market": mkt,
                      "regular_market_time": now, "last_price_update": now})
    return stocks


def update_quotes(market: Market, stocks: dict[str, Stock], start: date, now: datetime) -> int:
    """Insert missing daily closes up to the last closed day; refresh current prices.

    Idempotent: only days after a stock's latest stored quote are added, so
    restarting the demo container later fills the gap up to today.
    """
    end = last_closed_day(now)
    created = 0
    for symbol, stock in stocks.items():
        latest = StockQuote.objects.filter(stock=stock).aggregate(m=Max("close_timestamp"))["m"]
        first = timezone.localtime(latest).date() + timedelta(days=1) if latest else start
        new = [StockQuote(stock=stock, close_val=market.close(symbol, d), close_timestamp=_aware_close(d))
               for d in trading_days(first, end)]
        StockQuote.objects.bulk_create(new)
        created += len(new)
        stock.regular_market_price = market.close(symbol, end)
        stock.regular_market_time = now
        stock.last_price_update = now
        stock.save()
    return created


def create_orders(market: Market, stocks: dict[str, Stock], user, end: date, months: int, seed: int):
    ops = {o.operation: o for o in OrderOperation.objects.all()}
    rows = demo_orders.generate(market, end=end, months=months, seed=seed)
    Order.objects.bulk_create(
        Order(user=user, date=r.date, code=r.code, account=r.account,
              operation=ops[r.operation], stock=stocks[r.symbol], quantity=r.quantity,
              price=r.price, transaction_cost=r.transaction_cost)
        for r in rows)
    return rows


def quotes_start(end: date, months: int) -> date:
    return demo_orders.months_back(end, months) - timedelta(days=QUOTES_LEAD_DAYS)
