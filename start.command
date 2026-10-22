#!/bin/zsh
cd "${0:A:h}"
if [[ ! -x .venv/bin/python || ! -d app/node_modules ]]; then
  echo 'Dependencies missing. See README.md.'
  exit 1
fi
.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
studio_backend_pid=$!
trap 'kill "$studio_backend_pid" 2>/dev/null' EXIT INT TERM
cd app
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
