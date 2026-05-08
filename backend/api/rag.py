from fastapi import APIRouter
from pydantic import BaseModel
from backend.rag.service import rag_service

router = APIRouter(
    prefix="/api",
    tags=["RAG"]
)

class RAGQuery(BaseModel):
    question: str

class RAGResponse(BaseModel):
    answer: str

@router.post("/explain")
def explain_rag(q: RAGQuery):
    try:
        print("🔥 RAG endpoint hit")
        answer = rag_service.explain(q.question)
        print("✅ RAG answer generated")
        return {"answer": answer}
    except Exception as e:
        print("❌ RAG ERROR:", e)
        raise
