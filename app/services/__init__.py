import time
import os
from openai import OpenAI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ANALYTICS = {
    "total_queries": 0,
    "slowest_query": None,
    "slowest_query_time": 0,
    "keyword_counts": {},
    "queries": []
}

_groq_api_key = os.getenv("GROQ_API_KEY", "")
client = OpenAI(
    api_key=_groq_api_key,
    base_url="https://api.groq.com/openai/v1"
) if _groq_api_key else None


def validate_question(question: str) -> tuple[bool, str]:
    question_upper = question.upper()
    dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE", "EXEC", "GRANT", "REVOKE"]
    for keyword in dangerous_keywords:
        if keyword in question_upper:
            return False, "Only safe SELECT-style analytical questions are allowed."
    return True, "Valid"


def validate_sql(sql: str) -> tuple[bool, str]:
    sql_upper = sql.upper().strip()
    dangerous_keywords = ["DELETE", "UPDATE", "DROP", "ALTER", "INSERT", "TRUNCATE", "CREATE"]
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False, f"Rejected: {keyword} queries are not allowed"
    if not sql_upper.startswith("SELECT"):
        return False, "Only SELECT queries are allowed"
    return True, "Valid"


def extract_keywords(question: str) -> list[str]:
    stop_words = {"how", "many", "the", "in", "a", "an", "is", "are", "was", "were", "to", "of", "and", "or", "for", "on", "with", "from"}
    words = question.lower().split()
    keywords = [w.strip(".,?!") for w in words if w.strip(".,?!") not in stop_words and len(w) > 2]
    return keywords


def generate_sql(question: str) -> str:
    if not client:
        return "SELECT * FROM students LIMIT 5"
    
    schema_info = """
Database Schema:
- students(id INTEGER PRIMARY KEY, name TEXT, grade TEXT, created_at TIMESTAMP)
- courses(id INTEGER PRIMARY KEY, name TEXT, category TEXT)
- enrollments(id INTEGER PRIMARY KEY, student_id INTEGER REFERENCES students(id), course_id INTEGER REFERENCES courses(id), enrolled_at TIMESTAMP)

Relationships:
- enrollments.student_id -> students.id (many enrollments per student)
- enrollments.course_id -> courses.id (many enrollments per course)

Examples:
Q: "How many students enrolled in Python courses in 2024?"
A: SELECT COUNT(*) FROM enrollments e JOIN courses c ON e.course_id = c.id WHERE c.name LIKE '%Python%' AND strftime('%Y', e.enrolled_at) = '2024'

Q: "List all courses"
A: SELECT * FROM courses

Q: "Show students with grade A"
A: SELECT * FROM students WHERE grade = 'A'

Q: "Count total enrollments"
A: SELECT COUNT(*) FROM enrollments

Q: "Find courses in Programming category"
A: SELECT * FROM courses WHERE category = 'Programming'
"""
    
    prompt = f"""Generate ONLY a valid SQLite SELECT query. No markdown, no explanation, just raw SQL.

{schema_info}

Question: {question}
SQL:"""
    
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0
        )
        sql = response.choices[0].message.content.strip()
        for line in sql.split('\n'):
            clean_line = line.strip().strip(';').strip()
            if clean_line and clean_line.upper().startswith("SELECT"):
                return clean_line
        return "SELECT * FROM students LIMIT 5"
    except Exception:
        return "SELECT * FROM students LIMIT 5"


def execute_sql(sql: str) -> tuple[list, float]:
    start_time = time.time()
    with Session(engine) as db:
        result = db.execute(text(sql))
        rows = [dict(row._mapping) for row in result.fetchall()]
    execution_time = (time.time() - start_time) * 1000
    return rows, execution_time


def track_query(question: str, sql: str, execution_time: float):
    ANALYTICS["total_queries"] += 1
    keywords = extract_keywords(question)
    for kw in keywords:
        ANALYTICS["keyword_counts"][kw] = ANALYTICS["keyword_counts"].get(kw, 0) + 1
    ANALYTICS["queries"].append({
        "question": question,
        "sql": sql,
        "execution_time_ms": execution_time
    })
    if execution_time > ANALYTICS["slowest_query_time"]:
        ANALYTICS["slowest_query_time"] = execution_time
        ANALYTICS["slowest_query"] = {
            "question": question,
            "sql": sql,
            "execution_time_ms": execution_time
        }


def process_query(question: str) -> tuple[str, list | dict | None, float]:
    is_valid, message = validate_question(question)
    if not is_valid:
        raise ValueError(message)
    sql = generate_sql(question)
    is_valid, message = validate_sql(sql)
    if not is_valid:
        raise ValueError(message)
    result, execution_time = execute_sql(sql)
    track_query(question, sql, execution_time)
    return sql, result, execution_time


def get_stats() -> dict:
    sorted_keywords = sorted(ANALYTICS["keyword_counts"].items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "total_queries": ANALYTICS["total_queries"] if ANALYTICS["total_queries"] else 0,
        "common_keywords": [{"keyword": k, "count": v} for k, v in sorted_keywords],
        "slowest_query": ANALYTICS["slowest_query"] if ANALYTICS["slowest_query"] else None,
        "queries": ANALYTICS["queries"][-10:] if ANALYTICS["queries"] else []
    }