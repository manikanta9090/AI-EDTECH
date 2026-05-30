import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.database import engine
from app.models import Base

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_query_endpoint_success():
    response = client.post("/query", json={"question": "SELECT 1"})
    assert response.status_code == 200


def test_query_endpoint_validation_rejects_dangerous_sql():
    from app.services import validate_sql
    is_valid, msg = validate_sql("DELETE FROM students")
    assert is_valid == False
    assert "DELETE" in msg


def test_query_endpoint_validation_rejects_update():
    from app.services import validate_sql
    is_valid, msg = validate_sql("UPDATE students SET name='test'")
    assert is_valid == False


def test_query_endpoint_validation_accepts_select():
    from app.services import validate_sql
    is_valid, msg = validate_sql("SELECT * FROM students")
    assert is_valid == True


def test_stats_endpoint():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data
    assert "common_keywords" in data


def test_keyword_extraction():
    from app.services import extract_keywords
    keywords = extract_keywords("How many students enrolled in Python courses")
    assert "students" in keywords
    assert "python" in keywords
    assert "how" not in keywords


def test_question_validation_blocks_drop():
    from app.services import validate_question
    is_valid, msg = validate_question("DROP TABLE students")
    assert is_valid == False
    assert "safe SELECT-style" in msg


def test_question_validation_blocks_delete():
    from app.services import validate_question
    is_valid, msg = validate_question("DELETE FROM students")
    assert is_valid == False


def test_question_validation_blocks_update():
    from app.services import validate_question
    is_valid, msg = validate_question("UPDATE students SET grade='F'")
    assert is_valid == False


def test_question_validation_accepts_safe_question():
    from app.services import validate_question
    is_valid, msg = validate_question("How many students are in the database?")
    assert is_valid == True


def test_drop_table_returns_400():
    response = client.post("/query", json={"question": "DROP TABLE students"})
    assert response.status_code == 400