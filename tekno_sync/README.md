# Tekno Sync

## Prerrequisitos
- Python 3.11
- Node 20
- Archivo de Service Account de Google como `service_account.json`

## Setup
1. Copiar `.env.example` a `.env` y completar variables.
2. Colocar `service_account.json` en la raíz del proyecto.
3. Crear una hoja de cálculo con pestaña `Clients` y obtener `SHEETS_SPREADSHEET_ID`.

## Modo local
```bash
pip install -r requirements.txt
uvicorn backend.api:app --reload --port 8000
```

En otra terminal:
```bash
cd frontend
npm install
npm run dev
```

## Docker
```bash
docker compose up --build
```

## Prueba
- `GET http://localhost:8000/api/health`
- `GET http://localhost:8000/api/clients`
