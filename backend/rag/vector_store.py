import chromadb
from config import CHROMA_PERSIST_PATH, CHROMA_COLLECTION_NAME

_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)
        _collection = _client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

def add_bug(bug_id: str, embedding: list, metadata: dict, document: str):
    get_collection().upsert(ids=[bug_id], embeddings=[embedding], metadatas=[metadata], documents=[document])

def search_similar(embedding: list, n_results: int = 3) -> dict:
    col = get_collection()
    count = col.count()
    if count == 0:
        return {"ids": [[]], "distances": [[]], "metadatas": [[]], "documents": [[]]}
    return col.query(query_embeddings=[embedding], n_results=min(n_results, count), include=["metadatas", "documents", "distances"])

def get_bug_count() -> int:
    return get_collection().count()

def get_all() -> list:
    col = get_collection()
    if col.count() == 0:
        return []
    results = col.get(include=["metadatas", "documents"])
    return [{"id": doc_id, "document": results["documents"][i], "metadata": results["metadatas"][i]} for i, doc_id in enumerate(results["ids"])]
