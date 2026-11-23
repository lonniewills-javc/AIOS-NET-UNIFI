import unittest
from unittest.mock import patch
from unifi_diagnostics import UniFi, sanitize_stats

class DiagnosticTests(unittest.TestCase):
    def test_private_fields_excluded(self):
        self.assertEqual(sanitize_stats({"cpuUtilizationPct": 12, "macAddress": "private", "uplink": {"txRateBps": 100, "ipAddress": "private"}}),
                         {"cpuUtilizationPct": 12, "uplink": {"txRateBps": 100}})
    def test_tls_required(self):
        with self.assertRaises(ValueError):
            UniFi("http://example.com/integration/v1", "test")
    def test_pagination(self):
        client = UniFi("https://example.com/integration/v1", "test")
        with patch.object(client, "get", side_effect=[{"data":[{"id":"a"}],"totalCount":2},{"data":[{"id":"b"}],"totalCount":2}]):
            self.assertEqual(list(client.pages("/sites")), [{"id":"a"},{"id":"b"}])
    def test_snapshot(self):
        client = UniFi("https://example.com/integration/v1", "test")
        with patch.object(client,"pages",side_effect=[[{"id":"a","name":"AP","macAddress":"private"}],[{}]]), patch.object(client,"get",return_value={"uptimeSec":100}):
            result=client.snapshot("site")
        self.assertFalse(result["partial"])
        self.assertEqual(result["connectedClientCount"],1)
        self.assertEqual(result["devices"][0]["statistics"],{"uptimeSec":100})
        self.assertNotIn("macAddress",result["devices"][0])

if __name__ == "__main__":
    unittest.main()
