# UniFi Environment Baseline

- **Document ID:** DOC-AIOS-NET-UNIFI-ENV-20260714-0001
- **Project:** AIOS-NET-UNIFI
- **Status:** Active / Environment Discovery
- **Recorded:** 2026-07-14
- **Owners:** Lonnie Wills / Jeff Harrison

## Confirmed environment

| Component | Value | Status |
|---|---|---|
| Console / controller | UniFi CloudKey Gen2 (`UCK-G2`, user-reported identifier `uckG2`) | Confirmed by operator |
| UniFi OS | `5.1.19` | Confirmed by operator |
| UniFi Network application | `10.4.7` | Confirmed by operator |
| Project repository | `lonniewills-javc/AIOS-NET-UNIFI` | Confirmed |
| Integration mode | Read-only | Governed by ADR |
| Firestore domain root | `domains/aiosNet/projects/AIOS-NET-UNIFI` | Governed architecture |

## Architectural implications

1. API discovery and testing must be performed against UniFi Network `10.4.7`; older undocumented response shapes must not be assumed.
2. The collector must record both UniFi OS and Network application versions with every capability profile.
3. The local CloudKey is expected to be LAN-resident, so the preferred deployment remains an on-premises collector that makes outbound writes to Firestore.
4. Authentication should use the least-privileged read-only integration exposed by **UniFi Network → Settings → Integrations** where available.
5. Before implementation, capture sanitized responses for site discovery, device inventory, latest statistics, connected clients, events/alarms, and any radio utilization fields.
6. Metric names must be preserved exactly until their meaning is validated. In particular, `interference`, `other airtime`, and total channel utilization must not be treated as interchangeable.

## Remaining environment inventory

- Exact CloudKey model variant and hardware identifier.
- Controller hostname or LAN address; store only in protected environment configuration.
- Site ID and site name.
- Authentication method and credential lifecycle.
- Official/local API base path exposed by Network `10.4.7`.
- AP inventory, models, firmware versions, radio bands, channels, widths, and power settings.
- Available fields for utilization, interference/other airtime, retries, noise floor, and neighboring radios.
- Controller reachability from the selected collector runtime.

## Security note

Do not commit controller addresses containing credentials, API keys, cookies, session tokens, passwords, or raw client identity mappings. Sanitized samples belong under `docs/api-samples/`; secrets belong only in the approved secret-management system.
