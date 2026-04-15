from flask import Flask, jsonify, request
import secrets
import string
import os
import redis
from redis.exceptions import RedisError

# OpenTelemetry
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from otel import setup_otel

setup_otel("password-api")

# --- App ---
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RedisInstrumentor().instrument()

API_VERSION = "2.7.0"

# --- Redis ---
redis_host = os.getenv("REDIS_HOST", "redis")
redis_client = redis.Redis(
    host=redis_host,
    port=6379,
    socket_connect_timeout=2,
    socket_timeout=2,
    decode_responses=True,
)
RedisInstrumentor().instrument()

PASSWORD_CHARS = (
    string.ascii_letters
    + string.digits
    + "!@#$%^&*()-_=+[]{}|;:,.<>?/"
)

@app.route("/generate-password")

@app.route("/generate-password")
def generate_password():
    length = int(request.args.get("length", 12))
    cache_key = f"password:{length}"

    try:
        cached = redis_client.get(cache_key)
        if cached:
            return jsonify({"password": cached, "source": "cache"})
    except RedisError as e:
        app.logger.warning(f"Redis get failed: {e}")

    password = "".join(secrets.choice(PASSWORD_CHARS) for _ in range(length))

    try:
        redis_client.setex(cache_key, 60, password)
    except RedisError as e:
        app.logger.warning(f"Redis set failed: {e}")

    return jsonify({"password": password, "source": "generated"})

@app.route("/health")
def health():
    return jsonify({"status": "UP"})

@app.route("/version")
def version():
    return jsonify({"version": API_VERSION})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

