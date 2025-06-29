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
    """Generates a response using the hosted gpt2 model."""
    data = _hf_request("gpt2", {"inputs": context, "parameters": {"max_length": 150}})
    # API returns a list with dicts like {"generated_text": "..."}
    if isinstance(data, list) and len(data) > 0:
        return data[0].get("generated_text", "No response generated")
    else:
        return "No response generated"


def classify(text: str) -> List[str]:
    """Simple classification using GPT-2 for now (fallback implementation)."""
    # For now, we'll use a simple heuristic-based classification
    # In a real implementation, you'd want to use a proper classification model
    text_lower = text.lower()
    labels = []
    
    if any(word in text_lower for word in ["tech", "technical", "bug", "error", "issue"]):
        labels.append("tech support")
    if any(word in text_lower for word in ["payment", "bill", "invoice", "cost", "price"]):
        labels.append("billing")
    if any(word in text_lower for word in ["buy", "purchase", "sale", "product", "demo"]):
        labels.append("sales")
    
    return labels

