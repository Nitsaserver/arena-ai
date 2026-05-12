import requests

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MODEL_NAME = "llama3.1:8b"


def generate(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 4096
            }
        },
        timeout=120
    )

    response.raise_for_status()
    return response.json()["response"]

