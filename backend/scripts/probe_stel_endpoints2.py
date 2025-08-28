# backend/scripts/probe_stel_endpoints.py

from backend.stel_client import StelClient
import json

def main():
    client = StelClient()

    # pide solo 1 factura de venta
    invoices = client.list_invoices(limit=1)
    print(json.dumps(invoices, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
