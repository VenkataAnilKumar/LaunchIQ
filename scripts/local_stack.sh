#!/usr/bin/env bash
# Manage the keyless local stack: redis (if needed), API, optional Celery worker, optional web.
#   scripts/local_stack.sh up [inline|celery]   start (default: inline = no worker process)
#   scripts/local_stack.sh down                 stop everything it started
#   scripts/local_stack.sh status
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .local
RUN=.local

start() { # name, command...
  local name=$1; shift
  setsid nohup "$@" > "$RUN/$name.log" 2>&1 < /dev/null &
  echo $! > "$RUN/$name.pid"
}

stop_one() {
  local f="$RUN/$1.pid"
  [ -f "$f" ] || return 0
  kill "$(cat "$f")" 2>/dev/null || true
  rm -f "$f"
}

case "${1:-status}" in
  up)
    mode="${2:-inline}"
    export TASK_RUNNER="$mode"
    # shellcheck disable=SC1091
    source scripts/local_env.sh
    if ! redis-cli ping >/dev/null 2>&1; then
      redis-server --daemonize yes --port 6379 --dir "${TMPDIR:-/tmp}" >/dev/null
    fi
    stop_one api; stop_one worker
    start api python3 -m uvicorn src.apps.api.main:app --port 8000
    if [ "$mode" = "celery" ]; then
      start worker python3 -m celery -A src.apps.api.workers.celery_app worker -l info --pool=solo
    fi
    for _ in $(seq 1 30); do
      curl -sf localhost:8000/api/v1/health >/dev/null && { echo "API up on :8000 (task runner: $mode)"; exit 0; }
      sleep 0.5
    done
    echo "API did not start; see $RUN/api.log" >&2; exit 1
    ;;
  down) stop_one api; stop_one worker; stop_one web; echo stopped ;;
  status)
    for n in api worker web; do
      if [ -f "$RUN/$n.pid" ] && kill -0 "$(cat "$RUN/$n.pid")" 2>/dev/null; then echo "$n: running"; else echo "$n: stopped"; fi
    done
    redis-cli ping 2>/dev/null | sed 's/^/redis: /' || echo "redis: down"
    ;;
  *) echo "usage: $0 up [inline|celery] | down | status" >&2; exit 2 ;;
esac
