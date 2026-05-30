# EdTech NLP-to-SQL Backend

AI-powered backend service that converts natural language questions into SQL queries and safely executes them on an EdTech database.

## Architecture

```
app/
├── main.py       # FastAPI entry point
├── api/          # API routes (POST /query, GET /stats)
├── services/     # NLP-to-SQL, validation, analytics
├── database/     # SQLAlchemy engine and session
├── models/       # ORM models (Student, Course, Enrollment)
└── schemas/      # Pydantic request/response models
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variable:
```bash
copy .env.example .env
# Edit .env with your Groq API key
```

3. Seed database:
```bash
python seed.py
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### POST /query
```json
{
  "question": "How many students enrolled in Python courses in 2024?"
}
```
Response:
```json
{
  "question": "...",
  "generated_sql": "SELECT COUNT(*) FROM enrollments e JOIN courses c ON e.course_id = c.id WHERE c.name LIKE '%Python%' AND strftime('%Y', e.enrolled_at) = '2024'",
  "result": [{"count": 5}],
  "execution_time_ms": 12.5
}
```

### GET /stats
```json
{
  "total_queries": 10,
  "common_keywords": [{"keyword": "students", "count": 5}],
  "slowest_query": {...},
  "queries": [...]
}
```

## NLP-to-SQL Approach

1. Validate natural language question for malicious keywords
2. Send to Groq LLaMA3-8b-8192 with detailed schema context
3. LLM returns SELECT-only SQL
4. SQL validated against dangerous keywords
5. Execute via SQLAlchemy

## Security

- Two-layer validation (question + generated SQL)
- Blocks DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, CREATE, EXEC, GRANT, REVOKE
- Only SELECT queries allowed
- HTTP 400 for malicious prompts

## Limitations

- Requires Groq API key (uses fallback queries if not set)
- In-memory analytics (resets on restart)
- SQLite for simplicity (not production scale)

## Docker

Build:
```bash
docker build -t edtech-nlp2sql .
```

Run:
```bash
docker run -p 8000:8000 -e GROQ_API_KEY=your_key edtech-nlp2sql
```

## Kubernetes

Apply pod configuration:
```bash
kubectl apply -f kubernetes/pod.yaml
```

## Testing

Run tests:
```bash
pytest tests/ -v
```