from fastapi import APIRouter
from models.bug_report import BugReport
from agents import triage_agent, log_agent, root_cause_agent, duplicate_agent, remediation_agent

router = APIRouter(prefix="/api", tags=["Analysis"])

@router.post("/analyze")
async def analyze_bug(bug: BugReport):
    results = {}
    errors  = {}
    data    = {
        "log":         bug.log,
        "component":   bug.component,
        "environment": bug.environment.value if bug.environment else "Production"
    }

    try:    results["triage"]       = await triage_agent.run(data)
    except Exception as e: errors["triage"] = str(e); results["triage"] = {"error": str(e)}

    try:    results["log_analysis"] = await log_agent.run(data)
    except Exception as e: errors["log_analysis"] = str(e); results["log_analysis"] = {"error": str(e)}

    try:    results["duplicates"]   = await duplicate_agent.run(data)
    except Exception as e: errors["duplicates"] = str(e); results["duplicates"] = {"error": str(e), "matches": [], "duplicates_found": False}

    try:
        results["root_cause"] = await root_cause_agent.run({
            **data,
            "log_analysis": results.get("log_analysis", {}),
            "similar_bugs": results.get("duplicates", {}).get("matches", [])
        })
    except Exception as e: errors["root_cause"] = str(e); results["root_cause"] = {"error": str(e)}

    try:
        results["remediation"] = await remediation_agent.run({
            **data,
            "triage":       results.get("triage", {}),
            "log_analysis": results.get("log_analysis", {}),
            "root_cause":   results.get("root_cause", {}),
            "duplicates":   results.get("duplicates", {})
        })
    except Exception as e: errors["remediation"] = str(e); results["remediation"] = {"error": str(e)}

    return {"status": "complete", "errors": errors if errors else None, "results": results}
