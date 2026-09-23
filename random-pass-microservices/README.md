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
4. Use `docker-compose up` to start all services.

## Usage Examples

- Access the password API at `http://localhost:5000/generate-password?length=12`.
- Use the policy service to manage password policies via its defined routes.
- View password generation history through the history service.

## Observability

This project integrates OpenTelemetry for tracing and metrics, and Prometheus for monitoring. Ensure the observability tools are configured correctly to collect and visualize data.

## Feature Flags

Feature flags are managed through the flagd service, allowing for dynamic feature management across the microservices.