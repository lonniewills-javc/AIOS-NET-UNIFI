# AIOS-NET-UNIFI System Architecture

- **Document ID:** DOC-AIOS-NET-UNIFI-ARCH-20260714-0001
- **Version:** 1.0
- **Status:** Active / Architecture Baseline
- **Project:** AIOS-NET-UNIFI
- **Parent project:** AIOS-NET
- **Owners:** Lonnie Wills / Jeff Harrison
- **Date:** 2026-07-14

## 1. Purpose

AIOS-NET-UNIFI provides independent, evidence-based monitoring and analysis of the JAVC UniFi network. It is intended to answer questions the native UniFi dashboard does not answer well, including:

- Which AP, radio, band, channel, or time window is driving interference?
- Is channel airtime consumed by valid Wi-Fi traffic, co-channel contention, adjacent-channel overlap, or likely non-Wi-Fi interference?
- Are weak signals, retries, roaming, uplink constraints, or configuration choices contributing to poor client experience?
- Are problems recurring at predictable times or locations?
- What evidence supports a recommended network change?

The system preserves historical telemetry so findings can be reproduced rather than relying on a changing dashboard snapshot.

## 2. North Star alignment

AIOS-NET-UNIFI is a governed AIOS infrastructure project, not a standalone dashboard experiment.

- **Projects organize the work.** `AIOS-NET-UNIFI` is a child of `AIOS-NET`.
- **Services execute the work.** UniFi access is isolated behind a controlled connector/service boundary.
- **Memory preserves the work.** Firestore retains observations, events, findings, incidents, reports, and evidence.
- **AI employees analyze and escalate.** Future AIOS services can read sanitized network health and create governed findings or incidents.
- **Sensitive actions remain approval-gated.** Version 1 is read-only and cannot modify the production network.

## 3. Scope

### In scope for Version 1

- Read-only authentication to the local UniFi Network application or supported official API.
- Controller, site, device, AP, radio, WLAN, client-summary, event, and alarm discovery.
- Scheduled telemetry collection.
- Firestore persistence using normalized schemas.
- Hourly and daily aggregation.
- Interference, contention, coverage, retry, uplink, and temporal-pattern analysis.
- Operator dashboard and reports.
- Findings, incidents, acknowledgements, and evidence history.
- Read-only AIOS service integration.

### Out of scope for Version 1

- Automatic changes to channels, channel width, transmit power, WLANs, VLANs, firewall rules, routing, firmware, adoption, or credentials.
- Packet capture or payload inspection.
- Employee or resident attendance tracking.
- Browsing-history, DNS-content, message-content, or application-content monitoring.
- Guaranteed identification of the exact physical source of non-Wi-Fi interference when the controller does not expose spectrum-identification data.

## 4. Architecture overview

```text
┌──────────────────────────────────────────────────────────────┐
│                    UniFi Network Controller                  │
│ Devices • Radios • Clients • Events • Alarms • Statistics    │
└──────────────────────────────┬───────────────────────────────┘
                               │ read-only HTTPS/API
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                     UniFi Connector Layer                    │
│ Auth • Version discovery • Endpoint adapters • Normalization │
│ Rate limiting • Retry • Redaction • Capability registry      │
└──────────────────────────────┬───────────────────────────────┘
                               │ normalized contracts
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                     Collection Orchestrator                  │
│ Scheduler • Inventory sync • Telemetry polls • Checkpoints    │
│ Idempotency • Collection runs • Health • Data-quality flags   │
└──────────────────────────────┬───────────────────────────────┘
                               │ server-side writes
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                   Google Cloud Firestore                     │
│ Inventory • Telemetry • Events • Aggregates • Findings        │
│ Incidents • Reports • Collector state • Policies              │
└───────────────┬───────────────────────┬──────────────────────┘
                │                       │
                ▼                       ▼
┌───────────────────────────┐  ┌───────────────────────────────┐
│ Analysis & Correlation    │  │ Aggregation & Retention       │
│ Rules • Trends • Evidence │  │ Hourly/daily rollups • TTL    │
│ Confidence • Findings     │  │ Cost controls • Export path   │
└───────────────┬───────────┘  └───────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│                   Presentation & AIOS Layer                  │
│ Network health dashboard • AP/radio history • Reports         │
│ Finding workflow • Incident workflow • AIOS read services     │
└──────────────────────────────────────────────────────────────┘
```

## 5. Component responsibilities

### 5.1 UniFi Connector Layer

The connector is the only component permitted to communicate directly with the UniFi controller.

