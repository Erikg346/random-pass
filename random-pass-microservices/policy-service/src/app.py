from flask import Flask, jsonify, request
import os

# OpenTelemetry
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from otel import setup_otel

setup_otel("policy-service")

# --- App ---
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

API_VERSION = "1.0.0"

# In-memory storage for password policies
password_policies = {}

@app.route("/policies", methods=["GET"])
def get_policies():
    return jsonify(password_policies)

@app.route("/policies/<policy_name>", methods=["GET"])
def get_policy(policy_name):
    policy = password_policies.get(policy_name)
    if policy:
        return jsonify(policy)
    return jsonify({"error": "Policy not found"}), 404

@app.route("/policies", methods=["POST"])
def create_policy():
    policy_name = request.json.get("name")
    policy_rules = request.json.get("rules")
    if not policy_name or not policy_rules:
        return jsonify({"error": "Invalid input"}), 400
    password_policies[policy_name] = policy_rules
    return jsonify({"message": "Policy created"}), 201

@app.route("/policies/<policy_name>", methods=["PUT"])
def update_policy(policy_name):
    if policy_name not in password_policies:
        return jsonify({"error": "Policy not found"}), 404
    policy_rules = request.json.get("rules")
    if not policy_rules:
        return jsonify({"error": "Invalid input"}), 400
    password_policies[policy_name] = policy_rules
    return jsonify({"message": "Policy updated"}), 200

@app.route("/health")
def health():
    return jsonify({"status": "UP"})

@app.route("/version")
def version():
    return jsonify({"version": API_VERSION})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)