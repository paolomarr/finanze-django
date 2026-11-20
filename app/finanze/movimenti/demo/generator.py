"""
Demo data generator: pure Python, no Django/ORM imports.

Turns the specs in categories.yaml / profiles.yaml into a list of
GeneratedMovement rows covering the `months` months that end on `end`.
Output is fully determined by (spec, end, months, seed).
"""
from __future__ import annotations

import calendar
import math
import random
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

SPEC_DIR = Path(__file__).resolve().parent
BALANCE_CATEGORY = "BALANCE"

# Fixed English names: calendar.month_name follows the process locale.
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]


@dataclass(frozen=True)
class GeneratedMovement:
    date: date
    description: str
    category: str
    subcategory: str | None
    abs_amount: float


@dataclass
class Spec:
    categories: list[dict]
    profiles: list[dict]
    balance: dict

    @property
    def directions(self) -> dict[str, float]:
        return {c["name"]: float(c["direction"]) for c in self.categories}


def load_spec(spec_dir: Path = SPEC_DIR) -> Spec:
    with open(spec_dir / "categories.yaml") as f:
        categories = yaml.safe_load(f)["categories"]
    with open(spec_dir / "profiles.yaml") as f:
        profiles = yaml.safe_load(f)
    return Spec(categories=categories, profiles=profiles["profiles"], balance=profiles["balance"])


# --------------------------------------------------------------------- helpers

def _add_months(d: date, n: int) -> date:
    m = d.month - 1 + n
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def _months_between(start: date, end: date):
    """Yield (year, month) for every month touching [start, end]."""
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def _poisson(rng: random.Random, lam: float) -> int:
    # Knuth; lam is small (< 10) here
    if lam <= 0:
        return 0
    limit, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


_PATTERN_TOKEN = re.compile(r"\[(A-Z|0-9)\](?:\{(\d+)\})?|(.)")


def _from_pattern(rng: random.Random, pattern: str) -> str:
    """Tiny regex subset: [A-Z]{n}, [0-9]{n}, literal characters."""
    out = []
    for cls, count, literal in _PATTERN_TOKEN.findall(pattern):
        if literal:
            out.append(literal)
        else:
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if cls == "A-Z" else "0123456789"
            out.extend(rng.choice(alphabet) for _ in range(int(count or 1)))
    return "".join(out)


def _pool_value(rng: random.Random, pool) -> str:
    if isinstance(pool, list):
        return str(rng.choice(pool))
    if "range" in pool:
        lo, hi = pool["range"]
        return str(rng.randint(lo, hi))
    if "pattern" in pool:
        return _from_pattern(rng, pool["pattern"])
    raise ValueError(f"Unknown pool definition: {pool!r}")


