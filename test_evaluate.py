from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert "model_version" in response.json()

def test_evaluate_fit():
    payload = {
        "resume_text": "I have experience with Django, Python, and SQL databases.",
        "job_description": "We are hiring developers skilled in Python, Node.js, and Docker."
    }

    response = client.post("/evaluate-fit", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "fit_score" in data
    assert "verdict" in data
    assert "matched_skills" in data
    assert "missing_skills" in data
    assert "recommended_learning_track" in data
    assert "status" in data
