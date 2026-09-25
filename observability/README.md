# Observability for Random Pass

This directory contains the OpenTelemetry collector configuration for the
Random Pass demo.

## Telemetry Pipeline

The collector receives application traces, metrics, and logs over OTLP. It also
collects Docker container metrics and Redis metrics directly, then forwards all
signals to Elastic EDOT.

## Included Signals

- Application traces, metrics, and logs
- Docker CPU, memory, network, and block-I/O metrics
- Redis infrastructure metrics

## Usage

The collector starts with `docker compose --profile demo up -d --build`. Open
Kibana at `http://localhost:5601` to investigate service, SLO, alert, ML, and
infrastructure telemetry.