#!/bin/bash
set -e

# Ruta raíz del proyecto
ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚀 Iniciando TeknoCopy Sync..."

# 1) Activar entorno virtual
if [ -f "$ROOT/.venv/bin/activate" ]; then
  source "$ROOT/.venv/bin/activate"
  echo "✔️  Virtualenv activado"
else
  echo "❌ No existe .venv. Crea uno con: python3 -m venv .venv"
  exit 1
fi

# 2) Levantar backend (FastAPI)
echo "▶️  Iniciando backend en http://localhost:8000 ..."
cd "$ROOT"
# lanza uvicorn en segundo plano
uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 3) Levantar frontend (Vite)
echo "▶️  Iniciando frontend en http://localhost:5173 ..."
cd "$ROOT/frontend"
npm install --no-audit --no-fund
npm run dev -- --host & 
FRONTEND_PID=$!

# 4) Cleanup al salir
trap "echo '🛑 Deteniendo...'; kill $BACKEND_PID $FRONTEND_PID" SIGINT SIGTERM

# Esperar ambos procesos
wait
