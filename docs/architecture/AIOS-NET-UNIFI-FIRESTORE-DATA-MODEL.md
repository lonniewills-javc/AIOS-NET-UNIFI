# AIOS-NET-UNIFI Firestore Data Model

- **Document ID:** DOC-AIOS-NET-UNIFI-DATA-20260714-0001
- **Version:** 1.0
- **Status:** Active / Architecture Baseline
- **Project:** AIOS-NET-UNIFI
- **Owners:** Lonnie Wills / Jeff Harrison

## Design principles

1. Stable inventory is separate from high-frequency observations.
2. Telemetry and events are immutable and idempotent.
3. Common dashboards read aggregates, not large raw scans.
4. Findings retain evidence references so conclusions can be reproduced.
5. Client data is privacy-limited and pseudonymous by default.
6. Every document carries source, schema, and ingestion metadata.

## Root namespace

All project data is contained under:

```text
projects/AIOS-NET-UNIFI
```

The project document contains status, environment references, active schema version, retention policy version, and timestamps. No secret values are stored here.

## Collection map

```text
projects/AIOS-NET-UNIFI
├── controllers/{controllerId}
├── sites/{siteId}
│   ├── devices/{deviceId}
│   ├── accessPoints/{apId}
│   │   └── radios/{radioId}
│   ├── wlans/{wlanId}
│   ├── observations/{observationId}
│   ├── radioObservations/{observationId}
│   ├── clientSummaries/{summaryId}
│   ├── events/{eventId}
│   ├── findings/{findingId}
│   ├── incidents/{incidentId}
│   ├── hourlyAggregates/{aggregateId}
│   └── dailyAggregates/{aggregateId}
├── collectionPolicies/{policyId}
├── collectionRuns/{runId}
├── collectorHealth/{collectorId}
├── reports/{reportId}
└── identityMappings/{mappingId}   # restricted, optional
```

## Common metadata fields

Every stored record should include the applicable fields:

```json
{
  "projectId": "AIOS-NET-UNIFI",
  "controllerId": "controller-main",
  "siteId": "javc-main",
  "sourceSystem": "UNIFI_NETWORK",
  "sourceVersion": "unknown-until-discovered",
  "schemaVersion": 1,
  "collectorVersion": "0.1.0",
  "observedAt": "Timestamp",
  "sourceObservedAt": "Timestamp|null",
  "ingestedAt": "Timestamp",
  "createdAt": "Timestamp",
  "updatedAt": "Timestamp"
}
```

## Inventory objects

### controllers/{controllerId}

Purpose: records the controller/application identity and API capability profile.

Core fields:

```text
controllerId, name, baseUrlFingerprint, controllerType,
networkApplicationVersion, apiMode, status, lastSeenAt,
capabilities[], siteIds[], schemaVersion
```

`baseUrlFingerprint` is a non-secret normalized identifier. Do not store credentials or credential-bearing URLs.

### sites/{siteId}

```text
siteId, controllerId, sourceSiteId, name, description,
timezone, status, lastInventorySyncAt, tags[]
```

### sites/{siteId}/devices/{deviceId}

Supports gateways, switches, APs, and other adopted devices.

```text
deviceId, sourceDeviceId, macHash, name, model, deviceType,
firmwareVersion, ipAddressRestricted, status, adopted,
uplinkDeviceId, lastSeenAt, capabilities[]
```

### sites/{siteId}/accessPoints/{apId}

```text
apId, deviceId, name, model, locationLabel, firmwareVersion,
status, uplinkType, uplinkDeviceId, radioIds[], lastSeenAt
```

### sites/{siteId}/accessPoints/{apId}/radios/{radioId}

```text
radioId, apId, band, radioIndex, channel, channelWidthMhz,
transmitPowerDbm, transmitPowerMode, enabled, antennaGainDbi,
minimumRssi, lastConfigObservedAt
```

### sites/{siteId}/wlans/{wlanId}

```text
wlanId, name, enabled, bandPolicy, vlanId, securityMode,
broadcastingApGroupIds[], guestNetwork, configurationFingerprint
```

Do not store Wi-Fi passwords or private keys.

## Observation objects

### sites/{siteId}/radioObservations/{observationId}

Recommended deterministic ID:

```text
{radioId}_{observedAtEpochMinute}
```

Fields:

```text
observationId, apId, radioId, band, channel, channelWidthMhz,
transmitPowerDbm, clientCount, channelUtilizationPct,
wifiTxUtilizationPct, wifiRxUtilizationPct,
interferenceUtilizationPct, noiseFloorDbm,
retryRatePct, txBytesDelta, rxBytesDelta,
txPacketsDelta, rxPacketsDelta, txErrorsDelta, rxErrorsDelta,
radarDetected, scanState, sampleIntervalSeconds,
qualityFlags[], rawPayloadRef|null
```

