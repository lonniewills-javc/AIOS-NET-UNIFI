# AIOS-NET-UNIFI Firestore Data Model

- **Document ID:** DOC-AIOS-NET-UNIFI-DATA-20260714-0001
- **Version:** 1.1
- **Status:** Active / Architecture Baseline
- **Project:** AIOS-NET-UNIFI
- **Owners:** Lonnie Wills / Jeff Harrison

## Governing Firestore placement

This project uses the shared governed AIOS Firestore database and follows the accepted domain-root architecture.

```text
domains/aiosNet/projects/AIOS-NET-UNIFI
```

It does not create a competing top-level database layout.

## Design principles

1. Stable inventory is separate from high-frequency observations.
2. Telemetry and events are immutable and idempotent.
3. Dashboards read aggregates for common views rather than scanning raw telemetry.
4. Findings retain evidence references so conclusions can be reproduced.
5. Client data is privacy-limited and pseudonymous by default.
6. Every record carries source, schema, collector, and ingestion metadata.
7. No secrets are stored in Firestore.

## Collection map

```text
domains/aiosNet/projects/AIOS-NET-UNIFI
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
└── identityMappings/{mappingId}   # restricted and optional
```

## Common metadata

```json
{
  "projectId": "AIOS-NET-UNIFI",
  "domain": "aiosNet",
  "controllerId": "controller-main",
  "siteId": "javc-main",
  "sourceSystem": "UNIFI_NETWORK",
  "sourceVersion": "discovered-at-runtime",
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

```text
controllerId, name, baseUrlFingerprint, controllerType,
networkApplicationVersion, apiMode, status, lastSeenAt,
capabilities[], siteIds[], schemaVersion
```

### sites/{siteId}

```text
siteId, controllerId, sourceSiteId, name, description,
timezone, status, lastInventorySyncAt, tags[]
```

### sites/{siteId}/devices/{deviceId}

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

Wi-Fi passwords, API keys, private keys, and controller credentials are prohibited.

## Telemetry objects

### sites/{siteId}/radioObservations/{observationId}

Recommended deterministic ID:

```text
{radioId}_{observedAtEpochMinute}
```

```text
observationId, apId, radioId, band, channel, channelWidthMhz,
transmitPowerDbm, clientCount, channelUtilizationPct,
wifiTxUtilizationPct, wifiRxUtilizationPct,
interferenceUtilizationPct, metricSemantics,
noiseFloorDbm, retryRatePct, txBytesDelta, rxBytesDelta,
txPacketsDelta, rxPacketsDelta, txErrorsDelta, rxErrorsDelta,
radarDetected, scanState, sampleIntervalSeconds,
qualityFlags[], rawPayloadRef|null
```

If UniFi exposes only "other airtime," `metricSemantics` must preserve that fact. The system may not relabel ambiguous source data as scientifically identified interference.

### sites/{siteId}/observations/{observationId}

```text
observationId, deviceId, apId|null, status, uptimeSeconds,
cpuUtilizationPct, memoryUtilizationPct, temperatureC,
uplinkStatus, uplinkSpeedMbps, txThroughputBps,
rxThroughputBps, clientCount, radioSummary, qualityFlags[]
```

### sites/{siteId}/clientSummaries/{summaryId}

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

## Findings and incidents

### sites/{siteId}/findings/{findingId}

```text
findingId, findingType, severity, status,
firstObservedAt, lastObservedAt, apId|null, radioId|null,
band|null, channel|null, confidence,
summary, technicalExplanation, recommendedAction,
evidenceRefs[], metricSummary, analysisRuleId,
analysisRuleVersion, createdAt, updatedAt
```

Initial finding types:

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
rootCause|null, remediation|null, validationEvidenceRefs[], history[]
```

## Aggregates

### hourlyAggregates/{aggregateId}

```text
{radioId}_{YYYY-MM-DDTHH}
```

Store sample count, missing-sample count, min, max, average, percentiles, and threshold-duration minutes.

### dailyAggregates/{aggregateId}

Store daily health summaries, peaks, recurrence windows, and trend indicators.

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

## Initial indexes

- Radio observations: `radioId + observedAt desc`.
- Findings: `status + severity + lastObservedAt desc`.
- Events: `eventType + occurredAt desc`.
- Incidents: `status + openedAt desc`.
- Collection runs: `status + startedAt desc`.
- Aggregates: `apId/radioId + bucketStart desc`.

Indexes must be driven by real application queries and reviewed for cost.

## Access roles

```text
collector: create inventory, telemetry, events, and collector state
analyzer: read telemetry/events and create or update findings
operator: read operational data and manage findings/incidents
viewer: read sanitized dashboard collections and reports
admin: manage policies, access, and restricted identity mappings
```

Browser clients never receive UniFi secrets or unrestricted identity mappings.
