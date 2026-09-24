using OpenTelemetry.Resources;
using OpenTelemetry.Logs;
using OpenTelemetry.Trace;

var builder = WebApplication.CreateBuilder(args);
var otlpEndpoint = builder.Configuration["OTEL_EXPORTER_OTLP_ENDPOINT"] ?? "http://otel-collector:4317";

builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource
        .AddService("policy-service", serviceVersion: "2.0.0")
        .AddAttributes(new Dictionary<string, object>
        {
            ["service.namespace"] = "random-pass",
            ["deployment.environment"] = "local",
            ["service.domain"] = "security",
            ["service.tier"] = "backend",
            ["team.name"] = "identity-platform",
        }))
    .WithLogging(logging => logging
        .AddOtlpExporter(options => options.Endpoint = new Uri(otlpEndpoint)))
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddOtlpExporter(options => options.Endpoint = new Uri(otlpEndpoint)));

var app = builder.Build();
var policy = new { min_length = 12, require_uppercase = true, require_special = true };

app.MapGet("/health", () => Results.Ok(new { status = "UP" }));
app.MapGet("/version", () => Results.Ok(new { version = "2.0.0-dotnet" }));
app.MapGet("/policies/default", () => Results.Ok(policy));
app.MapGet("/policies", () => Results.Ok(new Dictionary<string, object> { ["default"] = policy }));

app.Run();
