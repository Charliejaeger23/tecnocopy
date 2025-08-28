# Tekno Sync

## Requisitos
- Python 3.11
- Node 20
- Cuenta de servicio de Google (key JSON) **fuera del repo**  
  > Cárgala como secreto/var de entorno o monta el archivo localmente.

## Variables de entorno
Copia `.env.example` a `.env` y completa:
```
STEL_BASE_URL=
STEL_API_KEY=
SHEETS_SPREADSHEET_ID=
GOOGLE_APPLICATION_CREDENTIALS=./service_account.json   # (solo local)
```

Para el frontend, crea `frontend/.env.local`:
```
VITE_API_BASE=http://localhost:8000
```

## Ejecución en local

### Backend
```bash
python -m venv .venv && source .venv/bin/activate        # opcional pero recomendado
pip install -r backend/requirements.txt                  # <- ruta correcta
uvicorn backend.api:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm ci    # o npm install
npm run dev
```
Abre `http://localhost:5173`.

## Docker
```bash
docker compose up --build
```

## Smoke test rápido
```bash
# salud
curl -s http://localhost:8000/api/health | jq

# clientes (lista paginada)
curl -s "http://localhost:8000/api/clients?limit=5&offset=0" | jq

# búsqueda de clientes
curl -s "http://localhost:8000/api/clients/search?q=ACME&fields=name,email&limit=5&offset=0" | jq
```

## Buenas prácticas (evita dolores)
- **No** subas `service_account.json`. Manténlo fuera del repo y usa `GOOGLE_APPLICATION_CREDENTIALS` para apuntar al archivo local.
- Unifica dependencias en `backend/requirements.txt`. Elimina `requirements.txt` de la raíz si ya no se usa.
- Revisa que `.gitignore` incluya `.venv/`, `__pycache__/`, `frontend/node_modules/`, `frontend/dist/`, `.env*`, `tekno.db`, `service_account.json`.
