#!/bin/bash
echo "🚀 Starting KGBuilder RQ Worker..."

# Force load .env file
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "✅ Successfully loaded .env file"
    echo "   GEMINI_API_KEY loaded: ${GEMINI_API_KEY:0:8}..."
else
    echo "❌ .env file not found!"
    exit 1
fi

# Start the worker
rq worker \
  --url "$REDIS_URL" \
  --with-scheduler \
  --name "kgbuilder-worker-2" \
  -v