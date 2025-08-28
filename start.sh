#!/bin/bash
# Inicia backend y frontend en modo desarrollo

# Backend
uvicorn backend.api:app --reload --port 8000 &
BACKEND_PID=$!

# Frontend
cd frontend
npm run dev &
FRONTEND_PID=$!

# Esperar procesos
wait $BACKEND_PID $FRONTEND_PID
