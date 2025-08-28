#!/bin/sh
set -e

# Start backend
uvicorn backend.api:app --reload --port 8000 &
BACK_PID=$!

# Start frontend
cd frontend && npm run dev

wait $BACK_PID
