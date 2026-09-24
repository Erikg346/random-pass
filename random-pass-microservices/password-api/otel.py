import os
import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry import _logs
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

def setup_otel(service_name):
    attributes = {
        "service.name": service_name,
        "service.namespace": "random-pass",
        "deployment.environment": os.getenv("DEPLOYMENT_ENVIRONMENT", "local"),
        "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
        "service.domain": os.getenv("SERVICE_DOMAIN", "security"),
        "service.tier": os.getenv("SERVICE_TIER", "backend"),
        "team.name": os.getenv("TEAM_NAME", "platform-engineering"),
    }
    for pair in os.getenv("OTEL_RESOURCE_ATTRIBUTES", "").split(","):
        if "=" in pair:
            key, value = pair.split("=", 1)
            attributes[key.strip()] = value.strip()

    resource = Resource.create(attributes)

    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(service_name)

    otlp_exporter = OTLPSpanExporter()
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
    _logs.set_logger_provider(logger_provider)
    # Disable logging handler to prevent log explosion from OTEL encoder errors
    # Logs are not critical to observability demo; traces and metrics are sufficient
    FlaskInstrumentor().instrument()
    RedisInstrumentor().instrument()
    RequestsInstrumentor().instrument()