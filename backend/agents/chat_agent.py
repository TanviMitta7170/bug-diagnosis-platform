import json
from groq import Groq
from config import GROQ_API_KEY, SEED_DATA_PATH

async def run(input_data: dict) -> dict:
    client  = Groq(api_key=GROQ_API_KEY)
    context = input_data.get("context", "")
    message = input_data.get("message", "")
    source_ids = input_data.get("source_ids", [])

    system = """You are a bug diagnosis assistant. Answer the developer's question clearly and technically.
Always provide a full explanation, not just a bug ID.
If the answer is not found in the knowledge base context provided, answer from your general software engineering knowledge and say so."""

    if context:
        user_msg = f"Knowledge base context:\n{context}\n\nQuestion: {message}\n\nProvide a detailed answer explaining the bug, its cause, and how it was resolved. If this is not in the knowledge base, answer from general knowledge and mention that."
    else:
        user_msg = f"Question: {message}\n\nProvide a detailed technical answer from general software engineering knowledge."

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg}
        ],
        temperature=0.3,
        max_tokens=600
    )

    answer = response.choices[0].message.content.strip()

    # If not found in KB, add it as a new entry
    not_in_kb = not source_ids or "not in the knowledge base" in answer.lower() or "general knowledge" in answer.lower()
    if not_in_kb:
        try:
            with open(SEED_DATA_PATH, "r") as f:
                bugs = json.load(f)
            existing_ids = [b["id"] for b in bugs]
            new_id = f"BUG-{len(bugs)+1:03d}"
            while new_id in existing_ids:
                new_id = f"BUG-{int(new_id.split('-')[1])+1:03d}"
            new_bug = {
                "id": new_id,
                "title": message[:80],
                "stack_trace": "",
                "root_cause": "Added via Bug Chat — general knowledge query",
                "resolution": answer[:300],
                "severity": "Unknown",
                "priority": "Unknown",
                "component": "Unknown",
                "status": "Reference"
            }
            bugs.append(new_bug)
            with open(SEED_DATA_PATH, "w") as f:
                json.dump(bugs, f, indent=2)
            answer += f"\n\n[This query was not found in the knowledge base and has been saved as {new_id} for future reference.]"
        except Exception as e:
            print(f"KB save failed: {e}")

    return {"answer": answer, "sources": source_ids}