Responsibilities:

- Authenticate using server-side secrets.
- Discover controller and Network application versions.
- Discover which official or local endpoints are available.
- Encapsulate version-specific response shapes.
- Normalize source records into internal contracts.
- Redact secrets and sensitive headers from logs.
- Enforce rate limits, timeouts, retries, and circuit-breaker behavior.
- Report capability gaps instead of fabricating unavailable metrics.

The connector must preserve metric semantics. For example, if the controller exposes "other airtime" rather than a scientifically identified interference percentage, the normalized record must retain that distinction.

### 5.2 Collection Orchestrator

Responsibilities:

- Execute scheduled collection policies.
- Separate inventory synchronization from high-frequency telemetry polling.
- Generate deterministic IDs for idempotent writes.
- Track collection runs and checkpoints.
- Detect missed samples, stale devices, and source failures.
- Apply data-quality flags when fields are unavailable, delayed, estimated, or semantically ambiguous.

Initial cadence:

```text
Controller/site/device inventory: every 15 minutes
AP/radio operational telemetry: every 5 minutes
Privacy-limited client summaries: every 5 minutes when enabled
Events/alarms: every 1–5 minutes or incremental checkpoint
Hourly aggregates: shortly after each hour
Daily aggregates: shortly after local midnight
```

Cadence is configuration and will be tuned after observing Firestore usage, API response time, and controller load.

### 5.3 Firestore Persistence Layer

Firestore is the governed Phase 1 data store.

Data categories:

- Stable controller/site/device/AP/radio/WLAN inventory.
- Immutable time-stamped observations.
- Immutable normalized events and alarms.
- Hourly and daily aggregates.
- Derived findings and evidence references.
- Operator incidents, acknowledgements, reports, and history.
- Collection policies, runs, checkpoints, and collector health.

Detailed objects are defined in `AIOS-NET-UNIFI-FIRESTORE-DATA-MODEL.md`.

### 5.4 Aggregation and Retention

Raw telemetry is valuable for root-cause analysis but expensive to keep indefinitely.

Initial retention:

```text
Raw radio/AP telemetry: 90 days
Hourly aggregates: 13 months
Daily aggregates: 36 months
Events/alarms: 13 months unless incident-linked
Findings/incidents/reports: operational history
Collector logs: 30 days
```

Aggregation must complete before source records expire. Retention values are policy records and must not be scattered as hard-coded application constants.

### 5.5 Analysis and Correlation Engine

The engine evaluates measurements over windows, not isolated samples.

Initial analyses:

- High channel/interference utilization duration.
- Valid Wi-Fi airtime versus unexplained/other airtime.
- Co-channel contention among JAVC APs.
- Adjacent-channel overlap and excessive channel width.
- High retry rate combined with RSSI and client count.
- Weak coverage and sticky-client patterns.
- AP capacity pressure.
- Uplink throughput or link-speed constraints.
- DFS/radar and channel-change correlation.
- Time-of-day recurrence.
- Data gaps and collector-health failures.

Each finding includes:

```text
finding type
severity
affected site/AP/radio/band/channel
first and last observed times
confidence score
technical summary
plain-language summary
recommended action
evidence references
analysis-rule version
```

The engine must use cautious language. It may classify a pattern as "non-Wi-Fi interference suspected" when evidence supports that inference, but it must not claim a microwave, camera, Bluetooth device, or other exact source without supporting spectrum evidence.

### 5.6 Dashboard and Reporting

The dashboard is an analytical view, not the source of truth.

Initial views:

1. **Facility health** — site status, active findings, worst APs/radios, and data freshness.
2. **AP/radio matrix** — band, channel, width, power, clients, utilization, interference/other airtime, retries, and noise.
3. **Historical charting** — metric trends by AP, radio, band, and time window.
4. **Channel plan** — current channel reuse and overlap across JAVC APs.
5. **Finding workbench** — evidence, confidence, recommendation, acknowledgement, and incident linkage.
6. **Collector health** — last successful collection, endpoint failures, latency, and missing data.
7. **Reports** — daily health brief, weekly trend report, and incident evidence package.

### 5.7 AIOS Service Integration

Version 1 exposes only read and documentation-oriented actions:

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

AIOS actions operate through controlled services and sanitized Firestore views. They do not receive UniFi credentials or direct controller access.

Future production mutations require a separate service, separate authority grant, explicit approval, rollback design, and accepted ADR.

## 6. Firestore object summary

