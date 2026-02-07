from fastapi import APIRouter

from backend.rag.service import rag_service

router = APIRouter()

@router.post("/explain")
def explain_arena(query: str):
    explanation = rag_service.explain(query)
    return {"explanation": explanation}
