import os
import time
import requests

class StelClient:
    def __init__(self, base_url, api_key, page_size=200, timeout=30):
        self.base_url = str(base_url).rstrip("/")
        self.api_key = str(api_key).strip()
        self.page_size = int(page_size)
        self.timeout = int(timeout)
        self.auth_mode = os.getenv("STEL_AUTH_MODE", "apikey_query")  # apikey_query | apikey_header
        self.key_header = os.getenv("STEL_API_KEY_HEADER", "APIKEY")

    def _auth(self, params: dict, headers: dict):
        if self.auth_mode == "apikey_query":
            # STEL espera APIKEY en mayúsculas
            params["APIKEY"] = self.api_key
        else:
            if self.key_header.lower().startswith("authorization:apikey"):
                headers["Authorization"] = f"ApiKey {self.api_key}"
            elif self.key_header.lower().startswith("authorization:bearer"):
                headers["Authorization"] = f"Bearer {self.api_key}"
            else:
                headers[self.key_header] = self.api_key

    def list_clients_page(self, page: int):
        url = f"{self.base_url}/clients"
        params_base, headers = {"APIKEY": self.api_key}, {}
        items = None
        errors = []

        # Variantes de paginación
        for attempt in (
            {"page": page, "limit": self.page_size},                 # page/limit
            {},                                                      # sin paginación
            {"page-number": page, "items-per-page": self.page_size}  # otra convención
        ):
            params = {**params_base, **attempt}
            try:
                r = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                if r.status_code == 400:
                    errors.append(f"400 with params={attempt} body={r.text[:200]}")
                    continue
                r.raise_for_status()
                data = r.json()
                items = data if isinstance(data, list) else data.get("data", [])
                break
            except requests.HTTPError:
                errors.append(f"{r.status_code} {r.reason} with params={attempt} body={r.text[:200]}")
            except Exception as e:
                errors.append(str(e))

        if items is None:
            raise RuntimeError("STEL /clients failed. Tried variants:\n" + "\n".join(errors))

        return items

    def list_clients_incremental(self, since_iso: str | None = None):
        """Pagina todos los clientes. Si no hay paginación, devuelve todo en una llamada."""
        page = 1
        while True:
            items = self.list_clients_page(page)
            if not items:
                break
            for it in items:
                yield it
            if len(items) < self.page_size:
                break
            page += 1
            time.sleep(0.2)  # rate limit suave
