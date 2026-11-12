#!/usr/bin/env python3
"""Ship one Docker container's stdout/stderr to an OTLP Logs endpoint.

Designed for the Sharebook frontend host service: no Docker logging plugin and
no modification to the application container are required.  It follows the
named container again after a Coolify replacement, so a frontend restart does
not silently stop collection.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


def now_ns() -> str:
    return str(time.time_ns())


def timestamp_ns(value: str) -> str:
    try:
        return str(int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1_000_000_000))
    except ValueError:
        return now_ns()


def post(endpoint: str, username: str, token: str, service: str, line: str, timestamp: str) -> None:
    payload = {
        "resourceLogs": [{
            "resource": {"attributes": [
                {"key": "service.name", "value": {"stringValue": service}},
                {"key": "deployment.environment", "value": {"stringValue": "production"}},
            ]},
            "scopeLogs": [{"scope": {"name": "sharebook-docker-log-shipper"}, "logRecords": [{
                "timeUnixNano": timestamp,
                "observedTimeUnixNano": now_ns(),
                "severityText": "INFO",
                "body": {"stringValue": line},
            }]}],
        }],
    }
    auth = base64.b64encode(f"{username}:{token}".encode()).decode()
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, separators=(",", ":")).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Basic {auth}"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        if response.status not in (200, 202, 204):
            raise RuntimeError(f"OTLP returned HTTP {response.status}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--container", default="sharebook-frontend")
    parser.add_argument("--service-name", default="sharebook-frontend")
    args = parser.parse_args()

    endpoint = os.environ["GRAFANA_CLOUD_LOGS_OTLP_ENDPOINT"]
    username = os.environ["GRAFANA_CLOUD_LOGS_OTLP_INSTANCE_ID"]
    token = os.environ["GRAFANA_CLOUD_LOGS_OTLP_TOKEN"]

    while True:
        command = ["docker", "logs", "--tail", "0", "--follow", "--timestamps", args.container]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        assert process.stdout is not None
        for raw in process.stdout:
            raw = raw.rstrip("\n")
            timestamp, separator, line = raw.partition(" ")
            if not separator:
                line, timestamp = raw, ""
            try:
                post(endpoint, username, token, args.service_name, line, timestamp_ns(timestamp))
            except (OSError, RuntimeError, urllib.error.URLError, urllib.error.HTTPError) as exc:
                print(f"ship_error={type(exc).__name__}", flush=True)
        process.wait()
        time.sleep(3)


if __name__ == "__main__":
    main()
