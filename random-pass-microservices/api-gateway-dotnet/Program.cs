using System.Net.Http.Json;
using System.Text.Json;
using OpenTelemetry.Resources;
using OpenTelemetry.Logs;
using OpenTelemetry.Trace;

var builder = WebApplication.CreateBuilder(args);
var otlpEndpoint = builder.Configuration["OTEL_EXPORTER_OTLP_ENDPOINT"] ?? "http://otel-collector:4317";
var passwordApi = builder.Configuration["PASSWORD_API_URL"] ?? "http://password-api:5000";
var policyService = builder.Configuration["POLICY_SERVICE_URL"] ?? "http://policy-service:5001";
var notificationService = builder.Configuration["NOTIFICATION_SERVICE_URL"] ?? "http://notification-service:5003";

builder.Logging.AddOpenTelemetry(logging =>
{
    logging.IncludeFormattedMessage = true;
    logging.IncludeScopes = true;
    logging.ParseStateValues = true;
    logging.AddOtlpExporter(options => options.Endpoint = new Uri(otlpEndpoint));
});

builder.Services.AddHttpClient();
builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource
        .AddService("api-gateway", serviceVersion: "1.0.0")
        .AddAttributes(new Dictionary<string, object>
        {
            ["service.namespace"] = "random-pass",
            ["deployment.environment"] = "local",
            ["service.domain"] = "edge",
            ["service.tier"] = "gateway",
            ["team.name"] = "platform-engineering",
        }))
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddOtlpExporter(options => options.Endpoint = new Uri(otlpEndpoint)));

var app = builder.Build();
app.Logger.LogInformation("api gateway started");
app.MapGet("/health", async (IHttpClientFactory factory) => {
    var client = factory.CreateClient();
    var services = new Dictionary<string, string> { ["gateway"] = "UP" };
    foreach (var item in new[] { ("password_api", $"{passwordApi}/health"), ("policy_service", $"{policyService}/health"), ("notification_service", $"{notificationService}/health") }) {
        try {
            var response = await client.GetFromJsonAsync<JsonElement>(item.Item2);
            services[item.Item1] = response.GetProperty("status").GetString() ?? "UNKNOWN";
            if (item.Item1 == "password_api" && response.TryGetProperty("services", out var dependencies) && dependencies.TryGetProperty("redis", out var redis)) {
                services["redis"] = redis.GetString() ?? "UNKNOWN";
            }
        }
        catch { services[item.Item1] = "DOWN"; }
    }
    return Results.Ok(new { status = services.Values.All(value => value == "UP") ? "UP" : "DEGRADED", services });
});
app.MapGet("/metrics", async (IHttpClientFactory factory) => Results.Ok(await factory.CreateClient().GetFromJsonAsync<object>($"{passwordApi}/metrics")));
app.MapGet("/generate-password", async (HttpRequest request, IHttpClientFactory factory) => {
    var length = request.Query["length"].ToString();
    var response = await factory.CreateClient().GetAsync($"{passwordApi}/generate-password?length={Uri.EscapeDataString(length)}");
    return Results.Content(await response.Content.ReadAsStringAsync(), "application/json", statusCode: (int)response.StatusCode);
});
app.MapGet("/policy-health", async (IHttpClientFactory factory) => Results.Ok(await factory.CreateClient().GetFromJsonAsync<object>($"{policyService}/health")));
app.Run();
