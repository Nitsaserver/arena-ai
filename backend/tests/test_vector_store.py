from backend.rag.vector_store import VectorStore

# Create vector store
vs = VectorStore(dim=768)

# Add a dummy embedding
vs.add(
    embeddings=[[1.0] * 768],
    documents=["test document"]
)

# Search
results = vs.search([1.0] * 768)

print(results)
