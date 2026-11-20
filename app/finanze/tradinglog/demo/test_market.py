from collections import defaultdict
from datetime import date, datetime, timedelta
from unittest import TestCase

from tradinglog.demo import orders as demo_orders
from tradinglog.demo.market import EPOCH, Market, last_trading_day, trading_days
from tradinglog.lib.providers import demo as provider

END = date(2026, 11, 18)


class MarketTest(TestCase):
    def setUp(self):
        self.market = Market()

    def test_symbols_are_fictional(self):
        self.assertGreaterEqual(len(self.market.stocks), 6)
        self.assertTrue(all(s.endswith(".DMO") for s in self.market.stocks))

    def test_price_stable_across_instances_and_query_order(self):
        a, b = Market(), Market()
        b.close("SOLV.DMO", END)  # extend the series far first
        for d in (date(2024, 3, 4), date(2025, 7, 1), END):
            self.assertEqual(a.close("SOLV.DMO", d), b.close("SOLV.DMO", d))

    def test_starts_at_start_price_and_stays_positive(self):
        s = self.market.stocks["NBLA.DMO"]
        self.assertEqual(self.market.close(s.symbol, EPOCH), s.start_price)
        self.assertTrue(all(self.market.close(s.symbol, d) > 0 for d in trading_days(EPOCH, END)))

    def test_weekend_uses_friday_close(self):
        sat = date(2026, 11, 14)
        self.assertEqual(last_trading_day(sat), date(2026, 11, 13))
        self.assertEqual(self.market.close("GLBX.DMO", sat), self.market.close("GLBX.DMO", date(2026, 11, 13)))

    def test_prices_move_day_to_day(self):
        days = list(trading_days(END - timedelta(days=30), END))
        self.assertGreater(len({self.market.close("CASA.DMO", d) for d in days}), len(days) // 2)

    def test_search(self):
        self.assertEqual([s.symbol for s in self.market.search("solv")], ["SOLV.DMO"])
        self.assertEqual(len(self.market.search("globex")), 2)
        self.assertEqual(self.market.search("zzz"), [])


class OrdersTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.market = Market()
        cls.rows = demo_orders.generate(cls.market, END, months=24, seed=42)

    def test_deterministic(self):
        self.assertEqual(self.rows, demo_orders.generate(Market(), END, months=24, seed=42))
        self.assertNotEqual(self.rows, demo_orders.generate(Market(), END, months=24, seed=7))

    def test_period_and_order(self):
        self.assertEqual([r.date for r in self.rows], sorted(r.date for r in self.rows))
        self.assertGreaterEqual(self.rows[0].date, date(2024, 11, 1))
        self.assertLessEqual(self.rows[-1].date, END)
        self.assertTrue(all(r.date.weekday() < 5 for r in self.rows))

    def test_monthly_plan(self):
        plan = [r for r in self.rows if r.symbol == demo_orders.PLAN_ETF]
        self.assertEqual(len({(r.date.year, r.date.month) for r in plan}), 25)

    def test_never_sells_more_than_owned(self):
        held = defaultdict(int)
        sells = 0
        for r in self.rows:
            held[r.symbol] += r.quantity if r.operation == demo_orders.BUY else -r.quantity
            self.assertGreaterEqual(held[r.symbol], 0, r)
            sells += r.operation == demo_orders.SELL
        self.assertGreaterEqual(sells, 3)

    def test_prices_match_market(self):
        for r in self.rows:
            self.assertEqual(r.price, self.market.close(r.symbol, r.date))
        self.assertEqual(len({r.code for r in self.rows}), len(self.rows))


class DemoProviderTest(TestCase):
    def test_search_shape(self):
        [res] = provider.search("nebula")
        self.assertEqual(res, {"symbol": "NBLA.DMO", "name": "Nebula Semiconductors",
                               "currency": "EUR", "market": "DEMO"})

    def test_latest_quote(self):
        q = provider.get_latest_quote("FERR.DMO")
        close_day = datetime.fromtimestamp(q["close_timestamp"]).date()
        self.assertLessEqual(close_day, date.today())
        self.assertGreaterEqual(close_day, date.today() - timedelta(days=4))
        self.assertEqual(q["close_val"], provider.market().close("FERR.DMO", close_day))
        self.assertEqual(q["regular_market_price"], q["close_val"])

    def test_historical_respects_to_timestamp(self):
        to = datetime(2025, 6, 10, 12, 0)  # Tuesday, before close
        q = provider.get_historical("FERR.DMO", int((to - timedelta(15)).timestamp()), int(to.timestamp()))
        self.assertEqual(datetime.fromtimestamp(q["close_timestamp"]).date(), date(2025, 6, 9))

    def test_unknown_symbol(self):
        self.assertIn("error", provider.get_latest_quote("ENI.MI"))
