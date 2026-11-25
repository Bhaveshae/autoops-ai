# AutoOps AI — GenAI Log Analysis & Incident Automation Agent

An AI-powered incident triage, security anomaly detection, and automated remediation service built with **Python, FastAPI, PostgreSQL (`pgvector`), and Google Gemini**.

## Architecture

1. **Knowledge Base Ingestion (`/ingest-runbook`)**: Embeds SRE/Security runbooks using `text-embedding-004` and stores 768-dim vectors in PostgreSQL (`pgvector`).
2. **RAG Context Retrieval (`/analyze-log`)**: Performs cosine similarity search (`<=>`) against incoming error logs to surface relevant past runbooks.
3. **Structured LLM Triage**: Uses `gemini-2.5-flash` with Pydantic schema enforcement to classify severity (`LOW` to `CRITICAL`), domain (`Security`, `SRE/DevOps`, `Database`, `Application`), root cause, and remediation steps.
4. **Automated Alerting & Audit Trail**: Persists immutable incident logs in PostgreSQL and dispatches webhook alerts for `HIGH`/`CRITICAL` incidents.

## Quickstart

1. **Start PostgreSQL (`pgvector`)**:
   ```bash
   docker-compose up -d
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY inside .env
   ```

3. **Install Dependencies & Run API**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. **Seed Runbooks & Run Demo**:
   ```bash
   python test_pipeline.py
   ```
