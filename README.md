# Proyecto TeknoCopy

Sincronizador entre STEL, SQLite y Google Sheets con API FastAPI y frontend React.

## Endpoints principales

- `GET /api/health`: estado del servicio, base de datos, Google Sheets y `last_sync_at`.
- `GET /api/metrics`: métricas básicas de sincronización.
- `GET /api/clients/search?q=...&fields=name,email`: búsqueda rápida de clientes.

## Desarrollo local

```bash
./start.sh
```

El frontend lee la URL del backend desde `VITE_API_BASE`. Crea un archivo `frontend/.env.local` con:

```
VITE_API_BASE=http://localhost:8000
```

## Docker Compose

```bash
docker compose up --build
```

## CI/CD

Para que el workflow de GitHub Actions funcione correctamente es necesario definir los siguientes secrets en *Settings > Secrets and variables > Actions* del repositorio:

- `STEL_BASE_URL`
- `STEL_API_KEY`

Estos valores se inyectan durante la ejecución de las pruebas automatizadas.

## Pruebas

```bash
pytest -q
```

```bash
cd frontend
npm install
npm run lint
```
