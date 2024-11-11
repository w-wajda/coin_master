#!/bin/bash
set -e

case $1 in
  api)
    echo "Starting api server"
    exec uvicorn --port 8000 --host 0.0.0.0 app.main:app --workers 3
  ;;

  dev)
    echo "Starting dev server"
    python app/main.py
  ;;

  *)
    exec "$@"
  ;;
esac

exit 0