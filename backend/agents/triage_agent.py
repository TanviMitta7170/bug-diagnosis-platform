import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

SYSTEM_PROMPT = """You are a Triage Agent for a software bug diagnosis platform.
Given a bug report or stack trace, classify it and return structured output.
Respond ONLY with a valid JSON object, no markdown, no explanation.

{
  "severity": "Critical" | "High" | "Medium" | "Low",
  "priority": "P1" | "P2" | "P3" | "P4",
  "affected_component": "string",
  "affected_users": "string",
  "confidence": 0-100,
  "reasoning": "2-3 sentences explaining the classification"
}

Critical=system down, High=major feature broken, Medium=degraded, Low=minor.
P1=fix immediately, P2=this sprint, P3=next sprint, P4=when possible.
confidence=how certain you are about the classification based on available information."""

async def run(input_data: dict) -> dict:
    client   = Groq(api_key=GROQ_API_KEY)
    prompt   = f"{SYSTEM_PROMPT}\n\nComponent: {input_data.get('component','Unknown')}\nEnvironment: {input_data.get('environment','Production')}\n\n{input_data.get('log','')}"
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip())