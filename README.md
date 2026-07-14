# AIOS-NET-UNIFI

AIOS UniFi Network Observability is the governed facility-network monitoring project for JAVC. It collects UniFi telemetry through read-only APIs, stores normalized historical observations in Google Cloud Firestore, analyzes interference and network-health patterns, and exposes evidence-backed findings to operators and AIOS.

## Project identity

- **AIOS Project ID:** `AIOS-NET-UNIFI`
- **Parent project:** `AIOS-NET`
- **Repository:** `lonniewills-javc/AIOS-NET-UNIFI`
- **Code and Markdown source of truth:** GitHub
- **Governance and institutional-memory source of truth:** AIOS
- **Telemetry source system:** UniFi Network Controller
- **Historical analytical store:** Google Cloud Firestore

## Governing documents

- [System Architecture](docs/architecture/AIOS-NET-UNIFI-SYSTEM-ARCHITECTURE.md)
- [Firestore Data Model](docs/architecture/AIOS-NET-UNIFI-FIRESTORE-DATA-MODEL.md)
- [ADR 0001 — Use Firestore](docs/adr/ADR-AIOS-NET-UNIFI-20260714-0001-use-firestore.md)
- [ADR 0002 — Separate inventory, telemetry, and findings](docs/adr/ADR-AIOS-NET-UNIFI-20260714-0002-collection-boundaries.md)
- [ADR 0003 — Read-only UniFi integration](docs/adr/ADR-AIOS-NET-UNIFI-20260714-0003-read-only-unifi-integration.md)
- [ADR 0004 — Retention, privacy, and secrets](docs/adr/ADR-AIOS-NET-UNIFI-20260714-0004-retention-privacy-secrets.md)

## Initial release boundary

Version 1 is observational and diagnostic. It does not change UniFi channels, transmit power, firmware, WLAN configuration, firewall rules, or production devices. Any future mutation capability must be separately authorized and approval-gated through AIOS.
