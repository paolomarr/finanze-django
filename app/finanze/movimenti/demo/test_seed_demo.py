from io import StringIO
from unittest import mock

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from movimenti.models import Category, Movement


def run(*args):
    out = StringIO()
    call_command("seed_demo", *args, stdout=out)
    return out.getvalue()


class SeedDemoTest(TestCase):
    def test_creates_user_and_data(self):
        run()
        user = User.objects.get(username="demo")
        self.assertTrue(user.check_password("demo"))
        n = Movement.objects.filter(user=user).count()
        self.assertTrue(500 <= n <= 1000, n)
        balance = Category.objects.get(category="BALANCE")
        self.assertEqual(Category.objects.filter(category="BALANCE").count(), 1)
        self.assertTrue(balance.user.filter(pk=user.pk).exists())
        self.assertTrue(Movement.objects.filter(user=user, category=balance).exists())

    def test_idempotent(self):
        run()
        n = Movement.objects.count()
        self.assertIn("skipping", run())
        self.assertEqual(n, Movement.objects.count())

    def test_reset_regenerates(self):
        run()
        n = Movement.objects.count()
        run("--reset")
        self.assertEqual(n, Movement.objects.count())

    @mock.patch.dict("os.environ", {"DJANGO_SUPERUSER_USERNAME": "admin",
                                    "DJANGO_SUPERUSER_PASSWORD": "pw"})
    def test_superuser_from_env(self):
        run()
        self.assertTrue(User.objects.get(username="admin").is_superuser)

    def test_balance_to_date_works(self):
        run()
        from django.utils import timezone
        user = User.objects.get(username="demo")
        d, total = Movement.objects.balance_to_date(user, timezone.now())
        self.assertIsNotNone(d)
        self.assertGreater(total, 0)
