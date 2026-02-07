from backend.rag.embeddings import EmbeddingModel
from backend.rag.vector_store import VectorStore
from backend.rag.retriever import Retriever
from backend.rag.llm import generate
from backend.rag.prompt import build_prompt

class RAGService:
    def __init__(self, embedder, retriever, llm):
        self.embedder = embedder
        self.retriever = retriever
        self.llm = llm

    def explain(self, question: str):
        context = self.retriever.retrieve(question)
        prompt = build_prompt(context, question)
        return self.llm.generate(prompt)

# Initialize components
_embedder = EmbeddingModel()
_vector_store = VectorStore(dim=384)  # MiniLM embedding size
_retriever = Retriever(_embedder, _vector_store)

class LLMWrapper:
    def generate(self, prompt: str) -> str:
        return generate(prompt)

_llm = LLMWrapper()

# ✅ THIS is what you were missing
rag_service = RAGService(
    embedder=_embedder,
    retriever=_retriever,
    llm=_llm
)
