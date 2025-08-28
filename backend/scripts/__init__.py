# backend/scripts/probe_stel_endpoints.py
from pprint import pprint
from backend.stel_client import StelClient
from backend.config import settings


def sample(title: str, data, n: int = 3):
    """Imprime una muestra parcial del resultado."""
    print(f"\n=== {title} (sample) ===")
    if isinstance(data, list):
        pprint(data[:n])
    elif isinstance(data, dict):
        # imprime solo claves principales para no inundar
        pprint({k: data[k] for k in list(data)[:10]})
    else:
        pprint(data)


def main():
    client = StelClient()

    # Probar endpoints básicos
    sample("Clients", client.list_clients(limit=5))
    sample("Products", client.list_products(limit=5))
    sample("Contacts", client.list_contacts(limit=5))
    sample("Invoices (sales)", client.list_invoices(limit=5))
    sample("Purchase Invoices", client.list_purchase_invoices(limit=5))
    sample("Sales Orders", client.list_sales_orders(limit=5))
    sample("Purchase Orders", client.list_purchase_orders(limit=5))

    # Ejemplo de paginación
    print("\n=== Clients paginated (first 2) ===")
    for i, row in enumerate(client.paginate("clients", limit=2)):
        pprint(row)
        if i >= 1:  # solo mostrar 2 para prueba
            break


if __name__ == "__main__":
    if not (settings.STEL_BASE_URL and settings.STEL_API_KEY):
        raise SystemExit(
            "❌ Falta configurar STEL_BASE_URL o STEL_API_KEY en .env o secrets"
        )
    main()
