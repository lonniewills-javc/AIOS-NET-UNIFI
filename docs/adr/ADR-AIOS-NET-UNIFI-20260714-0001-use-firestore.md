# ADR-AIOS-NET-UNIFI-20260714-0001 — Use Google Cloud Firestore as the governed data store

- **Status:** Accepted
- **Date:** 2026-07-14
- **Project:** AIOS-NET-UNIFI
- **Owners:** Lonnie Wills / Jeff Harrison

## Context

The UniFi dashboard presents current and aggregated network information but does not preserve sufficient normalized history for independent analysis, correlation, root-cause investigation, or AIOS workflows. The project needs a durable store for controller inventory, radio observations, client association summaries, network events, analytical findings, incidents, collector state, and report metadata.

## Decision

AIOS-NET-UNIFI will use Google Cloud Firestore as the Phase 1 operational and historical data store.

Firestore will hold:

- Sites, controllers, devices, access points, radios, WLANs, and collection configuration.
- Time-bucketed radio, access-point, site, and client-summary observations.
- UniFi events and alarms retained for correlation.
- Derived findings, incidents, acknowledgements, and reports.
- Collector checkpoints, health, errors, and schema-version metadata.

All documents will include stable identifiers, UTC timestamps, source timestamps when available, schema version, collector version, and source-controller references.

## Rationale

- Firestore aligns with the broader AIOS Firebase architecture.
- It supports controlled server-side writes, indexed queries, scheduled collection, security rules, and future AIOS integration.
- It avoids placing high-frequency telemetry into Google Sheets.
- It provides a practical low-cost path for JAVC while preserving an export/migration path.

## Consequences

- Collection design must avoid unbounded documents and hot document paths.
- High-frequency observations will be immutable append-only documents grouped by time bucket.
- Aggregations will be precomputed for common dashboard and analytical queries.
- Indexes and retention controls must be explicitly managed.
- Firestore costs must be monitored as polling frequency and retained history grow.

## Alternatives considered

- **Google Sheets:** rejected for raw telemetry because of scale, indexing, concurrency, and analytical limitations.
- **SQLite:** useful for local prototypes but rejected as the governed shared store.
- **PostgreSQL/TimescaleDB:** technically strong, but adds infrastructure and operational overhead not required for Phase 1.
- **BigQuery:** retained as a future archival/large-scale analytical option.

## Guardrail

No UniFi credentials, API tokens, session cookies, private keys, or raw secrets may be stored in Firestore documents, GitHub, AIOS records, or application logs.
