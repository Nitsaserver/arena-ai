import faiss
import numpy as np


class VectorStore:
    def __init__(self, dim: int):
        # Inner Product index (used for cosine similarity after normalization)
        self.index = faiss.IndexFlatIP(dim)
        self.documents = []

    def add(self, embeddings, documents):
        """
        embeddings: List[List[float]]
        documents: List[str]
        """
        vectors = np.array(embeddings).astype("float32")

        # 🔑 Normalize for cosine similarity
        faiss.normalize_L2(vectors)

        self.index.add(vectors)
        self.documents.extend(documents)

    def search(self, query_embedding, k=5):
        if self.index.ntotal == 0:
            return []

        query_vector = np.array([query_embedding]).astype("float32")
        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(query_vector, k)

        seen = set()
        results = []

        for idx in indices[0]:
            if idx == -1:
                continue
            if idx not in seen:
                seen.add(idx)
                results.append(self.documents[idx])

        return results
