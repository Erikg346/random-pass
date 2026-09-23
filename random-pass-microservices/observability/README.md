# Observability Tools for Random Password Microservices

This directory contains the configuration and documentation for observability tools used in the Random Password Microservices architecture.

## OpenTelemetry

The OpenTelemetry collector is configured to collect and export telemetry data from the various microservices. The configuration file is located in `otel-collector-config.yaml`.

## Prometheus

Prometheus is used for monitoring and alerting. The configuration file for Prometheus is located in `prometheus.yaml`. This file defines the scrape configurations and alerting rules for the microservices.

## Setup Instructions

1. Ensure that the OpenTelemetry collector and Prometheus are properly installed and configured in your environment.
2. Update the configuration files as necessary to match your deployment setup.
3. Start the OpenTelemetry collector and Prometheus services.
4. Verify that the telemetry data is being collected and can be viewed in your monitoring dashboard.

## Usage

Refer to the individual configuration files for detailed settings and options. Make sure to consult the official documentation for OpenTelemetry and Prometheus for advanced configurations and best practices.