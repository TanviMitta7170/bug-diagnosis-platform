import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

SYSTEM_PROMPT = """You are a Remediation Agent for a software bug diagnosis platform.
Given all previous agent outputs, recommend a specific actionable fix.
Respond ONLY with a valid JSON object, no markdown, no explanation.

{
  "fix_approach": "detailed fix description in 3-5 sentences",
  "fix_steps": ["Step 1: action", "Step 2: action", "Step 3: action"],
  "confidence": "High" | "Medium" | "Low",
  "estimated_effort": "< 1 hour" | "1-2 hours" | "half day" | "1-2 days" | "1 week+",
  "reviewer_suggestion": "which team or role should review",
  "prevention_tip": "how to prevent this class of bug in future",
  "grounded_in_history": true | false
}"""

async def run(input_data: dict) -> dict:
    client       = Groq(api_key=GROQ_API_KEY)
    triage       = input_data.get("triage", {})
    log_analysis = input_data.get("log_analysis", {})
    root_cause   = input_data.get("root_cause", {})
    duplicates   = input_data.get("duplicates", {})
    content = f"{SYSTEM_PROMPT}\n\nBug Report:\n{input_data.get('log','')}\n\nSeverity: {triage.get('severity','?')}, Priority: {triage.get('priority','?')}, Component: {triage.get('affected_component','?')}\nException: {log_analysis.get('exception_type','?')}, Failure Point: {log_analysis.get('failure_point','?')}\nRoot Cause: {root_cause.get('primary_cause','?')} (Confidence: {root_cause.get('confidence','?')})\n"
    for m in duplicates.get("matches", [])[:2]:
        content += f"\nHistorical resolution: {m.get('title','')}: {m.get('resolution','')}"
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": content}],
        temperature=0.2,
        max_tokens=800
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip())