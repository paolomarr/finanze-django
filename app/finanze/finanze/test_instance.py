from unittest import mock

from django.test import TestCase, override_settings

URL = "/api/instance/"


class InstanceInfoTest(TestCase):
    @override_settings(DEMO_MODE=False)
    @mock.patch.dict("os.environ", {}, clear=True)
    def test_regular_instance_without_keys(self):
        r = self.client.get(URL)  # no authentication needed
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"demo": False,
                                    "features": {"voice": False, "receipt_scan": False}})

    @mock.patch.dict("os.environ", {"OPENAI_API_KEY": "k", "OCR_SPACE_KEY": "k"}, clear=True)
    def test_features_follow_keys(self):
        self.assertEqual(self.client.get(URL).json()["features"],
                         {"voice": True, "receipt_scan": True})

    @override_settings(DEMO_MODE=True)
    @mock.patch.dict("os.environ", {"DEMO_USERNAME": "guest", "DEMO_PASSWORD": "pw"}, clear=True)
    def test_demo_exposes_credentials(self):
        body = self.client.get(URL).json()
        self.assertTrue(body["demo"])
        self.assertEqual(body["demo_credentials"], {"username": "guest", "password": "pw"})
