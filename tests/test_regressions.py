import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from iprad.core.abuseipdb_client import AbuseIPDBClient
from iprad.core.whois_client import WhoIsClient
from iprad.utils import cache


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cache_patch = patch.object(cache, "CACHE", self.root)
        self.cache_patch.start()
        self.addCleanup(self.cache_patch.stop)
        self.path = self.root / "ipinfo" / "1_1_1_1.json"
        self.path.parent.mkdir()

    def seed(self, age):
        self.path.write_text(json.dumps({
            "ip": "1.1.1.1", "org": "old",
            "created_at": (datetime.now() - timedelta(hours=age)).isoformat(),
        }))

    def test_fresh_cache_does_not_fetch(self):
        self.seed(1)
        with patch.object(cache, "fetch") as fetch:
            data, cached = cache.cache_processing("ipinfo", "1.1.1.1", "url")
        self.assertTrue(cached)
        self.assertEqual(data["org"], "old")
        fetch.assert_not_called()

    def test_expired_cache_fetches_and_persists_new_data(self):
        self.seed(49)
        with patch.object(cache, "fetch", return_value={"org": "new"}) as fetch:
            data, cached = cache.cache_processing("ipinfo", "1.1.1.1", "url")
        fetch.assert_called_once_with("url", "ipinfo", "1.1.1.1", retries=2, timeout=10)
        self.assertFalse(cached)
        self.assertEqual(data["org"], "new")
        self.assertEqual(json.loads(self.path.read_text())["org"], "new")

    def test_failed_refresh_does_not_return_expired_data(self):
        self.seed(49)
        with patch.object(cache, "fetch", return_value=None):
            result = cache.cache_processing("ipinfo", "1.1.1.1", "url")
        self.assertEqual(result, (None, None))
        self.assertFalse(self.path.exists())


class ClientTests(unittest.TestCase):
    def test_abuseipdb_uses_outer_timestamp_for_live_and_cached_reports(self):
        timestamp = datetime(2026, 1, 2, 3, 4)
        for cached in (False, True):
            with self.subTest(cached=cached):
                output = io.StringIO()
                response = {
                    "created_at": timestamp.isoformat() if cached else timestamp,
                    "data": {"abuseConfidenceScore": 0, "ipAddress": "1.1.1.1"},
                }
                with patch("iprad.core.abuseipdb_client.Console", return_value=Console(file=output)), \
                     patch("iprad.core.abuseipdb_client.cache_processing", return_value=(response, cached)):
                    client = AbuseIPDBClient()
                    client.API_KEY = "test-placeholder"
                    client.check_ip("1.1.1.1")
                self.assertIn("AbuseIPDB Report", output.getvalue())
                self.assertIn("02.01.2026 03:04", output.getvalue())

    def test_unresolved_whois_input_reports_error_without_fetching(self):
        output = io.StringIO()
        with patch("iprad.core.whois_client.get_resolved_ip", return_value=None), \
             patch("iprad.core.whois_client.cache_processing") as fetch, \
             patch("iprad.core.whois_client.Console", return_value=Console(file=output)):
            WhoIsClient().check_ip("nonexistent.invalid")
        fetch.assert_not_called()
        self.assertIn("Unable to resolve IP address", output.getvalue())
        self.assertIn("nonexistent.invalid", output.getvalue())


if __name__ == "__main__":
    unittest.main()
