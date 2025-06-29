import os, requests, json, typing as t

_API_URL = "https://api-inference.huggingface.co/models/"
_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
if not _TOKEN:
    raise RuntimeError("Set HUGGINGFACE_API_TOKEN environment variable.")

_HEADERS = {"Authorization": f"Bearer {_TOKEN}"}

def _hf_request(model: str, payload: dict) -> dict:
    response = requests.post(_API_URL + model, headers=_HEADERS, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

