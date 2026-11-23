"""Read-only UniFi Network diagnostic CLI; credentials stay server-side."""
import argparse
import json
import os
import re
import ssl
import sys
from datetime import datetime, timezone
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPSHandler, HTTPRedirectHandler
from urllib.error import HTTPError, URLError

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

class UniFi:
    def __init__(self, base, key, ca=None):
        parsed = urlsplit(base)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Configure an HTTPS API base without credentials or query parameters")
        if not base.rstrip("/").endswith("/integration/v1"):
            raise ValueError("API base must end in /integration/v1")
        self.base = base.rstrip("/")
        self.key = key
        self.opener = build_opener(HTTPSHandler(context=ssl.create_default_context(cafile=ca)), NoRedirect())

    def get(self, path, **params):
        req = Request(self.base + path + ("?" + urlencode(params) if params else ""),
                      headers={"X-API-Key": self.key, "Accept": "application/json"}, method="GET")
        with self.opener.open(req, timeout=15) as response:
            raw = response.read(4_000_001)
            if len(raw) > 4_000_000:
                raise ValueError("API response exceeds size limit")
            return json.loads(raw)

    def pages(self, path):
        offset = 0
        while offset < 10000:
            result = self.get(path, offset=offset, limit=100)
            rows = result["data"]
            if not isinstance(rows, list):
                raise ValueError("Unexpected pagination response")
            yield from rows
            offset += len(rows)
            if not rows or offset >= result.get("totalCount", offset if len(rows) < 100 else 10001):
                return
        raise ValueError("Pagination limit reached")

    def snapshot(self, site_id):
        site = "/sites/" + quote(site_id, safe="")
        devices = []
        for node in self.pages(site + "/devices"):
            item = {k: node[k] for k in ("id", "name", "model", "state", "firmwareVersion", "features") if k in node}
            try:
                stats = self.get(site + "/devices/" + quote(node["id"], safe="") + "/statistics/latest")
                item["statistics"] = sanitize_stats(stats)
            except HTTPError as exc:
                item["statisticsError"] = "HTTP " + str(exc.code)
            except (URLError, TimeoutError, ValueError):
                item["statisticsError"] = "Unavailable"
            devices.append(item)
        client_count = None
        try:
            client_count = sum(1 for _ in self.pages(site + "/clients"))
        except (HTTPError, URLError, TimeoutError, ValueError):
            pass
        return {"observedAt": datetime.now(timezone.utc).isoformat(), "siteId": site_id,
                "devices": devices, "connectedClientCount": client_count,
                "partial": client_count is None or any("statisticsError" in d for d in devices)}

# Explicit metric allowlist; never return client identity, IP, MAC, or raw responses.
METRICS = {"uptimeSec", "uptime", "cpuUtilizationPct", "memoryUtilizationPct",
           "loadAverage1Min", "loadAverage5Min", "loadAverage15Min", "lastHeartbeatAt",
           "nextHeartbeatAt", "txRateBps", "rxRateBps", "txBytes", "rxBytes",
           "channel", "channelWidth", "frequencyGHz", "frequency", "band", "noise",
           "channelUtilizationPct", "interferencePct", "retryPct", "clientCount",
           "connectedClientCount", "speedMbps", "txRetries", "signalStrengthDbm"}
CONTAINERS = {"uplink", "radios", "interfaces", "ports", "radioStatistics", "statistics", "data"}
def sanitize_stats(value):
    if isinstance(value, list):
        return [sanitize_stats(x) for x in value if isinstance(x, dict)]
    if not isinstance(value, dict):
        return {}
    out = {}
    for key, item in value.items():
        if key in METRICS and isinstance(item, (str, int, float, bool)):
            out[key] = item
        elif key in CONTAINERS and isinstance(item, (dict, list)):
            out[key] = sanitize_stats(item)
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["sites", "snapshot"])
    parser.add_argument("--site-id")
    args = parser.parse_args()
    try:
        client = UniFi(os.environ["UNIFI_API_BASE"], os.environ["UNIFI_API_KEY"], os.getenv("UNIFI_CA_FILE"))
        if args.operation == "sites":
            result = [{k: row[k] for k in ("id", "name") if k in row} for row in client.pages("/sites")]
        else:
            if not args.site_id or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", args.site_id):
                parser.error("snapshot requires a valid --site-id")
            result = client.snapshot(args.site_id)
        print(json.dumps(result, indent=2))
        return 0
    except HTTPError as exc:
        print("UniFi request failed: HTTP " + str(exc.code), file=sys.stderr)
    except (KeyError, ValueError, URLError, TimeoutError):
        print("UniFi request failed: check protected configuration, TLS, reachability and API compatibility", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(main())
