from pydantic import BaseModel, Field
from typing import List, Literal

class RunbookIn(BaseModel):
    title: str = Field(..., example="PostgreSQL Connection Pool Exhaustion")
    category: Literal["Security", "SRE/DevOps", "Database", "Application"]
    content: str = Field(..., example="Check active connections via pg_stat_activity. Restart PgBouncer or increase max_connections.")

class LogAnalysisRequest(BaseModel):
    service_name: str = Field(..., example="payment-gateway-service")
    log_text: str = Field(..., example="FATAL: remaining connection slots are reserved for non-replication superuser connections")

class IncidentReport(BaseModel):
    category: Literal["Security", "SRE/DevOps", "Database", "Application"]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    root_cause: str = Field(description="Concise technical root cause diagnosis")
    remediation_steps: List[str] = Field(description="Ordered, actionable commands or engineering steps to resolve the issue")
    matched_runbooks: List[str] = Field(default_factory=list, description="Titles of historical runbooks used for context")
    auto_alert_triggered: bool = Field(default=False, description="True if severity is HIGH or CRITICAL")