def render(rng: random.Random, template: str, pools: dict, d: date) -> str:
    builtins = {
        "month_name": MONTH_NAMES[d.month - 1],
        "year": str(d.year),
        "prev_year": str(d.year - 1),
        "quarter": str((d.month - 1) // 3 + 1),
    }
    values = {}
    for key in re.findall(r"\{(\w+)\}", template):
        if key in values:
            continue
        if key in builtins:
            values[key] = builtins[key]
        elif key in pools:
            values[key] = _pool_value(rng, pools[key])
        else:
            raise KeyError(f"Template {template!r} uses unknown placeholder {{{key}}}")
    return template.format(**values)


def _amount(rng: random.Random, spec: dict, d: date, start: date) -> float:
    if "fixed" in spec:
        f = spec["fixed"]
        years = (d - start).days // 365
        return round(f["value"] * (1 + f.get("drift_per_year", 0.0)) ** years, 2)
    if "lognormal" in spec:
        ln = spec["lognormal"]
        value = ln["median"] * math.exp(ln["sigma"] * rng.gauss(0, 1))
        return round(min(max(value, ln["min"]), ln["max"]), 2)
    raise ValueError(f"Unknown amount definition: {spec!r}")


def _occurrence_days(rng: random.Random, schedule: dict, year: int, month: int) -> list[int]:
    last = calendar.monthrange(year, month)[1]
    if "monthly" in schedule:
        s = schedule["monthly"]
        if "months" in s and month not in s["months"]:
            return []
        day = rng.randint(1, last) if s["day"] == "random" else min(int(s["day"]), last)
        jitter = int(s.get("jitter", 0))
        if jitter:
            day += rng.randint(-jitter, jitter)
        return [min(max(day, 1), last)]
    if "poisson" in schedule:
        s = schedule["poisson"]
        rate = s["per_month"] * s.get("boost", {}).get(month, 1)
    elif "seasonal" in schedule:
        s = schedule["seasonal"]
        rate = s["per_month"] if month in s["months"] else 0.0
    else:
        raise ValueError(f"Unknown schedule: {schedule!r}")
    return sorted(rng.randint(1, last) for _ in range(_poisson(rng, rate)))


# ------------------------------------------------------------------ generation

def generate(spec: Spec, end: date, months: int = 24, seed: int = 42) -> list[GeneratedMovement]:
    """
    Generate movements in (end - months, end], plus monthly BALANCE rows whose
    Checking value equals the simulated running balance (with noise).
    """
    rng = random.Random(seed)
    start = _add_months(end, -months)
    directions = spec.directions

    movements: list[GeneratedMovement] = []
    for profile in spec.profiles:
        for year, month in _months_between(start, end):
            for day in _occurrence_days(rng, profile["schedule"], year, month):
                d = date(year, month, day)
                if not (start < d <= end):
                    continue
                movements.append(GeneratedMovement(
                    date=d,
                    description=render(rng, rng.choice(profile["templates"]), profile.get("pools") or {}, d),
                    category=profile["category"],
                    subcategory=profile["subcategory"],
                    abs_amount=_amount(rng, profile["amount"], d, start),
                ))
    movements.sort(key=lambda m: (m.date, m.category, m.description))

    movements.extend(_balances(rng, spec, movements, directions, start, end))
    movements.sort(key=lambda m: (m.date, m.category, m.description))
    return movements


def _balances(rng, spec, movements, directions, start, end) -> list[GeneratedMovement]:
    bal = spec.balance
    pools = bal.get("pools") or {}
    noise = bal.get("noise", 0.0)
    accounts = bal["accounts"]
    values = {a["name"]: float(a["start"]) for a in accounts}

    out = []
    idx = 0  # movements consumed so far into Checking
    for year, month in _months_between(start, end):
        days = _occurrence_days(rng, bal["schedule"], year, month)
        for day in days:
            d = date(year, month, day)
            if not (start < d <= end):
                continue
            # Checking: running balance of all movements up to and including d
            while idx < len(movements) and movements[idx].date <= d:
                m = movements[idx]
                values["Checking"] += directions[m.category] * m.abs_amount
                idx += 1
            # Other accounts: monthly drift
            for a in accounts:
                drift = a.get("drift")
                if not drift:
                    continue
                if "monthly_mean" in drift:
                    values[a["name"]] += rng.gauss(drift["monthly_mean"], drift["monthly_sigma"])
                elif "monthly_return_mean" in drift:
                    values[a["name"]] *= 1 + rng.gauss(drift["monthly_return_mean"], drift["monthly_return_sigma"])
            for a in accounts:
                declared = values[a["name"]] * (1 + rng.uniform(-noise, noise))
                out.append(GeneratedMovement(
                    date=d,
                    description=render(rng, a["description"], pools, d),
                    category=BALANCE_CATEGORY,
                    subcategory=None,
                    abs_amount=round(declared, 2),
                ))
    return out


def simulated_checking(spec: Spec, movements: list[GeneratedMovement], up_to: date) -> float:
    """Exact (noise-free) Checking balance at `up_to`; used by tests and sanity checks."""
    directions = spec.directions
    start = next(float(a["start"]) for a in spec.balance["accounts"] if a["name"] == "Checking")
    return start + sum(directions[m.category] * m.abs_amount
                       for m in movements if m.category != BALANCE_CATEGORY and m.date <= up_to)
