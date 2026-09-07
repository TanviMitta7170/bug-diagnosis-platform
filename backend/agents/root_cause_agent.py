import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

SYSTEM_PROMPT = """You are a Root Cause Analysis Agent for a software bug diagnosis platform.
Given a bug report, log analysis output, and similar historical bugs, reason about the probable root cause.
Respond ONLY with a valid JSON object, no markdown, no explanation.

{
  "primary_cause": "most likely root cause in 1-2 sentences",
  "confidence": "High" | "Medium" | "Low",
  "confidence_score": 0-100,
  "supporting_evidence": "what supports this conclusion",
  "secondary_hypothesis": "alternative cause or null",
  "affected_subsystem": "which part of the system is responsible"
}"""

async def run(input_data: dict) -> dict:
    client       = Groq(api_key=GROQ_API_KEY)
    log_analysis = input_data.get("log_analysis", {})
    kb_context   = ""
    for i, bug in enumerate(input_data.get("similar_bugs", [])[:3], 1):
        kb_context += f"\n[{i}] {bug.get('title','')}\n    Root Cause: {bug.get('root_cause','')}\n    Resolution: {bug.get('resolution','')}\n"
    log_summary = ""
    if log_analysis:
        log_summary = f"\nException: {log_analysis.get('exception_type','Unknown')}\nFailure Point: {log_analysis.get('failure_point','Unknown')}\nSignal: {log_analysis.get('diagnostic_signal','')}\n"
    content  = f"{SYSTEM_PROMPT}\n\n{input_data.get('log','')}\n{log_summary}"
    if kb_context:
        content += f"\nHistorical similar bugs:\n{kb_context}"
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