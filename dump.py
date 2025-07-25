import requests
import json

TOON_API_PORT = 1547  # change if needed

response = requests.get(f"http://localhost:{TOON_API_PORT}/all.json", headers={
    "Authorization": "Bearer ttr-local-ha-",
    "User-Agent": "ttr-local-ha"
})

if response.status_code == 200:
    with open("all.json", "w", encoding="utf-8") as f:
        json.dump(response.json(), f, indent=2)
    print("✅ Saved all.json")
else:
    print(f"❌ Failed to fetch data: {response.status_code}")
