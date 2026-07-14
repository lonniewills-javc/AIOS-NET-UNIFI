# ADR-AIOS-NET-UNIFI-20260714-0003 — Keep the initial UniFi integration read-only

- **Status:** Accepted
- **Date:** 2026-07-14
- **Project:** AIOS-NET-UNIFI
- **Owners:** Lonnie Wills / Jeff Harrison

## Context

The immediate business need is to understand interference, channel utilization, radio health, client experience, and recurring facility network problems. Network configuration changes are sensitive production actions that can interrupt resident, employee, security, and operational connectivity.

## Decision

Version 1 of AIOS-NET-UNIFI will use read-only UniFi API access and will not mutate controller or device configuration.

The connector may read:

- Controller, site, device, AP, radio, WLAN, client, alarm, and event data.
- Current and historical statistics exposed by the installed UniFi Network version.
- RF scan or neighboring-radio results when the controller exposes them through an authorized endpoint.

The connector may not change:

- Channels or channel widths.
- Transmit power.
- WLAN, VLAN, firewall, routing, or security settings.
- Firmware or device adoption state.
- User accounts, credentials, or API integrations.

## AIOS authority boundary

Read and analytical functions are authority levels 0–3. Any future network mutation is a level-5 sensitive action requiring a separate accepted ADR, explicit user approval, audit logging, rollback planning, and production safeguards.

## Consequences

- The first release can be deployed with materially lower operational risk.
- Findings will recommend changes but will not automatically apply them.
- Root-cause analysis remains evidence-based rather than being mixed with remediation automation.
- A future controlled remediation service may be added without changing the collector and analytical contracts.

## Guardrail

The application service account or API integration must have the minimum permissions required for collection. Administrator credentials must not be embedded in the application.
