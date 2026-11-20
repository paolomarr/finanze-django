from datetime import timedelta
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from tradinglog.demo import seed as trading
from tradinglog.demo.market import Market
from tradinglog.models import Order, Stock, StockQuote


def run(*args):
    out = StringIO()
    call_command("seed_demo", *args, stdout=out)
    return out.getvalue()


class SeedTradingTest(TestCase):
    def test_creates_stocks_quotes_orders(self):
        run()
        user = User.objects.get(username="demo")
        self.assertEqual(Stock.objects.count(), len(Market().stocks))
        self.assertGreater(StockQuote.objects.count(), 8 * 450)
        orders = Order.objects.filter(user=user)
        self.assertGreater(orders.count(), 40)
        for s in Stock.objects.all():
            self.assertGreater(s.regular_market_price, 0)
        # portfolio value is computable and positive
        self.assertGreater(StockQuote.objects.CountervalueAtDate(timezone.now()), 0)

    def test_idempotent_and_reset(self):
        run()
        n_orders, n_quotes = Order.objects.count(), StockQuote.objects.count()
        self.assertIn("already has orders", run())
        self.assertEqual((n_orders, n_quotes), (Order.objects.count(), StockQuote.objects.count()))
        run("--reset")
        self.assertEqual(n_orders, Order.objects.count())

    def test_quotes_are_topped_up(self):
        market = Market()
        stocks = trading.ensure_stocks(market)
        now = timezone.now()
        start = (now - timedelta(days=60)).date()
        first = trading.update_quotes(market, stocks, start, now - timedelta(days=20))
        added = trading.update_quotes(market, stocks, start, now)
        self.assertGreater(first, 0)
        self.assertGreaterEqual(added, 8 * 12)  # ~14 trading days per stock
        self.assertEqual(trading.update_quotes(market, stocks, start, now), 0)


@override_settings(FINANCE_PROVIDER="demo")
class DemoProviderViewsTest(TestCase):
    def setUp(self):
        run()
        self.user = User.objects.get(username="demo")
        self.client.force_login(self.user)

    def test_search_endpoint(self):
        r = self.client.get("/api/tradinglog/stocks/search/", {"q": "solv"})
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(r.json()[0]["symbol"], "SOLV.DMO")

    def test_refresh_quotes_endpoint(self):
        ids = list(Stock.objects.values_list("id", flat=True))
        r = self.client.post("/api/tradinglog/quotes/", {"symbols": ids}, content_type="application/json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(len(r.json()["stocks"]), len(ids))