`interferenceUtilizationPct` must preserve the source semantic. If UniFi exposes only an "other" airtime value, record the metric name and interpretation in `qualityFlags` or a `metricSemantics` field rather than overstating certainty.

### sites/{siteId}/observations/{observationId}

AP/site health snapshot:

```text
observationId, deviceId, apId|null, status, uptimeSeconds,
cpuUtilizationPct, memoryUtilizationPct, temperatureC,
uplinkStatus, uplinkSpeedMbps, txThroughputBps,
rxThroughputBps, clientCount, radioSummary, qualityFlags[]
```

### sites/{siteId}/clientSummaries/{summaryId}

Default is aggregate or pseudonymous, not personally identifying.

```text
summaryId, pseudonymousClientId|null, apId, radioId, band,
rssiDbm, signalQualityPct, txRateMbps, rxRateMbps,
retryRatePct, roamingCountDelta, disconnectCountDelta,
bytesTxDelta, bytesRxDelta, experienceScore|null,
identityResolutionAllowed=false
```

## Events and alarms

### sites/{siteId}/events/{eventId}

```text
eventId, sourceEventId, eventType, severity, category,
deviceId|null, apId|null, radioId|null, clientIdHash|null,
occurredAt, clearedAt|null, messageNormalized,
sourceCode, correlationKeys[], acknowledged=false
```

Examples include AP offline/online, uplink changes, DFS/radar events, high retries, repeated client disconnects, and collector-detected threshold crossings.

## Analysis objects

### sites/{siteId}/findings/{findingId}

```text
findingId, findingType, severity, status,
firstObservedAt, lastObservedAt, apId|null, radioId|null,
band|null, channel|null, confidence,
summary, technicalExplanation, recommendedAction,
evidenceRefs[], metricSummary, analysisRuleId,
analysisRuleVersion, createdAt, updatedAt
```

Finding types initially include:

```text
HIGH_INTERFERENCE
NON_WIFI_INTERFERENCE_SUSPECTED
CO_CHANNEL_CONTENTION
ADJACENT_CHANNEL_OVERLAP
EXCESSIVE_CHANNEL_WIDTH
HIGH_RETRY_RATE
WEAK_CLIENT_COVERAGE
STICKY_CLIENT_PATTERN
AP_CAPACITY_PRESSURE
UPLINK_CONSTRAINT
TEMPORAL_INTERFERENCE_PATTERN
COLLECTOR_DATA_GAP
```

### sites/{siteId}/incidents/{incidentId}

```text
incidentId, title, severity, status, openedAt, resolvedAt|null,
owner, findingIds[], affectedDeviceIds[], impactSummary,
rootCause|null, remediation|null, validationEvidenceRefs[],
history[]
```

## Aggregates

### hourlyAggregates/{aggregateId}

ID example:

```text
{radioId}_2026-07-14T18
```

Store count, min, max, average, percentile values, missing-sample count, and threshold-duration minutes for the key metrics.

### dailyAggregates/{aggregateId}

Store daily health summaries and peak windows for long-term trending.

## Collector operations

### collectionPolicies/{policyId}

```text
policyId, enabled, intervalSeconds, endpointGroups[],
rawRetentionDays, hourlyRetentionMonths, dailyRetentionMonths,
clientTelemetryMode, thresholds, activeFrom, activeTo|null
```

### collectionRuns/{runId}

```text
runId, collectorId, startedAt, completedAt, status,
requestedEndpointGroups[], documentsWritten, documentsSkipped,
errors[], controllerLatencyMs, nextCheckpoint
```

### collectorHealth/{collectorId}

```text
collectorId, status, version, environment, lastHeartbeatAt,
lastSuccessfulRunAt, consecutiveFailures, activeControllerIds[],
configurationFingerprint, deploymentRevision
```

## Index plan

Initial composite indexes should support:

- Radio observations by `radioId + observedAt desc`.
- Findings by `status + severity + lastObservedAt desc`.
- Events by `eventType + occurredAt desc`.
- Incidents by `status + openedAt desc`.
- Collection runs by `status + startedAt desc`.
- Aggregates by `apId/radioId + bucketStart desc`.

Index creation must be driven by real queries and reviewed for cost.

## Access roles

```text
collector: create inventory/telemetry/events and update collector state
analyzer: read telemetry/events and create/update findings
operator: read all operational data; update findings/incidents/acknowledgements
viewer: read sanitized dashboard collections and reports
admin: manage policies, roles, and restricted identity mappings
```

Client applications must never receive UniFi secrets or unrestricted identity mappings.
