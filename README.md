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

## Docker Compose

```bash
docker compose up --build
```
