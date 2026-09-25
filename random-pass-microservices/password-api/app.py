from flask import Flask, jsonify, request
import secrets
import string
import os
import time
from datetime import datetime, timezone
import redis
import requests
from redis.exceptions import RedisError
from openfeature import api as openfeature_api
from openfeature.contrib.provider.flagd import FlagdProvider

# OpenTelemetry
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry import trace
from otel import setup_otel

setup_otel("password-api")
openfeature_api.set_provider(
    FlagdProvider(
        host=os.getenv("FLAGD_HOST", "flagd"),
        port=int(os.getenv("FLAGD_PORT", "8013")),
    )
)
flag_client = openfeature_api.get_client()

# --- App ---
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RedisInstrumentor().instrument()

API_VERSION = "2.7.0"
APP_STARTED_AT = time.time()
REQUEST_METRICS = {"requests": 0, "cache_hits": 0, "generated": 0, "errors": 0}

# --- Redis ---
redis_host = os.getenv("REDIS_HOST", "redis")
history_service_url = os.getenv("HISTORY_SERVICE_URL", "http://history-service:5002")
policy_service_url = os.getenv("POLICY_SERVICE_URL", "http://policy-service:5001")
notification_service_url = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:5003")
redis_client = redis.Redis(
    host=redis_host,
    port=6379,
    socket_connect_timeout=2,
    socket_timeout=2,
    decode_responses=True,
)

PASSWORD_CHARS = (
    string.ascii_letters
    + string.digits
    + "!@#$%^&*()-_=+[]{}|;:,.<>?/"
)


def is_scenario_enabled(flag_key):
    try:
        return flag_client.get_boolean_value(flag_key, False)
    except Exception as error:
        app.logger.warning("Flag evaluation failed for %s: %s", flag_key, error)
        return False


@app.route("/generate-password")
def generate_password():
    REQUEST_METRICS["requests"] += 1
    started_at = time.perf_counter()
    app.logger.info("password generation request received")

    scenarios = {
        "api_latency": is_scenario_enabled("simulate_api_latency"),
        "policy_failure": is_scenario_enabled("simulate_policy_failure"),
    }
    span = trace.get_current_span()
    for scenario, enabled in scenarios.items():
        span.set_attribute(f"demo.scenario.{scenario}", enabled)
    span_context = span.get_span_context()
    trace_id = format(span_context.trace_id, "032x") if span_context.is_valid else None

    try:
        length = int(request.args.get("length", 12))
    except (TypeError, ValueError):
        REQUEST_METRICS["errors"] += 1
        return jsonify({"error": "length must be an integer"}), 400

    if not 8 <= length <= 128:
        REQUEST_METRICS["errors"] += 1
        return jsonify({"error": "length must be between 8 and 128"}), 400

    cache_key = f"password:{length}"
    source = "generated"

    if scenarios["api_latency"]:
        app.logger.warning("Demo scenario active: api_latency")
        time.sleep(1.5)

    try:
        policy_response = requests.get(
            f"{policy_service_url}/policies/default",
            headers={"X-Demo-Policy-Failure": "true"} if scenarios["policy_failure"] else {},
            timeout=0.75,
        )
        policy_response.raise_for_status()
    except requests.RequestException as e:
        REQUEST_METRICS["errors"] += 1
        app.logger.warning("Policy service unavailable: %s", e)
        return jsonify({
            "error": "password policy validation is unavailable",
            "trace_id": trace_id,
            "active_scenarios": [name for name, enabled in scenarios.items() if enabled],
        }), 503

    try:
        cached = redis_client.get(cache_key)
        if cached:
            source = "cache"
            password = cached
            REQUEST_METRICS["cache_hits"] += 1
        else:
            password = "".join(secrets.choice(PASSWORD_CHARS) for _ in range(length))
    except RedisError as e:
        app.logger.warning(f"Redis get failed: {e}")
        password = "".join(secrets.choice(PASSWORD_CHARS) for _ in range(length))

    if source == "generated":
        REQUEST_METRICS["generated"] += 1
        try:
            redis_client.setex(cache_key, 60, password)
        except RedisError as e:
            app.logger.warning(f"Redis set failed: {e}")

    try:
        requests.post(
            f"{history_service_url}/log-password-generation",
            json={"user_id": "demo-user", "length": length, "source": source, "trace_id": trace_id},
            timeout=0.75,
        )
    except requests.RequestException as e:
        app.logger.warning(f"History service unavailable: {e}")

    try:
        requests.post(
            f"{notification_service_url}/notifications",
            json={"user_id": "demo-user", "length": length, "source": source, "trace_id": trace_id},
            timeout=0.75,
        )
    except requests.RequestException as e:
        app.logger.warning(f"Notification service unavailable: {e}")

    return jsonify({
        "password": password,
        "source": source,
        "trace_id": trace_id,
        "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
        "active_scenarios": [name for name, enabled in scenarios.items() if enabled],
    })


@app.route("/health")
def health():
    redis_status = "UP"
    try:
        redis_client.ping()
    except RedisError:
        redis_status = "DOWN"

    status = "UP" if redis_status == "UP" else "DEGRADED"
    return jsonify({"status": status, "services": {"password_api": "UP", "redis": redis_status}})


@app.route("/metrics")
def metrics():
    requests = REQUEST_METRICS["requests"]
    cache_hit_rate = round((REQUEST_METRICS["cache_hits"] / requests) * 100, 1) if requests else 0
    return jsonify({
        **REQUEST_METRICS,
        "cache_hit_rate": cache_hit_rate,
        "uptime_seconds": round(time.time() - APP_STARTED_AT),
        "started_at": datetime.fromtimestamp(APP_STARTED_AT, timezone.utc).isoformat(),
    })


@app.route("/version")
def version():
    return jsonify({"version": API_VERSION})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)