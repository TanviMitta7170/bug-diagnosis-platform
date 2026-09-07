from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def embed_text(text: str) -> list:
    return get_model().encode(text, convert_to_numpy=True).tolist()

def embed_bug(bug: dict) -> str:
    parts = [bug.get("title", ""), bug.get("stack_trace", ""), bug.get("root_cause", ""), bug.get("component", "")]
    return " | ".join(p for p in parts if p)
