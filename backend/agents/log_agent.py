import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

SYSTEM_PROMPT = """You are a Log Analysis Agent for a software bug diagnosis platform.
Parse the stack trace and identify key technical details.
Respond ONLY with a valid JSON object, no markdown, no explanation.

{
  "exception_type": "e.g. NullPointerException",
  "failure_point": "e.g. UserService.java:142",
  "failure_method": "method where failure occurred",
  "call_chain": ["list", "of", "methods"],
  "error_message": "the actual error message",
  "diagnostic_signal": "1-2 sentences describing what went wrong"
}

Use null for any field not present in the log."""

async def run(input_data: dict) -> dict:
    client   = Groq(api_key=GROQ_API_KEY)
    prompt   = f"{SYSTEM_PROMPT}\n\nStack Trace:\n{input_data.get('log','')}"
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=600
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip())
