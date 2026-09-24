from flask import Flask, jsonify, request
import os
import json
import redis
from redis.exceptions import RedisError

# OpenTelemetry
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from otel import setup_otel

setup_otel("history-service")

# --- App ---
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RedisInstrumentor().instrument()

# --- Redis ---
redis_host = os.getenv("REDIS_HOST", "redis")
redis_client = redis.Redis(
    host=redis_host,
    port=6379,
    socket_connect_timeout=2,
    socket_timeout=2,
    decode_responses=True,
)

@app.route("/log-password-generation", methods=["POST"])
def log_password_generation():
    data = request.json
    user_id = data.get("user_id")
    length = data.get("length")
    source = data.get("source")
    trace_id = data.get("trace_id")
    
    if not user_id or not length or not source:
        return jsonify({"error": "user_id, length, and source are required"}), 400

    try:
        event = {"user_id": user_id, "length": length, "source": source, "trace_id": trace_id}
        redis_client.lpush("password_history", json.dumps(event))
    except RedisError as e:
        app.logger.warning(f"Redis lpush failed: {e}")
        return jsonify({"error": "Failed to log password generation"}), 500

    return jsonify({"message": "Password generation logged successfully"}), 201

@app.route("/history/<user_id>", methods=["GET"])
def get_history(user_id):
    try:
        history = redis_client.lrange("password_history", 0, -1)
        user_history = []
        for entry in history:
            try:
                event = json.loads(entry)
            except json.JSONDecodeError:
                continue
            if event.get("user_id") == user_id:
                user_history.append(event)
    except RedisError as e:
        app.logger.warning(f"Redis lrange failed: {e}")
        return jsonify({"error": "Failed to retrieve history"}), 500

    return jsonify({"history": user_history}), 200

@app.route("/health")
def health():
    return jsonify({"status": "UP"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)