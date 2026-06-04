import requests


class HaClient:
    def __init__(self, url: str, token: str):
        self._url = url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self._url}/api/", headers=self._headers, timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def get_pending_updates(self) -> list:
        try:
            r = requests.get(f"{self._url}/api/states", headers=self._headers, timeout=5)
            if r.status_code != 200:
                return []
            return [
                s["attributes"].get("friendly_name", s["entity_id"])
                for s in r.json()
                if s.get("entity_id", "").startswith("update.") and s.get("state") == "on"
            ]
        except Exception:
            return []
