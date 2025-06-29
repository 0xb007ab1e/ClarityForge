import os
import requests
from typing import List

def _hf_request(model_id: str, data: dict, retries=3, delay=1):
    """Make a request to the Hugging Face API with retry logic."""
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    hf_token = os.environ.get("HUGGINGFACE_API_TOKEN")
    if not hf_token:
        raise ValueError("HUGGINGFACE_API_TOKEN environment variable not set")
    headers = {"Authorization": f"Bearer {hf_token}"}
    for i in range(retries):
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        print(f"Request failed with status {response.status_code}, retrying in {delay}s...")
        # time.sleep(delay)  <- This is removed
    response.raise_for_status()


def generate_response(context: str) -> str:
    """Generates a response using the hosted google/flan-t5-base model."""
    data = _hf_request("google/flan-t5-base", {"inputs": context})
    # API returns a list with dicts like {"generated_text": "..."}
    return data[0]["generated_text"]


def classify(text: str) -> List[str]:
    candidate_labels = ["tech support", "billing", "sales"]
    data = _hf_request(
        "facebook/bart-large-mnli",
        {"inputs": text, "parameters": {"candidate_labels": candidate_labels}}
    )
    # API returns {"labels": [...], "scores": [...]}
    return [lbl for lbl, score in zip(data["labels"], data["scores"]) if score > 0.5]

