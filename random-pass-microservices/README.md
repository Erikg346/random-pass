# random-pass-microservices

This project is a microservices architecture for generating and managing passwords. It consists of several services, each responsible for a specific functionality, along with a frontend application and observability tools.

## Project Structure

- **password-api**: A Flask application for generating passwords.
  - **app.py**: Main application file with routes for password generation, health check, and version retrieval.
  - **otel.py**: Configuration for OpenTelemetry to enable observability.
  - **requirements.txt**: Python dependencies for the password API.
  - **README.md**: Documentation for the password API.

- **policy-service**: A Flask application for managing password policies.
  - **src/app.py**: Main application file with routes for creating and managing password policies.
  - **requirements.txt**: Python dependencies for the policy service.
  - **README.md**: Documentation for the policy service.

- **history-service**: A Flask application for logging and retrieving password generation history.
  - **src/app.py**: Main application file with routes for managing password generation history.
  - **requirements.txt**: Python dependencies for the history service.
  - **README.md**: Documentation for the history service.

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
  - **prometheus.yaml**: Configuration for Prometheus.
  - **README.md**: Documentation for observability tools.

- **docker-compose.yml**: Defines services, networks, and volumes for the microservices architecture.

## Setup Instructions

1. Clone the repository.
2. Navigate to each service directory and install the required dependencies.
3. Configure the environment variables as needed.
4. Use `docker compose up -d --build` to start all services.

The primary console is available at `http://localhost:3000`. It shows live API,
Redis, policy, history, and telemetry status. Jaeger is available at
`http://localhost:16686`; the flag configurator is available at
`http://localhost:4000/feature/`.

## Runtime Diversity

The running request path intentionally uses multiple application runtimes:

| Service | Runtime | Migration story |
| --- | --- | --- |
| API Gateway | ASP.NET Core / .NET 8 | New front door replacing the IIS edge |
| Password API | Python / Flask | Existing business capability extracted from the monolith |
| Policy Service | ASP.NET Core / .NET 8 | Rules bounded context owned by a .NET team |
| History Service | Java / Spring Boot | Event history bounded context owned by a Java team |
| Notification Service | Node.js | Notification boundary for downstream events |

The original Python policy and history implementations remain in the repository
as reference implementations for comparing the migration.

## Request Flow

Password generation follows this path:

`frontend -> api-gateway -> password-api -> policy-service`

`password-api -> history-service -> redis`

`password-api -> notification-service`

Every service exports OpenTelemetry traces through the collector to Jaeger.
The generation response includes a trace ID, and history stores generation
metadata without storing the generated password.

The flagd configuration includes demonstration scenarios for
`simulate_api_latency`, `simulate_history_failure`, and
`simulate_policy_failure`. These are the starting points for wiring controlled
fault injection into the request path.

## Elastic Observability Demo

Start Elastic's local Elasticsearch, Kibana, and EDOT collector in a separate
terminal:

```bash
curl -fsSL https://elastic.co/start-local | sh -s -- --edot
```

Then start this project with the optional traffic generator:

```bash
docker compose --profile demo up -d --build
```

The collector fans out traces to both Jaeger and Elastic EDOT. Open Kibana at
`http://localhost:5601` and Jaeger at `http://localhost:16686`. The load
generator emits one request every two seconds and prints structured request
logs, making the distributed request flow visible during a presentation.

## Usage Examples

- Access the password API at `http://localhost:5000/generate-password?length=12`.
- Use the policy service to manage password policies via its defined routes.
- View password generation history through the history service.

## Observability

This project integrates OpenTelemetry for tracing and metrics, and Prometheus for monitoring. Ensure the observability tools are configured correctly to collect and visualize data.

## Feature Flags

Feature flags are managed through the flagd service, allowing for dynamic feature management across the microservices.