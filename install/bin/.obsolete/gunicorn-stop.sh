#!/bin/bash
# Stop Gunicorn API Gateway
if [ -f /tmp/gunicorn.pid ]; then
  PID=$(cat /tmp/gunicorn.pid)
  if ps -p $PID > /dev/null 2>&1; then
    echo "Stopping Gunicorn (PID: $PID)..."
    kill $PID
    sleep 2
    if ps -p $PID > /dev/null 2>&1; then
      echo "Force killing Gunicorn..."
      kill -9 $PID
    fi
    rm -f /tmp/gunicorn.pid
    echo "Gunicorn stopped"
  else
    echo "Gunicorn not running (stale PID file)"
    rm -f /tmp/gunicorn.pid
  fi
else
  echo "Gunicorn PID file not found. Checking for running processes..."
  PIDS=$(pgrep -f "gunicorn.*main:app")
  if [ -n "$PIDS" ]; then
    echo "Found running Gunicorn processes: $PIDS"
    kill $PIDS
    echo "Gunicorn stopped"
  else
    echo "Gunicorn not running"
  fi
fi
