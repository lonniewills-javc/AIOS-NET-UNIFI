"""Read-only cloud API connectivity probe; never emit identifiers or credentials."""
import json
import os
from urllib.request import Request, build_opener
from urllib.error import HTTPError
from unifi_diagnostics import NoRedirect

def probe():
    key = os.environ["UNIFI_API_KEY"]
    request = Request("https://api.ui.com/v1/hosts", headers={"X-API-Key": key, "Accept": "application/json"})
    with build_opener(NoRedirect()).open(request, timeout=20) as response:
        payload = json.load(response)
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise ValueError("Unexpected host response")
    return {"authenticated": True, "hostCount": len(rows), "scope": "cloud-host-discovery-only"}

if __name__ == "__main__":
    try:
        print(json.dumps(probe()))
    except HTTPError as exc:
        raise SystemExit("UniFi cloud HTTP " + str(exc.code)) from None
    except Exception:
        raise SystemExit("UniFi cloud probe failed") from None
