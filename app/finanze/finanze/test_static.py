import tempfile

from django.core.management import call_command
from django.test import TestCase, override_settings


class AdminStaticFilesTest(TestCase):
    """With DEBUG off (production, demo), WhiteNoise serves the collected admin assets."""

    def test_admin_css_served_without_debug(self):
        with tempfile.TemporaryDirectory() as root, \
                override_settings(DEBUG=False, STATIC_ROOT=root):
            call_command("collectstatic", "--noinput", "--ignore=*.scss", verbosity=0)
            # a new client builds a new handler, so WhiteNoise indexes `root`
            r = self.client_class().get("/static/admin/css/base.css")
            self.assertEqual(r.status_code, 200)
            self.assertIn("text/css", r["Content-Type"])
