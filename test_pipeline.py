import json
import httpx

BASE_URL = "http://127.0.0.1:8000"

def run_demo():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        print("1. Seeding SRE & Security Runbooks into pgvector...")
        with open("sample_data/runbooks.json", "r") as f:
            runbooks = json.load(f)
        for rb in runbooks:
            res = client.post("/ingest-runbook", json=rb)
            print("  ->", res.json())

        print("\n2. Testing Security Threat Log...")
        sec_log = {
            "service_name": "auth-service",
            "log_text": "WARN: 420 failed JWT login attempts in 60s from IP 185.220.101.4 on /api/v1/login"
        }
        res1 = client.post("/analyze-log", json=sec_log)
        print(json.dumps(res1.json(), indent=2))

        print("\n3. Testing Database Outage Log...")
        db_log = {
            "service_name": "ledger-core-api",
            "log_text": "FATAL: remaining connection slots are reserved for non-replication superuser connections"
        }
        res2 = client.post("/analyze-log", json=db_log)
        print(json.dumps(res2.json(), indent=2))

if __name__ == "__main__":
    run_demo()
