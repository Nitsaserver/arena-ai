import requests

OLLAMA_EMBED_URL = "http://host.docker.internal:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


class EmbeddingModel:
    def embed(self, texts):
        response = requests.post(
            OLLAMA_EMBED_URL,
            json={
                "model": EMBED_MODEL,
                "input": texts if isinstance(texts, list) else [texts]
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        print(f"Ollama response keys: {data.keys()}")
        # Handle both "embedding" (single) and "embeddings" (multiple)
        if "embeddings" in data:
            return data["embeddings"]
        elif "embedding" in data:
            return [data["embedding"]]
        else:
            raise KeyError(f"Expected 'embeddings' or 'embedding' in response, got: {list(data.keys())}")
