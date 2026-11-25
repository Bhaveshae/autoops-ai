import os
import json
import psycopg
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection(register_vec: bool = True):
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    if register_vec:
        register_vector(conn)
    return conn

def init_db():
    # Pehle extension create kar bina register_vector call kiye
    conn = get_db_connection(register_vec=False)
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()
    
    # Ab vector type register kar aur tables bana
    register_vector(conn)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS runbooks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding vector(768),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS incident_audit_logs (
            id SERIAL PRIMARY KEY,
            service_name TEXT NOT NULL,
            raw_log TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            root_cause TEXT NOT NULL,
            remediation_steps JSONB NOT NULL,
            auto_alert_triggered BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def log_incident(service_name: str, raw_log: str, report: dict) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO incident_audit_logs 
        (service_name, raw_log, category, severity, root_cause, remediation_steps, auto_alert_triggered)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        service_name,
        raw_log,
        report["category"],
        report["severity"],
        report["root_cause"],
        json.dumps(report["remediation_steps"]),
        report["auto_alert_triggered"]
    ))
    incident_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return incident_id

def fetch_recent_incidents(limit: int = 10):
    conn = get_db_connection()
    cur = conn.cursor(row_factory=dict_row)
    cur.execute("""
        SELECT id, service_name, category, severity, root_cause, auto_alert_triggered, created_at
        FROM incident_audit_logs
        ORDER BY created_at DESC
        LIMIT %s;
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows