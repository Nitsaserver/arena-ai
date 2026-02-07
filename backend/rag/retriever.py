class Retriever:
    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.store = vector_store

    def retrieve(self, query: str, k=5):
        q_embedding = self.embedder.embed([query])[0]
        return self.store.search(q_embedding, k)
