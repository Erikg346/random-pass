#!/usr/bin/env bash
set -euo pipefail

: "${ELASTIC_URL:=http://localhost:9200}"
: "${ELASTIC_USER:=elastic}"
: "${ELASTIC_PASSWORD:?Set ELASTIC_PASSWORD before running this script}"

JOB_ID="random-pass-local-apm-transactions"
DATAFEED_ID="datafeed-${JOB_ID}"

request() {
  curl --fail --silent --show-error -u "$ELASTIC_USER:$ELASTIC_PASSWORD" "$@"
}

if ! request "$ELASTIC_URL/_ml/anomaly_detectors/$JOB_ID" >/dev/null 2>&1; then
  printf 'Creating ML job: %s\n' "$JOB_ID"
  request -X PUT "$ELASTIC_URL/_ml/anomaly_detectors/$JOB_ID" \
    -H 'content-type: application/json' \
    --data @- <<'JSON'
{
  "description": "Detects local APM transaction latency, throughput, and failure-rate anomalies.",
  "groups": ["apm", "random-pass"],
  "analysis_config": {
    "bucket_span": "15m",
    "summary_count_field_name": "doc_count",
    "detectors": [
      {
        "function": "high_mean",
        "field_name": "transaction_latency",
        "by_field_name": "transaction.type",
        "partition_field_name": "service.name",
        "detector_description": "high latency by transaction type for an APM service"
      },
      {
        "function": "mean",
        "field_name": "transaction_throughput",
        "by_field_name": "transaction.type",
        "partition_field_name": "service.name",
        "detector_description": "transaction throughput for an APM service"
      },
      {
        "function": "high_mean",
        "field_name": "failed_transaction_rate",
        "by_field_name": "transaction.type",
        "partition_field_name": "service.name",
        "detector_description": "failed transaction rate for an APM service"
      }
    ],
    "influencers": ["transaction.type", "service.name"],
    "model_prune_window": "30d"
  },
  "data_description": {
    "time_field": "@timestamp",
    "time_format": "epoch_ms"
  }
}
JSON

  request -X PUT "$ELASTIC_URL/_ml/datafeeds/$DATAFEED_ID" \
    -H 'content-type: application/json' \
    --data @- <<JSON
{
  "job_id": "$JOB_ID",
  "indices": ["metrics-apm*", "apm-*", "metrics-*.otel-*"],
  "query": {
    "bool": {
      "filter": [
        {"term": {"processor.event": "metric"}},
        {"term": {"metricset.name": "transaction"}},
        {"term": {"service.environment": "local"}}
      ]
    }
  },
  "aggregations": {
    "buckets": {
      "composite": {
        "size": 5000,
        "sources": [
          {"date": {"date_histogram": {"field": "@timestamp", "fixed_interval": "60s"}}},
          {"transaction.type": {"terms": {"field": "transaction.type"}}},
          {"service.name": {"terms": {"field": "service.name"}}}
        ]
      },
      "aggs": {
        "@timestamp": {"max": {"field": "@timestamp"}},
        "transaction_throughput": {"rate": {"unit": "minute"}},
        "transaction_latency": {"avg": {"field": "transaction.duration.histogram"}},
        "error_count": {
          "filter": {"term": {"event.outcome": "failure"}},
          "aggs": {"actual_error_count": {"value_count": {"field": "event.outcome"}}}
        },
        "success_count": {"filter": {"term": {"event.outcome": "success"}}},
        "failed_transaction_rate": {
          "bucket_script": {
            "buckets_path": {"failure_count": "error_count>_count", "success_count": "success_count>_count"},
            "script": "if ((params.failure_count + params.success_count)==0){return 0;}else{return 100 * (params.failure_count/(params.failure_count + params.success_count));}"
          }
        }
      }
    }
  }
}
JSON
fi

job_state="$(request "$ELASTIC_URL/_ml/anomaly_detectors/$JOB_ID/_stats" | jq -r '.jobs[0].state')"
if [[ "$job_state" != "opened" ]]; then
  request -X POST "$ELASTIC_URL/_ml/anomaly_detectors/$JOB_ID/_open" >/dev/null
fi

datafeed_state="$(request "$ELASTIC_URL/_ml/datafeeds/$DATAFEED_ID/_stats" | jq -r '.datafeeds[0].state')"
if [[ "$datafeed_state" != "started" ]]; then
  request -X POST "$ELASTIC_URL/_ml/datafeeds/$DATAFEED_ID/_start" \
    -H 'content-type: application/json' \
    --data '{}' >/dev/null
fi

printf 'ML job ready: %s (environment: local)\n' "$JOB_ID"
