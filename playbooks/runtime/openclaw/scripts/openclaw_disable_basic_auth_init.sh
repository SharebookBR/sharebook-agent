#!/usr/bin/env bash
set -u

# ShareBook/OpenClaw: remove nginx HTTP Basic Auth from the Coolify wrapper.
# Device identity/pairing remains the intended Control UI boundary. The wrapper
# generates nginx.conf after this init hook runs, so patch it from a short-lived
# watcher once the generated config is present.

CONF="/etc/nginx/conf.d/openclaw.conf"
MARKER="# sharebook-basic-auth-disabled"

(
  deadline=$((SECONDS + 180))

  while :; do
    if [ -s "$CONF" ] \
      && grep -q 'auth_basic_user_file' "$CONF" \
      && grep -q '^    location / {' "$CONF"; then
      break
    fi

    [ "$SECONDS" -ge "$deadline" ] && exit 0
    sleep 1
  done

  # The wrapper may restore the insecure-auth compatibility flag while
  # translating env vars. Normalize both Control UI bypasses after configure.js
  # has generated the persistent config and before normal operation settles.
  openclaw config unset gateway.controlUi.allowInsecureAuth >/dev/null 2>&1 || true
  openclaw config unset gateway.controlUi.dangerouslyDisableDeviceAuth >/dev/null 2>&1 || true

  grep -q "$MARKER" "$CONF" && exit 0

  tmp=$(mktemp)
  backup="${CONF}.sharebook-before-basic-auth-disable"

  awk -v marker="$MARKER" '
    BEGIN { print marker }
    $0 !~ /^[[:space:]]*auth_basic[[:space:]]/ &&
    $0 !~ /^[[:space:]]*auth_basic_user_file[[:space:]]/ { print }
  ' "$CONF" > "$tmp"

  cp -p "$CONF" "$backup"
  mv "$tmp" "$CONF"

  if nginx -t >/dev/null 2>&1; then
    nginx -s reload >/dev/null 2>&1 || true
    rm -f "$backup"
  else
    mv "$backup" "$CONF"
  fi
) &

exit 0