```text
projects/AIOS-NET-UNIFI
├── controllers
├── sites
│   ├── devices
│   ├── accessPoints
│   │   └── radios
│   ├── wlans
│   ├── observations
│   ├── radioObservations
│   ├── clientSummaries
│   ├── events
│   ├── findings
│   ├── incidents
│   ├── hourlyAggregates
│   └── dailyAggregates
├── collectionPolicies
├── collectionRuns
├── collectorHealth
├── reports
└── identityMappings  # optional and restricted
```

## 7. Security architecture

### Authentication and secrets

- UniFi credentials/API tokens remain server-side.
- Secrets use an approved secret manager or protected runtime configuration.
- Secrets never enter GitHub, Firestore, AIOS sheets, browser bundles, URLs, reports, or logs.
- The connector uses the least-privileged read-only integration available.

### Firestore access roles

- **collector:** write inventory, telemetry, events, and collection state.
- **analyzer:** read observations/events and write findings.
- **operator:** read operational data and manage finding/incident workflow.
- **viewer:** read sanitized dashboard and report data.
- **admin:** manage policies, access, and restricted mappings.

Browser clients must not write raw telemetry or access restricted identity mappings.

### Privacy

- Client identifiers are pseudonymous by default.
- Raw MAC addresses and reversible identity mappings are restricted and avoided unless operationally necessary.
- No packet payloads or browsing content are collected.
- Wi-Fi telemetry may not be repurposed for resident or employee surveillance without explicit governance and privacy review.

## 8. Reliability and observability

The monitor must monitor itself.

Required operational signals:

- Last successful inventory and telemetry runs.
- Controller/API latency.
- Per-endpoint failure counts.
- Consecutive failures and circuit-breaker state.
- Documents written, skipped, and rejected.
- Missing sample windows.
- Schema-validation failures.
- Firestore write latency and quota/cost indicators.
- Collector version and deployment revision.

A failed collector must generate a data-gap finding so an apparently quiet network is not mistaken for a healthy network.

## 9. Deployment direction

The initial deployment should use Firebase/Google Cloud-aligned server-side components. The exact runtime may be Cloud Run, Cloud Functions, or another governed server process after controller reachability is confirmed.

The local UniFi controller may not be reachable directly from a public cloud runtime. Supported deployment patterns include:

1. **On-premises collector with outbound Firestore writes** — preferred when the controller is LAN-only.
2. **Secure private network connection to a cloud collector** — considered only with explicit security design.
3. **Hybrid collector** — local polling with cloud analysis/dashboard.

The collector runtime decision will be recorded after controller model, Network version, authentication method, and LAN reachability are inventoried.

## 10. Initial delivery phases

### Phase 0 — Environment inventory

- Confirm UniFi console/controller model.
- Confirm UniFi OS and Network application versions.
- Create least-privileged API integration.
- Validate accessible endpoints and returned metrics.
- Record metric semantics and capability gaps.

### Phase 1 — Foundation

- Initialize application/runtime.
- Configure secrets and environment separation.
- Create Firestore collections, security rules, and required indexes.
- Implement inventory and radio telemetry collection.
- Implement collection-run and collector-health records.

### Phase 2 — Historical analysis

- Add events/alarms and client summaries.
- Add hourly/daily aggregation and retention.
- Implement initial analysis rules.
- Validate findings against known UniFi dashboard readings.

### Phase 3 — Operator experience

- Build facility-health, AP/radio, historical, channel-plan, finding, and collector-health views.
- Add reports, acknowledgements, and incident workflow.

### Phase 4 — AIOS integration

- Add read-only AIOS service contracts.
- Add scheduled network-health brief and finding escalation.
- Preserve reports and incidents in project memory.

## 11. Acceptance criteria for the architecture baseline

The baseline is complete when:

- GitHub contains the governing architecture, data model, and accepted ADRs.
- AIOS contains matching project, ADR, documentation, and object records.
- Firestore is the declared data store.
- The collection model separates inventory, observations, events, findings, and operations.
- Version 1 is explicitly read-only.
- Privacy, retention, secrets, and approval boundaries are documented.
- The next implementation task is controller/API capability inventory rather than premature dashboard coding.

## 12. Related ADRs

- `ADR-AIOS-NET-UNIFI-20260714-0001` — Use Google Cloud Firestore.
- `ADR-AIOS-NET-UNIFI-20260714-0002` — Separate collection boundaries.
- `ADR-AIOS-NET-UNIFI-20260714-0003` — Keep initial UniFi integration read-only.
- `ADR-AIOS-NET-UNIFI-20260714-0004` — Govern retention, privacy, and secrets.
