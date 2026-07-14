# AIOS-NET-UNIFI System Architecture

- **Document ID:** DOC-AIOS-NET-UNIFI-ARCH-20260714-0001
- **Version:** 1.1
- **Status:** Active / Architecture Baseline
- **Project:** AIOS-NET-UNIFI
- **Parent project:** AIOS-NET
- **Owners:** Lonnie Wills / Jeff Harrison
- **Date:** 2026-07-14

## Purpose

AIOS-NET-UNIFI independently collects, preserves, analyzes, and reports JAVC UniFi network telemetry so the organization can identify which AP, radio, band, channel, configuration, client pattern, or time window is contributing to interference and poor network performance.

It is a governed AIOS infrastructure service, not merely a replacement dashboard.

## Source-of-truth boundaries

- **GitHub:** code, Markdown architecture, ADRs, security rules, indexes, and release history.
- **AIOS:** project governance, ADR registry, tasks, objects, documentation registry, and handoffs.
- **UniFi Network Controller:** authoritative source for current controller/device/network telemetry.
- **Google Cloud Firestore:** governed operational and historical analytical store.
- **Secret Manager/protected runtime configuration:** UniFi credentials and API tokens.

## Firestore placement

The project uses the existing governed AIOS Firestore database and domain-root pattern:

```text
domains/aiosNet/projects/AIOS-NET-UNIFI
```

It must not create a competing top-level Firestore architecture.

## Version 1 scope

### Included

- Read-only UniFi authentication and API capability discovery.
- Controller, site, gateway, switch, AP, radio, WLAN, client-summary, alarm, and event inventory.
- Five-minute AP/radio telemetry collection, subject to controller performance testing.
- Firestore persistence with normalized, versioned objects.
- Hourly and daily aggregation.
- Interference, channel-contention, overlap, retry, coverage, capacity, uplink, DFS/radar, and temporal-pattern analysis.
- Operator dashboard, findings, incidents, reports, acknowledgements, and collector-health views.
- Read-only AIOS service integration.

### Excluded

- Automatic network configuration changes.
- Packet payload inspection, browsing history, DNS-content monitoring, or message/application content collection.
- Employee or resident attendance or movement tracking.
- Claims that identify an exact physical interference source without supporting spectrum evidence.

## Logical architecture

```text
UniFi Controller
      │ read-only HTTPS/API
      ▼
UniFi Connector
  authentication • version/capability discovery • endpoint adapters
  normalization • rate limits • retries • redaction • circuit breaker
      │ normalized contracts
      ▼
Collection Orchestrator
  schedules • inventory sync • telemetry polling • checkpoints
  deterministic IDs • data-quality flags • collector health
      │ server-side writes
      ▼
Firestore: domains/aiosNet/projects/AIOS-NET-UNIFI
  inventory • telemetry • events • aggregates • findings
  incidents • reports • policies • collection runs • health
      │
      ├──────────────► Aggregation and retention
      │                hourly/daily rollups • lifecycle cleanup
      │
      └──────────────► Analysis and correlation
                       evidence windows • rules • confidence • findings
                              │
                              ▼
Dashboard and AIOS Services
  facility health • AP/radio matrix • history • channel plan
  findings • incidents • reports • AIOS read actions
```

## Component responsibilities

### UniFi Connector

The connector is the only component that communicates directly with the controller.

It must:

- Use server-side, least-privileged read-only credentials.
- Detect controller and Network application versions.
- Register available endpoints and unavailable capabilities.
- Normalize version-specific responses.
- Preserve metric semantics. "Other airtime" may not be silently relabeled as proven non-Wi-Fi interference.
- Redact credentials, tokens, cookies, and authorization headers.
- Enforce timeouts, retries, rate limits, and circuit-breaker behavior.

### Collection Orchestrator

Initial configurable cadence:

```text
Inventory: every 15 minutes
AP/radio telemetry: every 5 minutes
Client summaries: every 5 minutes when enabled
Events/alarms: every 1–5 minutes or by incremental checkpoint
Hourly aggregates: after each hour
Daily aggregates: after local midnight
```

The orchestrator records collection runs, checkpoints, missed samples, endpoint failures, documents written/skipped, controller latency, schema validation, and collector version.

### Firestore Persistence

Detailed objects are defined in `AIOS-NET-UNIFI-FIRESTORE-DATA-MODEL.md`.

Collection families are separated by purpose:

```text
controllers
sites / devices / accessPoints / radios / wlans
observations / radioObservations / clientSummaries
events
findings / incidents
hourlyAggregates / dailyAggregates
collectionPolicies / collectionRuns / collectorHealth
reports
restricted identityMappings, only if separately justified
```

