import requests

OLLAMA_EMBED_URL = "http://host.docker.internal:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


class EmbeddingModel:
    def embed(self, text: str):
        response = requests.post(
            OLLAMA_EMBED_URL,
            json={
                "model": EMBED_MODEL,
                "prompt": text
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()["embedding"]
