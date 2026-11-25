from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.database import init_db, log_incident, fetch_recent_incidents
from app.rag_engine import store_runbook, retrieve_relevant_runbooks
from app.llm_agent import analyze_with_llm, trigger_automated_alert
from app.schemas import RunbookIn, LogAnalysisRequest, IncidentReport

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="AutoOps AI — GenAI Log Analysis & Incident Automation Agent",
    description="RAG-powered SRE & Security incident triage engine using FastAPI, pgvector, and Gemini.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AutoOps AI"}

@app.post("/ingest-runbook")
def ingest_runbook(rb: RunbookIn):
    try:
        rb_id = store_runbook(rb.title, rb.category, rb.content)
        return {"status": "success", "runbook_id": rb_id, "title": rb.title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-log", response_model=IncidentReport)
async def analyze_log(req: LogAnalysisRequest):
    try:
        matches = retrieve_relevant_runbooks(req.log_text, top_k=2)
        report = analyze_with_llm(req.service_name, req.log_text, matches)
        log_incident(req.service_name, req.log_text, report)
        
        if report["auto_alert_triggered"]:
            await trigger_automated_alert(req.service_name, report)
            
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/incidents")
def get_incidents(limit: int = 10):
    return {"incidents": fetch_recent_incidents(limit)}
