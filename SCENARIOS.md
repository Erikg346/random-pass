# Observability Scenarios

The Flagd configurator at http://localhost:4000/ controls the same
`flagd/config/flags.json` file watched by the running Flagd service. Start from
the default `off` variant and enable one scenario at a time.

## API Latency

Set `simulate_api_latency` to `on`, then send traffic through the gateway:

```sh
curl 'http://localhost:8080/generate-password?length=16'
```

Expected behavior: requests remain successful but take roughly 1.5 seconds.
The response contains `active_scenarios: ["api_latency"]`. In Elastic, open a
slow `password-api` trace; its root span has `demo.scenario.api_latency: true`.
This demonstrates a latency regression without an availability incident.

## Redis Dependency Latency

Set `simulate_redis_latency` to `on`, then repeat the request.

Expected behavior: requests remain successful but take roughly 750 ms longer.
The response contains `active_scenarios: ["redis_latency"]`. In Elastic, open
the trace and inspect the `redis.dependency.simulated_latency` span, which is
tagged with `db.system: redis` and `demo.scenario.redis_latency: true`. This
demonstrates separating a slow dependency from a general application slowdown.

## Policy Outage

Set `simulate_policy_failure` to `on`, then repeat the request.

Expected behavior: the gateway returns `503` with `policy_failure` and a trace
ID. In Elastic, use that trace ID to find the failed `policy-service` dependency
span. The `password-api` request fails because policy validation is required.
This demonstrates tracing from user impact to the owning downstream service.

## Demo Flow

1. Keep all scenario flags `off` and establish a two-minute baseline.
2. Enable one flag for two to five minutes while the load generator runs.
3. Show the affected SLO and Service Inventory metrics.
4. Open an affected trace and inspect `demo.scenario.*` attributes.
5. Disable the flag and show the recovery.

Always return the active scenario to `off` after a demonstration.
