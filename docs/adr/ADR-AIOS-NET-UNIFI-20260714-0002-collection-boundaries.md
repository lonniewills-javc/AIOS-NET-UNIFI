# ADR-AIOS-NET-UNIFI-20260714-0002 — Separate inventory, telemetry, events, findings, and operations

- **Status:** Accepted
- **Date:** 2026-07-14
- **Project:** AIOS-NET-UNIFI
- **Owners:** Lonnie Wills / Jeff Harrison

## Context

UniFi data contains several different classes of information: relatively stable configuration and inventory, high-volume observations, controller events, derived analytical conclusions, and collector operational state. Combining these into one document model would create large documents, poor query behavior, excessive write contention, and unclear ownership.

## Decision

Firestore data will be separated into bounded collection families:

1. **Inventory and configuration** — controllers, sites, devices, access points, radios, WLANs, and collection policies.
2. **Telemetry observations** — immutable site, AP, radio, and privacy-limited client-summary observations.
3. **Events and alarms** — normalized UniFi events, alarms, DFS/radar events, disconnects, and collector-detected state changes.
4. **Analysis** — findings, evidence references, confidence, recommendations, and trend summaries.
5. **Operations** — incidents, acknowledgements, reports, collection runs, checkpoints, and collector health.

Stable inventory records may be updated in place. Telemetry and event records are append-only. Findings and incidents have explicit state-transition histories.

## Required identifiers

Every record must contain the relevant stable keys:

- `projectId`
- `controllerId`
- `siteId`
- `deviceId` or `apId` where applicable
- `radioId` where applicable
- `observedAt` and `ingestedAt`
- `schemaVersion`
- `sourceSystem`

## Consequences

- Dashboards query purpose-built collections rather than scanning raw source payloads.
- Analysis results can be reproduced through evidence references.
- Collector retries can remain idempotent through deterministic document IDs.
- Raw source fragments may be retained only when necessary and must be sanitized.

## Guardrail

Do not store an ever-growing telemetry array inside an AP, radio, site, or controller inventory document. Historical observations must remain separate immutable documents or bounded time-bucket subcollections.
