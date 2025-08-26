# smoke_test.py
import os, requests
from dotenv import load_dotenv

load_dotenv(".env")

BASE = os.getenv("STEL_BASE_URL", "").rstrip("/")
KEY = os.getenv("STEL_API_KEY", "").strip()

if not BASE or not KEY:
    raise SystemExit("❌ Falta configurar STEL_BASE_URL o STEL_API_KEY en .env")

print("🔎 Probar con BASE =", BASE)

def try_req(desc, headers=None, params=None):
    url = f"{BASE}/clients"
    p = {"page": 1, "limit": 1}
    if params: p.update(params)
    try:
        r = requests.get(url, headers=headers or {}, params=p, timeout=15)
        print(f"\n[{desc}] {r.status_code} {r.reason}")
        print("→ URL:", r.url)
        if r.text:
            print("→ BODY:", r.text[:200])
    except Exception as e:
        print(f"[{desc}] EXC:", e)

# Distintas variantes
try_req("query_apikey", params={"apikey": KEY})
try_req("hdr_APIKEY", headers={"APIKEY": KEY})
try_req("hdr_apikey", headers={"apikey": KEY})
try_req("hdr_X-API-KEY", headers={"X-API-KEY": KEY})
try_req("hdr_Authorization_ApiKey", headers={"Authorization": f"ApiKey {KEY}"})
try_req("hdr_Authorization_Bearer", headers={"Authorization": f"Bearer {KEY}"})
