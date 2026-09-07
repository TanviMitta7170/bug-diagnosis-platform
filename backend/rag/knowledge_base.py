import json
from rag.embedder import embed_text, embed_bug
from rag.vector_store import add_bug, search_similar, get_bug_count, get_all
from config import SEED_DATA_PATH

def ingest_bug(bug: dict) -> bool:
    try:
        combined  = embed_bug(bug)
        embedding = embed_text(combined)
        metadata  = {
            "id": bug.get("id", ""), "title": bug.get("title", ""),
            "severity": bug.get("severity", "Unknown"), "priority": bug.get("priority", "Unknown"),
            "component": bug.get("component", "Unknown"), "status": bug.get("status", "Unknown"),
            "resolution": bug.get("resolution", ""), "root_cause": bug.get("root_cause", ""),
        }
        add_bug(bug["id"], embedding, metadata, combined)
        return True
    except Exception as e:
        print(f"Error ingesting {bug.get('id')}: {e}")
        return False

def seed_knowledge_base() -> int:
    if get_bug_count() > 0:
        return get_bug_count()
    with open(SEED_DATA_PATH, "r") as f:
        bugs = json.load(f)
    count = sum(1 for bug in bugs if ingest_bug(bug))
    print(f"Seeded {count} bugs into ChromaDB")
    return count

def retrieve_similar(query_text: str, n_results: int = 3) -> list:
    embedding = embed_text(query_text)
    results   = search_similar(embedding, n_results)
    similar   = []
    for i in range(len(results["ids"][0])):
        score = round((1 - results["distances"][0][i]) * 100, 1)
        meta  = results["metadatas"][0][i]
        similar.append({
            "id": results["ids"][0][i], "similarity": score,
            "title": meta.get("title", ""), "severity": meta.get("severity", ""),
            "component": meta.get("component", ""), "root_cause": meta.get("root_cause", ""),
            "resolution": meta.get("resolution", ""), "status": meta.get("status", ""),
        })
    return sorted(similar, key=lambda x: x["similarity"], reverse=True)

def add_resolved(bug: dict) -> bool:
    return ingest_bug(bug)

def list_all() -> list:
    return get_all()
