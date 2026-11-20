"""
Populate a demo instance: demo user, optional superuser, categories and
~2 years of generated movements (see movimenti/demo/).

Idempotent: if the demo user already has movements, nothing is generated
unless --reset is given.

Env vars (all optional):
  DEMO_USERNAME / DEMO_PASSWORD                     default: demo / demo
  DJANGO_SUPERUSER_USERNAME / _PASSWORD / _EMAIL    superuser created only if
                                                    USERNAME and PASSWORD are set
"""
import os
from datetime import datetime, time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from movimenti.demo.generator import BALANCE_CATEGORY, generate, load_spec
from movimenti.models import Category, Movement, Subcategory


class Command(BaseCommand):
    help = "Create the demo user and generate demo categories and movements."

    def add_arguments(self, parser):
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument("--months", type=int, default=24)
        parser.add_argument("--reset", action="store_true",
                            help="Delete the demo user's movements and regenerate them.")

    @transaction.atomic
    def handle(self, *args, seed, months, reset, **options):
        self._ensure_superuser()
        user = self._ensure_demo_user()

        existing = Movement.objects.filter(user=user)
        if existing.exists():
            if not reset:
                self.stdout.write(f"Demo user '{user.username}' already has data; skipping (use --reset).")
                return
            n, _ = existing.delete()
            self.stdout.write(f"Deleted {n} existing movements.")

        spec = load_spec()
        categories, subcategories = self._ensure_categories(spec, user)

        today = timezone.localdate()
        rows = generate(spec, end=today, months=months, seed=seed)
        tz = timezone.get_current_timezone()
        Movement.objects.bulk_create(
            Movement(
                user=user,
                date=timezone.make_aware(datetime.combine(r.date, time(12, 0)), tz),
                description=r.description,
                category=categories[r.category],
                subcategory=subcategories.get(r.subcategory),
                abs_amount=r.abs_amount,
            )
            for r in rows
        )
        self.stdout.write(self.style.SUCCESS(
            f"Created {len(rows)} movements for '{user.username}' "
            f"({rows[0].date} .. {rows[-1].date}, seed={seed})."))

    # ----------------------------------------------------------------- helpers

    def _ensure_demo_user(self) -> User:
        username = os.environ.get("DEMO_USERNAME", "demo")
        password = os.environ.get("DEMO_PASSWORD", "demo")
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f"Created demo user '{username}'.")
        return user

    def _ensure_superuser(self):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not (username and password):
            return
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username, os.environ.get("DJANGO_SUPERUSER_EMAIL", ""), password)
            self.stdout.write(f"Created superuser '{username}'.")

    def _ensure_categories(self, spec, user):
        categories, subcategories = {}, {}
        for c in spec.categories:
            if c["name"] == BALANCE_CATEGORY:
                # created by migration 0011; never create it here
                cat = Category.objects.get(category=BALANCE_CATEGORY)
            else:
                cat, _ = Category.objects.get_or_create(
                    category=c["name"], direction=float(c["direction"]))
            cat.user.add(user)
            categories[c["name"]] = cat
            for name in c["subcategories"]:
                # Subcategory.subcategory is not unique: reuse the first match
                sub = Subcategory.objects.filter(subcategory=name).first() \
                    or Subcategory.objects.create(subcategory=name)
                sub.user.add(user)
                subcategories[name] = sub
        return categories, subcategories
