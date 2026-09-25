#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
KIBANA_URL="${KIBANA_URL:-http://localhost:5601}"
DASHBOARD_TITLE="Random Pass Service Health"

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    printf 'Missing prerequisite: %s\n' "$1" >&2
    exit 1
  }
}

require_command docker
require_command curl
require_command jq
docker compose version >/dev/null

cd "$ROOT_DIR"

printf 'Starting Elastic...\n'
./elastic-start-local/start.sh

printf 'Starting Random Pass demo services...\n'
docker compose --profile demo up -d --build

ELASTIC_PASSWORD="$(docker inspect es-local-dev --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '$1=="ELASTIC_PASSWORD" {print $2}')"
export ELASTIC_PASSWORD

slo_count="$(curl --fail --silent -u "elastic:$ELASTIC_PASSWORD" \
  "$KIBANA_URL/api/observability/slos?perPage=100&page=1" | jq '.results | length')"

if [[ "$slo_count" == "0" ]]; then
  generated_dashboard="$(mktemp "${TMPDIR:-/tmp}/random-pass-dashboard.XXXXXX.json")"
  trap 'rm -f "$generated_dashboard"' EXIT

  printf 'Creating SLOs and burn-rate alerts...\n'
  DASHBOARD_OUTPUT="$generated_dashboard" ./scripts/bootstrap-slos.sh

  dashboard_id="$(curl --fail --silent -u "elastic:$ELASTIC_PASSWORD" \
    -X POST "$KIBANA_URL/api/dashboards" \
    -H 'kbn-xsrf: true' \
    -H 'content-type: application/json' \
    --data-binary "@$generated_dashboard" | jq -r '.id')"
else
  dashboard_id="$(curl --fail --silent -u "elastic:$ELASTIC_PASSWORD" \
    "$KIBANA_URL/api/saved_objects/_find?type=dashboard&search=$(printf '%s' "$DASHBOARD_TITLE" | jq -sRr @uri)&search_fields=title" \
    | jq -r '.saved_objects[0].id // empty')"
fi

./scripts/bootstrap-ml.sh

printf '\nRandom Pass is ready.\n'
printf 'Frontend:  http://localhost:3000\n'
printf 'Gateway:   http://localhost:8080/health\n'
printf 'Kibana:    %s\n' "$KIBANA_URL"
printf 'Username:  elastic\n'
printf 'Password:  %s\n' "$ELASTIC_PASSWORD"
printf 'SLOs:      %s/app/slos\n' "$KIBANA_URL"
if [[ -n "$dashboard_id" ]]; then
  printf 'Dashboard: %s/app/dashboards#/view/%s\n' "$KIBANA_URL" "$dashboard_id"
fi
printf 'Flagd UI:  http://localhost:4000\n'