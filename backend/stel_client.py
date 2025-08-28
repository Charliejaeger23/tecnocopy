import os
import time
import requests


class StelClient:
    def __init__(self, base_url, api_key, page_size=200, timeout=30):
        self.base_url = str(base_url).rstrip("/")
        self.api_key = str(api_key).strip()
        self.page_size = int(page_size)
        self.timeout = int(timeout)
        self.auth_mode = os.getenv(
            "STEL_AUTH_MODE", "apikey_query"
        )  # apikey_query | apikey_header
        self.key_header = os.getenv("STEL_API_KEY_HEADER", "APIKEY")
        self.mode_file = ".stel_mode"
        self.mode = self._load_mode()

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

    def _load_mode(self):
        if os.path.exists(self.mode_file):
            with open(self.mode_file) as f:
                return f.read().strip()
        return ""

    def _save_mode(self, mode: str):
        with open(self.mode_file, "w") as f:
            f.write(mode)

    def _variants(self, page: int):
        return {
            "page_limit": {"page": page, "limit": self.page_size},
            "none": {},
            "page_number": {"page-number": page, "items-per-page": self.page_size},
        }

    def list_clients_page(self, page: int):
        url = f"{self.base_url}/clients"
        params_base, headers = {"APIKEY": self.api_key}, {}
        variants = self._variants(page)
        order = [self.mode] if self.mode in variants else []
        order += [k for k in variants if k != self.mode]
        items = None
        errors = []
        for key in order:
            attempt = variants[key]
            params = {**params_base, **attempt}
            for retries in range(5):
                try:
                    r = requests.get(
                        url, params=params, headers=headers, timeout=self.timeout
                    )
                    if r.status_code in (429, 500, 502, 503, 504):
                        time.sleep(2**retries)
                        continue
                    if r.status_code == 400:
                        errors.append(f"400 with params={attempt} body={r.text[:200]}")
                        break
                    r.raise_for_status()
                    data = r.json()
                    items = data if isinstance(data, list) else data.get("data", [])
                    self.mode = key
                    self._save_mode(key)
                    break
                except Exception as e:
                    errors.append(str(e))
                    time.sleep(2**retries)
                    continue
            if items is not None:
                break

        if items is None:
            raise RuntimeError(
                "STEL /clients failed. Tried variants:\n" + "\n".join(errors)
            )

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
