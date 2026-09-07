import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

SYSTEM_PROMPT = """You are a Bug Prediction Agent for a software bug diagnosis platform.
Given a git commit diff, analyze and predict bug risk.
Respond ONLY with a valid JSON object, no markdown, no explanation.

{
  "risk_level": "High" | "Medium" | "Low",
  "risk_score": 0-100,
  "risk_reasons": ["reason 1", "reason 2"],
  "vulnerable_areas": ["area 1", "area 2"],
  "recommended_tests": ["test 1", "test 2"],
  "summary": "2-3 sentence risk summary"
}"""

async def run(input_data: dict) -> dict:
    client   = Groq(api_key=GROQ_API_KEY)
    content  = f"{SYSTEM_PROMPT}\n\nAuthor: {input_data.get('author','Unknown')}\nMessage: {input_data.get('commit_message','')}\n\n{input_data.get('commit_diff','')}"
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": content}],
        temperature=0.2,
        max_tokens=600
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip())
