"""Check readiness AND release identity; fail with a useful nonzero exit code."""
import argparse
import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def check(base_url, expected_version):
    for path in ("/healthz", "/readyz", "/version"):
        with urlopen(base_url.rstrip("/") + path, timeout=3) as response:
            data = json.load(response)
        if path == "/version" and data.get("version") != expected_version:
            raise ValueError(f"Expected release {expected_version}, received {data.get('version')}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url")
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--attempts", type=int, default=20)
    args = parser.parse_args()
    if args.attempts < 1:
        parser.error("--attempts must be at least 1")
    for attempt in range(1, args.attempts + 1):
        try:
            check(args.base_url, args.expected_version)
            print(f"PASS: healthy application, release {args.expected_version}")
            return 0
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            print(f"Attempt {attempt}/{args.attempts}: {exc}", file=sys.stderr)
            if attempt < args.attempts:
                time.sleep(2)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
