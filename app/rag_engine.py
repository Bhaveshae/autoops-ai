import os
from google import genai
from dotenv import load_dotenv
from app.database import get_db_connection

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=text,
    )
    return response.embeddings[0].values

def store_runbook(title: str, category: str, content: str) -> int:
    embedding = generate_embedding(f"[{category}] {title}: {content}")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO runbooks (title, category, content, embedding)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """,
        (title, category, content, embedding)
    )
    rb_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return rb_id

def retrieve_relevant_runbooks(query_text: str, top_k: int = 2) -> list[dict]:
    query_embedding = generate_embedding(query_text)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT title, category, content, 1 - (embedding <=> %s::vector) AS similarity
        FROM runbooks
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (query_embedding, query_embedding, top_k)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return [
        {"title": r[0], "category": r[1], "content": r[2], "similarity": round(float(r[3]), 3)}
        for r in rows
    ]
