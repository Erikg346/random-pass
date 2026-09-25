import json
import os
import random
import time
from datetime import datetime, timezone

import requests

TARGET_URL = os.getenv("TARGET_URL", "http://password-api:5000/generate-password")
INTERVAL_SECONDS = float(os.getenv("INTERVAL_SECONDS", "2"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "3"))


def run():
    print(json.dumps({"event": "load_generator_started", "target": TARGET_URL}), flush=True)
    while True:
        length = random.choice([12, 16, 20, 24])
        started = time.perf_counter()
        try:
            response = requests.get(
                TARGET_URL,
                params={"length": length},
                timeout=REQUEST_TIMEOUT,
            )
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            payload = response.json()
            print(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "load_request",
                "status_code": response.status_code,
                "length": length,
                "source": payload.get("source"),
                "trace_id": payload.get("trace_id"),
                "duration_ms": duration_ms,
            }), flush=True)
        except requests.RequestException as error:
            print(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "load_request_failed",
                "error": str(error),
            }), flush=True)
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
