# UniFi diagnostic API client (phase 0)

No UI or controller changes. Python 3.10+, standard library only. Run from a trusted runtime with access to the controller, or use the official cloud connector if supported by the console and account.

## Configuration

Create a dedicated integration API key in UniFi Network > Integrations, using the least privilege available. Store it in Google Secret Manager or protected runtime configuration; never commit or paste it into chat. The runtime injects UNIFI_API_KEY. Set UNIFI_API_BASE to the HTTPS Network integration v1 base documented by your controller, typically https://<console>/proxy/network/integration/v1. For an approved remote cloud connector, use its documented HTTPS base instead. For a private CA, configure UNIFI_CA_FILE; TLS verification remains enabled.

## First live checks

    python diagnostics/unifi_diagnostics.py sites
    python diagnostics/unifi_diagnostics.py snapshot --site-id <site-id>

Output is JSON with timestamp, adopted device inventory, latest per-device allowlisted statistics and aggregate client count. Partial readings are flagged; missing metrics are not zero. Verify endpoint paths and field names against installed Network 10.4.7 documentation and sanitized live responses. No client identities are returned. Never publish live snapshots to this public repository.

## Remaining gates

- Unit tests and live API connectivity verification.
- Confirm API key permissions, supported metric fields, and coverage against UniFi dashboard.
- Deploy to authenticated private runtime; add a narrow authenticated ChatGPT-accessible read interface.
- Add scheduled Firestore collection under existing governed domain, retention, retry/backoff and historical analysis.
- UI deferred. No network mutation endpoints.
