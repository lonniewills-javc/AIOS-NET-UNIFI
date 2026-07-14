# ADR-AIOS-NET-UNIFI-20260714-0004 — Govern retention, privacy, and secrets

- **Status:** Accepted
- **Date:** 2026-07-14
- **Project:** AIOS-NET-UNIFI
- **Owners:** Lonnie Wills / Jeff Harrison

## Context

Network telemetry can expose device identifiers, user behavior patterns, facility occupancy indicators, and operational details. High-frequency collection also creates continuing storage cost. The project must preserve enough evidence for root-cause analysis without collecting or retaining unnecessary personal information.

## Decision

### Secrets

- Store UniFi credentials and API tokens only in an approved server-side secret store or protected runtime configuration.
- Never store secrets in Firestore, GitHub, browser code, AIOS sheets, documentation, or logs.
- Redact authorization headers, cookies, tokens, and credential-bearing URLs from diagnostics.

### Privacy

- Store client-level telemetry only when required for troubleshooting.
- Prefer hashed or pseudonymous client identifiers over raw MAC addresses in analytical collections.
- Keep any reversible identity mapping in a restricted collection with separate access controls.
- Do not infer resident identity or attendance from Wi-Fi telemetry without a separately approved AIOS-NET privacy decision.
- Do not store packet payloads, DNS content, message content, browsing history, or application content.

### Initial retention policy

- Raw high-frequency radio/AP telemetry: 90 days.
- Hourly aggregates: 13 months.
- Daily aggregates: 36 months.
- Events and alarms: 13 months unless linked to an open incident.
- Findings, incidents, acknowledgements, and reports: retained as institutional operational history.
- Collector logs: 30 days, excluding security incident preservation.

Retention values are configuration, not hard-coded constants, and may be revised through an ADR after cost and operational review.

## Consequences

- Scheduled lifecycle cleanup is required.
- Aggregation must occur before raw telemetry expires.
- Security rules must separate collectors, analysts, operators, and general dashboard readers.
- Privacy-safe client summaries become the default dashboard data source.

## Guardrail

Network telemetry must not quietly evolve into employee or resident surveillance. Any presence, identity, movement, or attendance use case requires explicit purpose limitation, legal/privacy review, and a separate accepted ADR.
