from fastapi import APIRouter
from pydantic import BaseModel

from backend.rag.service import rag_service

router = APIRouter()

class RAGQuery(BaseModel):
    question: str

class RAGResponse(BaseModel):
    answer: str

@router.post("/explain", response_model=RAGResponse)
def explain_rag(q: RAGQuery):
    answer = rag_service.explain(q.question)
    return {"answer": answer}
