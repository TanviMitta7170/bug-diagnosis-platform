import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, SEED_DATA_PATH

SYSTEM_PROMPT = """You are a Duplicate Detection Agent for a software bug diagnosis platform.
Given a new bug and historical bugs, identify which are most semantically similar.
Respond ONLY with a valid JSON object, no markdown, no explanation.

{
  "duplicates_found": true | false,
  "matches": [
    {
      "bug_id": "BUG-XXX",
      "title": "title of matched bug",
      "similarity_score": 0-100,
      "similarity_reason": "why this is similar",
      "resolution": "how it was fixed"
    }
  ],
  "recommendation": "whether to treat as duplicate or new bug"
}
Return at most 3 matches. Only include bugs with similarity score above 40."""


async def run(input_data: dict) -> dict:
    client = Groq(api_key=GROQ_API_KEY)
    with open(SEED_DATA_PATH, "r") as f:
        all_bugs = json.load(f)
    kb_text = "Historical bugs:\n"
    for bug in all_bugs:
        kb_text += f"\nID: {bug['id']}\nTitle: {bug['title']}\nStack Trace: {bug.get('stack_trace','')[:200]}\nRoot Cause: {bug.get('root_cause','')}\nResolution: {bug.get('resolution','')}\nComponent: {bug.get('component','')}\n---\n"
    prompt   = f"{SYSTEM_PROMPT}\n\nNew Bug:\nComponent: {input_data.get('component','Unknown')}\n{input_data.get('log','')}\n\n{kb_text}\nWhich historical bugs are most similar?"
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=800
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip())