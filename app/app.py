"""Small portfolio application: release identity, health checks and JSON logs."""

import json
import os
import sys
import time
from datetime import datetime, timezone

from flask import Flask, g, jsonify, render_template, request


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        APP_VERSION=os.getenv("APP_VERSION", "local"),
        APP_MESSAGE="Hello from my cloud project!",
        ENABLE_DEMO_ERRORS=os.getenv("ENABLE_DEMO_ERRORS", "false").lower() == "true",
        FORCE_NOT_READY=os.getenv("FORCE_NOT_READY", "false").lower() == "true",
    )
    if test_config:
        app.config.update(test_config)

    @app.before_request
    def start_timer():
        g.started = time.perf_counter()

    @app.after_request
    def log_request(response):
        # One JSON record per HTTP request, suitable for a CloudWatch metric filter.
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "request",
            "level": "ERROR" if response.status_code >= 500 else "INFO",
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": round((time.perf_counter() - g.started) * 1000, 3),
            "version": app.config["APP_VERSION"],
        }
        print(json.dumps(record), file=sys.stdout, flush=True)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.get("/")
    def index():
        return render_template(
            "index.html", version=app.config["APP_VERSION"], message=app.config["APP_MESSAGE"]
        )

    @app.get("/version")
    def version():
        return jsonify(version=app.config["APP_VERSION"], message=app.config["APP_MESSAGE"])

    @app.get("/healthz")
    def health():
        # Liveness: the process can answer a request.
        return jsonify(status="ok")

    @app.get("/readyz")
    def ready():
        # Readiness: Kubernetes should send user traffic to this process.
        if app.config["FORCE_NOT_READY"]:
            return jsonify(status="not_ready"), 503
        return jsonify(status="ready")

    @app.post("/demo/error")
    def demo_error():
        # Deliberate, temporary learning exercise. Disabled by default.
        if not app.config["ENABLE_DEMO_ERRORS"]:
            return jsonify(error="not_found"), 404
        return jsonify(error="intentional_demo_error"), 500

    return app


app = create_app()

if __name__ == "__main__":
    # Local development only. The Docker image uses Gunicorn.
    app.run(host="127.0.0.1", port=8080, debug=False)
