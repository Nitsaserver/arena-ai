SYSTEM_PROMPT = """
You are an AI cyber security analyst.
Explain system behavior using ONLY the provided context.
Be concise, factual, and structured.
"""

def build_prompt(context: list[str], question: str):
    joined_context = "\n---\n".join(context)
    return f"""
{SYSTEM_PROMPT}

Context:
{joined_context}

Question:
{question}

Answer:
"""
