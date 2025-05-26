from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Load skills.json or use default
if os.path.exists("skills.json"):
    with open("skills.json") as f:
        skill_keywords = json.load(f)
else:
    skill_keywords = ["python", "flask", "docker", "aws", "system design", "node.js", "mongodb"]

# Load learning_paths.json or use default
if os.path.exists("learning_paths.json"):
    with open("learning_paths.json") as f:
        learning_paths = json.load(f)
else:
    learning_paths = {
        "docker": {
            "steps": [
                "Understand containers vs virtual machines",
                "Install Docker CLI and Docker Desktop",
                "Write a Dockerfile for a simple app",
                "Build and run Docker containers locally"
            ]
        },
        "aws": {
            "steps": [
                "Understand cloud basics",
                "Explore AWS free tier services",
                "Deploy a project using EC2 and S3",
                "Set up basic IAM roles"
            ]
        }
    }

# Fit config
FIT_CUTOFFS = {
    "strong_fit": 0.75,
    "moderate_fit": 0.4
}

# Input schema
class FitRequest(BaseModel):
    resume_text: str
    job_description: str

# Output schema
class Step(BaseModel):
    skill: str
    steps: List[str]

class FitResponse(BaseModel):
    fit_score: float
    verdict: str
    matched_skills: List[str]
    missing_skills: List[str]
    recommended_learning_track: List[Step]
    status: str

@app.get("/")
def read_root():
    return {"message": "Resume–Role Fit Evaluator is running."}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"model_version": "1.0.0"}

@app.post("/evaluate-fit", response_model=FitResponse)
def evaluate_fit(payload: FitRequest):
    resume = payload.resume_text.lower()
    job = payload.job_description.lower()

    matched_skills = [skill for skill in skill_keywords if skill in resume and skill in job]
    missing_skills = [skill for skill in skill_keywords if skill in job and skill not in resume]

    # TF-IDF score
    vect = TfidfVectorizer()
    vectors = vect.fit_transform([resume, job])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]

    if score >= FIT_CUTOFFS["strong_fit"]:
        verdict = "strong_fit"
    elif score >= FIT_CUTOFFS["moderate_fit"]:
        verdict = "moderate_fit"
    else:
        verdict = "weak_fit"

    # Recommend learning tracks
    track = []
    for skill in missing_skills:
        if skill in learning_paths:
            steps = learning_paths[skill]["steps"][:4]
            track.append(Step(skill=skill, steps=steps))

    return {
        "fit_score": round(score, 2),
        "verdict": verdict,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommended_learning_track": track,
        "status": "success"
    }
