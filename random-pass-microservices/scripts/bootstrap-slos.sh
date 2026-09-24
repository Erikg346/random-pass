#!/bin/sh
set -eu

: "${KIBANA_URL:=http://localhost:5601}"
: "${ELASTIC_USER:=elastic}"
: "${ELASTIC_PASSWORD:?Set ELASTIC_PASSWORD before running this script}"

jq -c '.[]' dashboards/random-pass-slos.json | while read -r slo; do
  name=$(printf '%s' "$slo" | jq -r '.name')
  curl -fsS -u "$ELASTIC_USER:$ELASTIC_PASSWORD" \
    -X POST "$KIBANA_URL/api/observability/slos" \
    -H 'kbn-xsrf: true' \
    -H 'content-type: application/json' \
    -d "$slo"
  printf 'Created SLO: %s\n' "$name"
done
