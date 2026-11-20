import random
import re
from collections import Counter, defaultdict
from datetime import date
from unittest import TestCase

from movimenti.demo.generator import (
    BALANCE_CATEGORY, _from_pattern, generate, load_spec, simulated_checking,
)

END = date(2026, 11, 18)


class GeneratorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = load_spec()
        cls.rows = generate(cls.spec, END, months=24, seed=42)
        cls.movements = [r for r in cls.rows if r.category != BALANCE_CATEGORY]
        cls.balances = [r for r in cls.rows if r.category == BALANCE_CATEGORY]

    def test_deterministic(self):
        self.assertEqual(self.rows, generate(self.spec, END, months=24, seed=42))
        self.assertNotEqual(self.rows, generate(self.spec, END, months=24, seed=7))

    def test_date_range(self):
        self.assertTrue(all(date(2024, 11, 18) < r.date <= END for r in self.rows))

    def test_volume(self):
        self.assertTrue(500 <= len(self.rows) <= 1000, len(self.rows))

    def test_every_subcategory_used(self):
        expected = {s for c in self.spec.categories for s in c["subcategories"]}
        self.assertEqual(expected, {m.subcategory for m in self.movements})

    def test_no_unfilled_placeholders(self):
        self.assertFalse([r.description for r in self.rows if re.search(r"[{}]", r.description)])

    def test_amounts_positive(self):
        self.assertTrue(all(m.abs_amount > 0 for m in self.movements))

    def test_fixed_monthly_once_per_month(self):
        rent = Counter((m.date.year, m.date.month) for m in self.movements if m.subcategory == "Rent")
        self.assertTrue(all(n == 1 for n in rent.values()))
        self.assertGreaterEqual(len(rent), 23)

    def test_months_filter(self):
        ins = [m for m in self.movements if m.subcategory == "Car insurance"]
        self.assertTrue(all(m.date.month == 3 for m in ins))
        self.assertEqual(len(ins), 2)

    def test_balance_three_accounts_same_date_monthly(self):
        by_date = defaultdict(list)
        for b in self.balances:
            by_date[b.date].append(b.description)
        self.assertGreaterEqual(len(by_date), 23)
        for descs in by_date.values():
            self.assertEqual(len(descs), 3)
            self.assertEqual(sorted(d.split(" ")[0] for d in descs), ["Brokerage", "Checking", "Savings"])
        self.assertTrue(all(b.subcategory is None for b in self.balances))

    def test_checking_balance_coherent(self):
        noise = self.spec.balance["noise"]
        for b in self.balances:
            if b.description.startswith("Checking"):
                exact = simulated_checking(self.spec, self.rows, b.date)
                self.assertAlmostEqual(b.abs_amount, exact, delta=abs(exact) * noise + 0.01)

    def test_pattern(self):
        self.assertRegex(_from_pattern(random.Random(1), "EXP-[0-9]{5}"), r"^EXP-\d{5}$")
        self.assertRegex(_from_pattern(random.Random(1), "[A-Z]{6}"), r"^[A-Z]{6}$")
