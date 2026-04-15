from flask import Flask, render_template, request, jsonify
import requests
import os

# OpenTelemetry
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from otel import setup_otel

setup_otel("password-ui")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

API_URL = os.getenv("API_URL", "http://api:5000")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate-password")
def generate_password():
    length = request.args.get("length", 12)
    resp = requests.get(
        f"{API_URL}/generate-password",
        params={"length": length},
        timeout=5,
    )
    return jsonify(resp.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)