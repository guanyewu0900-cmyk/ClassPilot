#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js 18 or later is required." >&2
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Add provider API keys to enable AI responses."
fi

exec node server.js
