#!/bin/sh
# Start FastAPI backend in background and Next.js standalone server in foreground
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
exec node server.js
