# random-pass-microservices

Random Pass is a containerized password-generation demo with feature-controlled
incident scenarios and Elastic Observability.
<img width="1052" height="888" alt="image" src="https://github.com/user-attachments/assets/21f66aa7-9091-4e16-8e13-d4f3059e1087" />


## Quick Start

Prerequisites:

- Docker Desktop with at least 10 GB of memory available to containers
- Docker Compose v2
- `curl` and `jq`

```sh
./bootstrap.sh
```

The bootstrap starts Elastic, the microservices demo, continuous traffic, SLOs,
burn-rate alerts, the Service Health dashboard, and local APM anomaly detection.
See [BOOTSTRAP.md](BOOTSTRAP.md) for restart and reset details.

At completion, the bootstrap prints the local Kibana URL and the generated
`elastic` login credentials.

Run `./reset.sh` to remove all local demo and Elastic data volumes, then run
`./bootstrap.sh` for a clean state.

## Project Structure

- **password-api**: A Flask application for generating passwords.
  - **app.py**: Main application file with routes for password generation, health check, and version retrieval.
  - **otel.py**: Configuration for OpenTelemetry to enable observability.
  - **requirements.txt**: Python dependencies for the password API.
  - **README.md**: Documentation for the password API.

- **policy-service-dotnet**: An ASP.NET Core service that provides password policy rules.

- **frontend**: A React application for interacting with the password API.
  - **src/App.tsx**: Main entry point for the frontend application.
  - **src/components/PasswordGenerator.tsx**: Component for generating passwords.
  - **src/types/index.ts**: TypeScript interfaces and types.
  - **package.json**: Configuration for npm.
  - **tsconfig.json**: TypeScript configuration.
  - **README.md**: Documentation for the frontend application.

- **flagd**: Service for managing feature flags.
  - **config/flags.json**: Configuration for feature flags.
  - **README.md**: Documentation for the feature flag service.

- **observability**: Configuration for monitoring and observability tools.
  - **otel-collector-config.yaml**: Configuration for OpenTelemetry collector.
  - **README.md**: Documentation for observability tools.

- **docker-compose.yml**: Defines services, networks, and volumes for the microservices architecture.

## Access

- Frontend: http://localhost:3000
- Gateway health: http://localhost:8080/health
- Kibana: http://localhost:5601
- Flagd UI: http://localhost:4000

## Runtime Diversity

The running request path intentionally uses multiple application runtimes:

| Service | Runtime | Migration story |
| --- | --- | --- |
| API Gateway | ASP.NET Core / .NET 8 | New front door replacing the IIS edge |
| Password API | Python / Flask | Existing business capability extracted from the monolith |
| Policy Service | ASP.NET Core / .NET 8 | Rules bounded context owned by a .NET team |
| Notification Service | Node.js | Notification boundary for downstream events |

## Request Flow

Password generation follows this path:

`frontend -> api-gateway -> password-api -> policy-service`

`password-api -> notification-service`

Every service exports OpenTelemetry traces through the collector to Elastic.
The generation response includes a trace ID for use in Elastic investigation.

The flagd configuration includes demonstration scenarios for
`simulate_api_latency`, `simulate_redis_latency`, and
`simulate_policy_failure`. See [SCENARIOS.md](SCENARIOS.md) for the controlled
incident and troubleshooting workflows.

## Elastic Observability Demo

`bootstrap.sh` starts Elasticsearch, Kibana, EDOT, and the load generator. The
collector exports application, Docker, and Redis telemetry to Elastic. Kibana
contains the Service Health dashboard, SLOs, burn-rate alerts, and the data
needed to enable local-environment ML anomaly detection.

## Usage Examples

- Access the password API at `http://localhost:5000/generate-password?length=12`.
- Use the policy service to manage password policies via its defined routes.

## Observability

This project uses OpenTelemetry and Elastic for traces, logs, application
metrics, Docker container metrics, Redis metrics, SLOs, alerts, and ML.

## Feature Flags

Feature flags are managed through the flagd service, allowing for dynamic feature management across the microservices.
