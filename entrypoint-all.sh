#!/bin/sh
set -e

MODE="$1"
if [ -z "$MODE" ]; then
  MODE="services"
else
  shift
fi

start_services() {
  # Analyzer on 5002
  (
    cd /app/presidio-analyzer
    PORT=5002 WORKERS="${WORKERS:-1}" ./entrypoint.sh
  ) &
  echo ANALYZER_PID=$!

  # Anonymizer on 5001
  (
    cd /app/presidio-anonymizer
    PORT=5001 WORKERS="${WORKERS:-1}" ./entrypoint.sh
  ) &
  echo ANON_PID=$!

  # Image redactor on 5003
  (
    cd /app/presidio-image-redactor
    PORT=5003 WORKERS="${WORKERS:-1}" ./entrypoint.sh
  ) &
  echo IMG_PID=$!
}

if [ "$MODE" = "services" ]; then
  start_services
  # Keep container alive while services run
  wait
elif [ "$MODE" = "scan" ]; then
  start_services
  # Give analyzer some time to start before scanning
  sleep 15
  python /app/presidio-scan.py "$@"
  EXIT_CODE=$?
  # Stop background services gracefully
  kill "$ANALYZER_PID" "$ANON_PID" "$IMG_PID" 2>/dev/null || true
  wait || true
  exit "$EXIT_CODE"
else
  # Fallback: execute arbitrary command
  exec "$MODE" "$@"
fi


