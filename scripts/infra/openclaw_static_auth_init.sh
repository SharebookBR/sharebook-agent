#!/usr/bin/env bash
set -u

# ShareBook/OpenClaw: avoid browser Basic Auth prompts for Control UI assets.
# The wrapper generates nginx.conf after this init hook runs, so patch it from
# a short-lived watcher once the generated config is present.

CONF="/etc/nginx/conf.d/openclaw.conf"
MARKER="# sharebook-static-auth-exemptions"

(
  deadline=$((SECONDS + 180))

  while :; do
    if [ -s "$CONF" ] \
      && grep -q 'auth_basic_user_file' "$CONF" \
      && grep -q '^    location / {' "$CONF" \
      && grep -q 'proxy_set_header Authorization "Bearer ' "$CONF"; then
      break
    fi

    [ "$SECONDS" -ge "$deadline" ] && exit 0
    sleep 1
  done

  grep -q "$MARKER" "$CONF" && exit 0

  token=$(sed -n 's/.*proxy_set_header Authorization "Bearer \([^"]*\)";.*/\1/p' "$CONF" | head -n 1)
  [ -n "$token" ] || exit 0

  tmp=$(mktemp)
  backup="${CONF}.sharebook-before-static-auth"

  awk -v marker="$MARKER" -v token="$token" '
    !inserted && $0 ~ /^    location \/ \{$/ {
      print "    " marker
      print "    # Control UI static assets do not carry HTTP Basic Auth."
      print "    # Dynamic Gateway and browser routes remain protected below."
      print "    location ~ ^/(sw\\.js|manifest\\.webmanifest|control-ui-config\\.json|favicon\\.(ico|svg)|apple-touch-icon\\.png|assets/|avatar/|provider-icons/) {"
      print "        auth_basic off;"
      print "        proxy_pass http://127.0.0.1:18789;"
      print "        proxy_set_header Authorization \"Bearer " token "\";"
      print "        proxy_set_header Host $host;"
      print "        proxy_set_header X-Real-IP $remote_addr;"
      print "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;"
      print "        proxy_set_header X-Forwarded-Proto $scheme;"
      print "        proxy_http_version 1.1;"
      print "        proxy_read_timeout 86400s;"
      print "        proxy_send_timeout 86400s;"
      print "    }"
      print ""
      inserted=1
    }
    { print }
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
