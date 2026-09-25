# Random Pass Demo Bootstrap

Use these steps to start the complete microservices demo with live Elastic
Observability, SLOs, and the Service Health dashboard.

## Fresh Elastic Install

Run all commands from this directory.

```sh
# Start the repository's Elastic stack. It enables the Elastic APM connector.
./elastic-start-local/start.sh

# Start all microservices and continuous demo traffic.
docker compose --profile demo up -d --build

# Read the password from the local stack without placing it in shell history.
export ELASTIC_PASSWORD="$(docker inspect es-local-dev --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '$1=="ELASTIC_PASSWORD" {print $2}')"

# Create the three SLOs, their enabled burn-rate alerts, and update dashboard panel IDs.
./scripts/bootstrap-slos.sh

# Import the Service Health dashboard and print its Kibana URL.
DASHBOARD_ID="$(curl --fail --silent -u "elastic:$ELASTIC_PASSWORD" \
  -X POST 'http://localhost:5601/api/dashboards' \
  -H 'kbn-xsrf: true' \
  -H 'content-type: application/json' \
  --data-binary @dashboards/random-pass-service-health.json | jq -r '.id')"
printf 'Dashboard: http://localhost:5601/app/dashboards#/view/%s\n' "$DASHBOARD_ID"
```

The load generator sends a password-generation request every two seconds. The
project collector forwards its telemetry to Jaeger and to the EDOT collector on
the shared `elastic-start-local_default` Docker network.

## Verify

- Frontend: http://localhost:3000
- Gateway health: http://localhost:8080/health
- Kibana: http://localhost:5601
- SLOs: http://localhost:5601/app/slos
- Jaeger: http://localhost:16686

In Kibana Service Inventory, choose **Last 15 minutes** and disable comparison.
The current traffic should appear within about a minute.

## Machine Learning

After the load generator has produced a baseline, enable APM anomaly detection
for the `local` environment in Kibana. Keep the environment filter scoped to
`local`; it prevents local demo traffic from being combined with another
environment's baseline.

The enabled job should analyze transaction metrics by `service.name` and
`transaction.type`, with detectors for:

- high mean transaction latency
- transaction throughput
- high mean failed-transaction rate

Its datafeed should read `metrics-apm*`, `apm-*`, and `metrics-*.otel-*`, with
filters for `processor.event: metric`, `metricset.name: transaction`, and
`service.environment: local`. A 15-minute bucket span is appropriate for this
low-volume demo. Let the default traffic run for 10-15 minutes before presenting
an anomaly scenario.

## Restart Without Resetting Data

When the Elastic volumes already contain the dashboard and SLOs, start only the
two stacks. Do not rerun the fresh-install SLO commands, as they create new SLO
objects.

```sh
./elastic-start-local/start.sh
docker compose --profile demo up -d --build
```

## Reset

To discard all demo state, stop the microservices and remove the Elastic
volumes, then follow **Fresh Elastic Install** again.

```sh
docker compose --profile demo down -v
./elastic-start-local/uninstall.sh
```
