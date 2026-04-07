#!/usr/bin/env python
from __future__ import annotations

import json
import os
import socket
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


API_BASE = "https://api.sharebook.com.br/api"
SSL_CONTEXT = ssl._create_unverified_context()
TOKEN_ENV_VAR = "SHAREBOOK_PROD_ACCESS_TOKEN"


def load_env(repo_root: Path) -> dict[str, str]:
    env_path = repo_root / ".env"
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def save_env_value(repo_root: Path, key: str, value: str) -> None:
    env_path = repo_root / ".env"
    lines = env_path.read_text(encoding="utf-8").splitlines()
    updated = False
    new_lines: list[str] = []
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        if new_lines and new_lines[-1] != "":
            new_lines.append("")
        new_lines.append(f"{key}={value}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


class ApiHttpError(RuntimeError):
    def __init__(self, code: int, url: str, detail: str) -> None:
        super().__init__(f"{code} {url}\n{detail}")
        self.code = code
        self.url = url
        self.detail = detail


def request_json(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    allow_http_error_json: bool = False,
) -> Any:
    encoded = None
    final_headers = {"Content-Type": "application/json"}
    if headers:
        final_headers.update(headers)
    if body is not None:
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=encoded, headers=final_headers, method=method)

    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=60, context=SSL_CONTEXT) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if allow_http_error_json:
                try:
                    return json.loads(detail)
                except json.JSONDecodeError:
                    pass
            raise ApiHttpError(exc.code, url, detail) from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            if attempt >= 2 or not _is_transient_network_error(exc):
                raise
            time.sleep(2 * (attempt + 1))


def _is_transient_network_error(exc: Exception) -> bool:
    message = str(exc).lower()
    transient_markers = [
        "timed out",
        "time out",
        "winerror 10053",
        "winerror 10054",
        "connection reset",
        "connection aborted",
        "software no computador host",
        "remote end closed connection",
    ]
    return any(marker in message for marker in transient_markers)


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def login(env_values: dict[str, str]) -> str:
    payload = {
        "Email": env_values.get("SHAREBOOK_PROD_USER") or os.environ.get("SHAREBOOK_PROD_USER"),
        "Password": env_values.get("SHAREBOOK_PROD_PASSWORD") or os.environ.get("SHAREBOOK_PROD_PASSWORD"),
    }
    for attempt in range(3):
        response = request_json(
            f"{API_BASE}/Account/Login/",
            method="POST",
            body=payload,
            headers={"x-requested-with": "web", "client-version": "v0.0.0"},
            allow_http_error_json=True,
        )
        if response["success"]:
            return response["value"]["accessToken"]

        messages = response.get("messages") or []
        blocked = any("Login bloqueado por 30 segundos" in message for message in messages)
        if blocked and attempt < 2:
            time.sleep(31)
            continue

        raise SystemExit(json.dumps(response, ensure_ascii=False, indent=2))

    raise SystemExit("Nao foi possivel autenticar na API do Sharebook.")


def get_token(
    env_values: dict[str, str],
    *,
    repo_root: Path | None = None,
    force_refresh: bool = False,
) -> str:
    if force_refresh:
        token = login(env_values)
        if repo_root is not None:
            save_env_value(repo_root, TOKEN_ENV_VAR, token)
        return token

    token = os.environ.get(TOKEN_ENV_VAR)
    if token:
        return token.strip()

    env_token = env_values.get(TOKEN_ENV_VAR)
    if env_token:
        return env_token.strip()

    token = login(env_values)
    if repo_root is not None:
        save_env_value(repo_root, TOKEN_ENV_VAR, token)
    return token
