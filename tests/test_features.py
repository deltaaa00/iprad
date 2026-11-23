import io
import json
import socket
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import requests
from click.testing import CliRunner
from rich.console import Console

from iprad.cli import main
from iprad.utils.functions import get_resolved_ip
from iprad.utils.http import get_json
from iprad.core.ping_tracert_client import PingTracertClient
import test_regressions


class CacheControlTests(unittest.TestCase):
    setUp = test_regressions.CacheTests.setUp
    seed = test_regressions.CacheTests.seed

    def test_refresh_replaces_fresh_cache(self):
        self.seed(1)
        with patch('iprad.utils.cache.fetch', return_value={'org': 'new'}):
            from iprad.utils.cache import cache_processing
            data, cached = cache_processing('ipinfo', '1.1.1.1', 'url', refresh=True)
        self.assertFalse(cached)
        self.assertEqual(data['org'], 'new')
        self.assertEqual(json.loads(self.path.read_text())['org'], 'new')

    def test_custom_ttl_and_zero_ttl(self):
        from iprad.utils.cache import cache_processing
        for ttl in (0, 0.5):
            with self.subTest(ttl=ttl):
                self.seed(1)
                with patch('iprad.utils.cache.fetch', return_value={'org': 'new'}) as fetch:
                    _, cached = cache_processing('ipinfo', '1.1.1.1', 'url', cache_ttl=ttl)
                self.assertFalse(cached)
                fetch.assert_called_once()

    def test_ipv6_cache_filename_and_equivalent_addresses(self):
        from iprad.utils.cache import cache_processing
        ip = get_resolved_ip('2606:4700:4700:0:0:0:0:1111')
        with patch('iprad.utils.cache.fetch', return_value={'ip': ip}) as fetch:
            cache_processing('ipinfo', ip, 'url')
            data, cached = cache_processing('ipinfo', get_resolved_ip('2606:4700:4700::1111'), 'url')
        self.assertTrue(cached)
        self.assertEqual(data['ip'], '2606:4700:4700::1111')
        fetch.assert_called_once()
        self.assertTrue(all(':' not in p.name for p in self.root.rglob('*.json')))


class RetryTests(unittest.TestCase):
    def test_real_http_retry_success_exhaustion_and_nonretryable_status(self):
        class Handler(BaseHTTPRequestHandler):
            calls = 0
            statuses = []
            def do_GET(self):
                type(self).calls += 1
                self.send_response(type(self).statuses.pop(0))
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"ok": true}')
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f'http://127.0.0.1:{server.server_port}/'
            for statuses, retries, success in [([503, 200], 1, True), ([503, 503], 1, False),
                                                ([503], 0, False), ([401], 2, False)]:
                with self.subTest(statuses=statuses, retries=retries):
                    Handler.calls = 0
                    Handler.statuses = statuses.copy()
                    if success:
                        self.assertEqual(get_json(url, retries=retries, timeout=1), {'ok': True})
                    else:
                        with self.assertRaises(requests.RequestException):
                            get_json(url, retries=retries, timeout=1)
                    self.assertEqual(Handler.calls, len(statuses))
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_timeout_is_passed_to_requests(self):
        with patch('iprad.utils.http.requests.Session') as session:
            session.return_value.__enter__.return_value.get.side_effect = requests.Timeout
            with self.assertRaises(requests.Timeout):
                get_json('https://example.com', timeout=0.25)
            session.return_value.__enter__.return_value.get.assert_called_once_with(
                'https://example.com', timeout=0.25)


class IPv6AndCliTests(unittest.TestCase):
    def test_ipv6_literal_is_normalized_without_dns(self):
        with patch('socket.getaddrinfo') as dns:
            self.assertEqual(get_resolved_ip('2001:0db8:0:0:0:0:0:1'), '2001:db8::1')
        dns.assert_not_called()

    def test_ipv6_only_domain(self):
        with patch('socket.getaddrinfo', return_value=[
            (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('2001:db8::1', 0, 0, 0))]):
            self.assertEqual(get_resolved_ip('ipv6.example'), '2001:db8::1')

    def test_cli_forwards_options_to_all_lookup_clients(self):
        with patch('iprad.cli.IPinfoClient') as info, patch('iprad.cli.WhoIsClient') as whois, \
             patch('iprad.cli.AbuseIPDBClient') as abuse:
            result = CliRunner().invoke(main, ['check', '2001:db8::1', '--refresh',
                '--cache-ttl', '3', '--retries', '1', '--timeout', '2'])
        self.assertEqual(result.exit_code, 0, result.output)
        for client in (info, whois, abuse):
            client.return_value.check_ip.assert_called_once_with('2001:db8::1',
                refresh=True, cache_ttl=3.0, retries=1, timeout=2.0)

    def test_invalid_cli_options(self):
        for args in [('--retries', '-1'), ('--timeout', '0'), ('--cache-ttl', '-1')]:
            result = CliRunner().invoke(main, ['check', '1.1.1.1', *args])
            self.assertEqual(result.exit_code, 2)

    def test_ipv6_api_urls_and_abuseipdb_resolved_target(self):
        from iprad.core.ipinfo_client import IPinfoClient
        from iprad.core.whois_client import WhoIsClient
        from iprad.core.abuseipdb_client import AbuseIPDBClient
        for module, client, url in [
            ('ipinfo_client', IPinfoClient(), 'https://ipinfo.io/2001:db8::1/json'),
            ('whois_client', WhoIsClient(), 'https://rdap.org/ip/2001:db8::1'),
            ('abuseipdb_client', AbuseIPDBClient(), 'https://api.abuseipdb.com/api/v2/check'),
        ]:
            client.API_KEY = 'test-placeholder'
            with patch(f'iprad.core.{module}.cache_processing', return_value=(None, None)) as fetch:
                client.check_ip('2001:db8::1')
            self.assertEqual(fetch.call_args.args[1], '2001:db8::1')
            self.assertEqual(fetch.call_args.kwargs.get('url', fetch.call_args.args[-1]), url)

    def test_ipv6_target_is_forwarded_to_ping_and_traceroute(self):
        output = io.StringIO()
        with patch('iprad.core.ping_tracert_client.ping') as ping, \
             patch('iprad.core.ping_tracert_client.traceroute') as traceroute, \
             patch('iprad.core.ping_tracert_client.Console', return_value=Console(file=output)):
            ping.return_value.is_alive = False
            traceroute.return_value = []
            PingTracertClient().check_ip('::1')
        ping.assert_called_once_with('::1', count=3, timeout=1)
        traceroute.assert_called_once_with('::1', count=2, timeout=4, max_hops=20)
        self.assertIn('traceroute report', output.getvalue())
