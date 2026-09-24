const { NodeSDK } = require('@opentelemetry/sdk-node');
const { trace } = require('@opentelemetry/api');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { resourceFromAttributes } = require('@opentelemetry/resources');

const traceExporter = new OTLPTraceExporter({
  url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://otel-collector:4317',
});
const sdk = new NodeSDK({
  resource: resourceFromAttributes({
    'service.name': process.env.OTEL_SERVICE_NAME || 'notification-service',
  }),
  traceExporter,
  instrumentations: [getNodeAutoInstrumentations()],
});
sdk.start();

const express = require('express');
const app = express();
app.use(express.json());
const notifications = [];

app.get('/health', (_request, response) => response.json({ status: 'UP' }));
app.post('/notifications', (request, response) => {
  const tracer = trace.getTracer('notification-service');
  tracer.startActiveSpan('notification.queue', (span) => {
    const event = { ...request.body, received_at: new Date().toISOString() };
    span.setAttribute('notification.source', event.source || 'unknown');
    span.setAttribute('notification.length', Number(event.length || 0));
    notifications.unshift(event);
    notifications.splice(20);
    console.log(JSON.stringify({ event: 'notification_queued', ...event }));
    span.end();
    response.status(202).json({ status: 'accepted', notification_id: `${Date.now()}` });
  });
});
app.get('/notifications', (_request, response) => response.json({ notifications }));

const port = Number(process.env.PORT || 5003);
app.listen(port, '0.0.0.0', () => console.log(`notification-service listening on ${port}`));
