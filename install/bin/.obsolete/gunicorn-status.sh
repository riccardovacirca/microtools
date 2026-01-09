#!/bin/bash
# Show Gunicorn API Gateway status

# Load environment variables
[ -f /workspace/.env ] && . /workspace/.env

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "                         GUNICORN SERVER STATUS"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

if [ -f /tmp/gunicorn.pid ]; then
  PID=$(cat /tmp/gunicorn.pid)
  if ps -p $PID > /dev/null 2>&1; then
    STATUS="RUNNING"
    ICON="✓"
  else
    STATUS="STOPPED (stale PID)"
    ICON="✗"
  fi
else
  PIDS=$(pgrep -f "gunicorn.*main:app" 2>/dev/null)
  if [ -n "$PIDS" ]; then
    STATUS="RUNNING (no PID file)"
    ICON="✓"
    PID=$(echo "$PIDS" | head -1)
  else
    STATUS="STOPPED"
    ICON="✗"
  fi
fi

printf "%-20s %-15s\n" "STATUS" "[$ICON] $STATUS"

if [ "$STATUS" = "RUNNING" ] || [ "$STATUS" = "RUNNING (no PID file)" ]; then
  printf "%-20s %-15s\n" "PID" "$PID"
  printf "%-20s %-15s\n" "Port" "${GUNICORN_PORT:-8001}"
  printf "%-20s %-15s\n" "Host" "${GUNICORN_HOST:-127.0.0.1}"
  printf "%-20s %-15s\n" "Workers" "${THREAD_COUNT:-4}"

  # Show worker processes
  echo ""
  echo "Worker Processes:"
  echo "───────────────────────────────────────────────────────────────────────────"
  ps aux | grep "gunicorn.*main:app" | grep -v grep | awk '{printf "  PID %-8s CPU: %6s%%  MEM: %6s%%  %s\n", $2, $3, $4, substr($0, index($0,$11))}'

  # Test endpoint
  echo ""
  echo "Health Check:"
  echo "───────────────────────────────────────────────────────────────────────────"
  if curl -s -o /dev/null -w "%{http_code}" http://${GUNICORN_HOST:-127.0.0.1}:${GUNICORN_PORT:-8001}/api/status/health 2>/dev/null | grep -q "200"; then
    echo "  ✓ HTTP endpoint responding: http://${GUNICORN_HOST:-127.0.0.1}:${GUNICORN_PORT:-8001}/api/status/health"
  else
    echo "  ✗ HTTP endpoint not responding"
  fi
fi

echo ""
echo "Logs:"
echo "───────────────────────────────────────────────────────────────────────────"
echo "  Access: /workspace/logs/gunicorn-access.log"
echo "  Error:  /workspace/logs/gunicorn-error.log"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
