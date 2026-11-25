import os
import json
import httpx
from google import genai
from google.genai import types
from dotenv import load_dotenv
from app.schemas import IncidentReport

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_with_llm(service_name: str, log_text: str, retrieved_runbooks: list[dict]) -> dict:
    if retrieved_runbooks:
        context_str = "\n".join(
            [f"- [{rb['category']}] {rb['title']} (Match: {rb['similarity']}): {rb['content']}" for rb in retrieved_runbooks]
        )
    else:
        context_str = "No historical runbooks available."

    prompt = f"""
    You are an autonomous SRE & Security Operations AI Agent.
    Analyze the incoming production log, correlate it with the retrieved historical runbooks, 
    and output a structured incident triage report.

    Target Service: {service_name}
    Raw Log Trace: {log_text}

    Retrieved Knowledge Base (Runbooks):
    {context_str}

    Rules:
    - Classify strictly into Security, SRE/DevOps, Database, or Application.
    - Assign severity: CRITICAL (outage/breach), HIGH (degraded/attack attempt), MEDIUM (warning), LOW (info).
    - Provide concrete, executable remediation steps.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=IncidentReport,
            temperature=0.1,
        ),
    )

    report = json.loads(response.text)
    report["matched_runbooks"] = [rb["title"] for rb in retrieved_runbooks]
    report["auto_alert_triggered"] = report["severity"] in ["HIGH", "CRITICAL"]
    return report

async def trigger_automated_alert(service_name: str, report: dict):
    webhook_url = os.getenv("ALERT_WEBHOOK_URL")
    alert_payload = {
        "alert": f"[{report['severity']}] AutoOps AI Incident in {service_name}",
        "category": report["category"],
        "root_cause": report["root_cause"],
        "remediation": report["remediation_steps"]
    }
    
    print(f"\n[AUTO-REMEDIATION ALERT TRIGGERED] -> {json.dumps(alert_payload, indent=2)}\n")
    
    if webhook_url:
        async with httpx.AsyncClient() as http_client:
            try:
                await http_client.post(webhook_url, json=alert_payload, timeout=5.0)
            except Exception as e:
                print(f"Webhook delivery warning: {e}")