Stable inventory may be updated in place. Telemetry and events are append-only and idempotent. Findings reference evidence records so conclusions can be reproduced.

### Analysis Engine

Initial rule families:

- High interference or unexplained airtime sustained over a window.
- Valid Wi-Fi airtime compared with other/unexplained airtime.
- Co-channel contention among JAVC APs.
- Adjacent-channel overlap and excessive channel widths.
- High retry rates correlated with RSSI, client count, and data rates.
- Weak coverage and sticky-client patterns.
- AP capacity pressure.
- Uplink constraints.
- DFS/radar and channel-change correlation.
- Time-of-day recurrence.
- Collector data gaps.

Every finding includes severity, confidence, affected scope, time range, plain-language and technical summaries, recommendation, evidence references, and analysis-rule version.

### Dashboard

Initial views:

1. Facility health and current findings.
2. AP/radio matrix with channel, width, power, clients, utilization, other/interference airtime, retries, and noise.
3. Historical charts by AP, radio, band, channel, and time.
4. Channel plan and overlap view.
5. Finding workbench with evidence and confidence.
6. Incident and acknowledgement workflow.
7. Collector health and data freshness.
8. Daily and weekly reports.

The dashboard is a presentation surface; Firestore remains the operational source of truth.

### AIOS Integration

Initial controlled actions:

```text
READ_NETWORK_HEALTH
READ_SITE_NETWORK_HEALTH
READ_AP_HEALTH
READ_RADIO_HISTORY
READ_ACTIVE_NETWORK_FINDINGS
READ_NETWORK_INCIDENT
GENERATE_NETWORK_HEALTH_REPORT
CREATE_NETWORK_INCIDENT
ACKNOWLEDGE_NETWORK_FINDING
```

AIOS reads sanitized service results. It does not receive controller credentials or direct controller access.

## Security and privacy

- Secrets exist only in an approved server-side secret store or protected runtime configuration.
- Browser clients cannot write raw telemetry.
- Client identifiers are pseudonymous by default.
- Raw MAC addresses and reversible mappings are restricted and avoided unless operationally necessary.
- No packet payloads or browsing content are collected.
- Network telemetry cannot be repurposed for employee or resident surveillance without a separate accepted ADR, purpose limitation, and privacy/legal review.

## Retention baseline

```text
Raw AP/radio telemetry: 90 days
Hourly aggregates: 13 months
Daily aggregates: 36 months
Events and alarms: 13 months unless linked to an open incident
Findings, incidents, acknowledgements, and reports: operational history
Collector logs: 30 days
```

Retention is controlled through policy records and lifecycle jobs, not hard-coded throughout the application.

## Deployment direction

The UniFi controller may only be reachable from the facility LAN. The preferred initial pattern is:

```text
On-premises collector → outbound encrypted Firestore writes
Cloud/Firebase analysis and dashboard → Firestore reads
```

Cloud Run, Cloud Functions, or another server runtime may host aggregation, analysis, reports, and dashboard APIs. The final collector runtime decision follows controller version, API authentication, and network reachability inventory.

## Delivery phases

### Phase 0 — Environment and API inventory

Confirm controller model, UniFi OS/Network versions, authentication method, accessible endpoints, metric semantics, and LAN reachability.

### Phase 1 — Firestore foundation and collector

Create security rules, indexes, collection policies, connector contracts, inventory sync, radio telemetry polling, collection-run records, and collector health.

### Phase 2 — Historical analysis

Add events, alarms, privacy-limited client summaries, aggregates, retention, and initial findings. Validate against current UniFi readings.

### Phase 3 — Operator dashboard

Build facility health, AP/radio matrix, history, channel plan, findings, incidents, collector health, and reports.

### Phase 4 — AIOS integration

Add controlled read services, network-health briefs, finding escalation, and project-memory preservation.

## Architecture decisions

- `ADR-AIOS-NET-UNIFI-20260714-0001` — Use Google Cloud Firestore.
- `ADR-AIOS-NET-UNIFI-20260714-0002` — Separate inventory, telemetry, events, findings, and operations.
- `ADR-AIOS-NET-UNIFI-20260714-0003` — Keep Version 1 read-only.
- `ADR-AIOS-NET-UNIFI-20260714-0004` — Govern retention, privacy, and secrets.

## Next implementation gate

Do not begin dashboard coding first. The next task is to inventory the actual UniFi environment and capture real API responses so field mappings and metric semantics are grounded in the installed controller version.
