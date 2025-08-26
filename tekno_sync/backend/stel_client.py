import time
import requests


class StelClient:
    def __init__(self, base_url: str, api_key: str, page_size: int = 200, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.page_size = page_size
        self.timeout = timeout

    def list_clients_page(self, page: int):
        url = f"{self.base_url}/clients"
        params = {"page": page, "limit": self.page_size, "apikey": self.api_key}
        resp = requests.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def list_clients_incremental(self, since_iso: str):
        page = 1
        while True:
            items = self.list_clients_page(page)
            if not items:
                break
            for item in items:
                yield item
            page += 1
            time.sleep(0.2)
