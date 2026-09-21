"""Invoke the private Lambda API and verify both readiness and release identity."""
import argparse
import base64
import json
import subprocess
import tempfile
from pathlib import Path


def event_for(path, method="GET"):
    return {
        "version": "2.0", "routeKey": "$default", "rawPath": path,
        "rawQueryString": "", "headers": {"host": "portfolio.local"},
        "requestContext": {
            "accountId": "demo", "apiId": "demo", "domainName": "portfolio.local",
            "domainPrefix": "portfolio", "requestId": "portfolio-demo", "routeKey": "$default",
            "stage": "$default", "time": "01/Jan/2026:00:00:00 +0000", "timeEpoch": 1767225600000,
            "http": {"method": method, "path": path, "protocol": "HTTP/1.1",
                     "sourceIp": "127.0.0.1", "userAgent": "portfolio-demo"},
        },
        "body": "", "isBase64Encoded": False,
    }


def validate_response(metadata, payload, path, expected_version):
    if metadata.get("FunctionError"):
        raise ValueError(f"Lambda execution error: {payload}")
    if metadata.get("StatusCode") != 200 or payload.get("statusCode") != 200:
        raise ValueError(f"Unexpected response: metadata={metadata}, payload={payload}")
    body = payload.get("body", "")
    if payload.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    data = json.loads(body)
    if path == "/version" and data.get("version") != expected_version:
        raise ValueError(f"Expected version {expected_version}; got {data.get('version')}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--function-name", required=True)
    parser.add_argument("--qualifier", default="live")
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        for path in ("/healthz", "/readyz", "/version"):
            event_path = Path(directory) / "event.json"
            output_path = Path(directory) / "response.json"
            event_path.write_text(json.dumps(event_for(path)), encoding="utf-8")
            metadata = json.loads(subprocess.check_output([
                "aws", "lambda", "invoke", "--function-name", args.function_name,
                "--qualifier", args.qualifier, "--cli-binary-format", "raw-in-base64-out",
                "--payload", f"file://{event_path}", "--output", "json", str(output_path),
            ], text=True))
            validate_response(metadata, json.loads(output_path.read_text()), path, args.expected_version)
            print(f"PASS: Lambda {args.qualifier} {path}")
    print(f"Verified AWS release: {args.expected_version}")


if __name__ == "__main__":
    main()
