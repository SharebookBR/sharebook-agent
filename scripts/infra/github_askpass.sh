#!/bin/sh
set -eu

ENV_FILE="${GITHUB_TOKEN_ENV_FILE:-/data/workspace/sharebook-agent/.env}"
TOKEN="$(sed -n 's/^GITHUB_PERSONAL_ACCESS_TOKEN=//p' "$ENV_FILE" | head -n 1)"

case "${1:-}" in
  *Username*)
    printf '%s\n' "${GITHUB_USERNAME:-x-access-token}"
    ;;
  *Password*)
    if [ -z "$TOKEN" ]; then
      echo "GITHUB_PERSONAL_ACCESS_TOKEN not found in $ENV_FILE" >&2
      exit 1
    fi
    printf '%s\n' "$TOKEN"
    ;;
  *)
    exit 1
    ;;
esac
