from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Load skills and learning paths
with open("skills.json") as f:
    skill_keywords = json.load(f)

with open("learning_paths.json") as f:
    learning_paths = json.load(f)

# Fit config (optional tuning)
FIT_CUTOFFS = {
    "strong_fit": 0.75,
    "moderate_fit": 0.4
}

# ----------------------------
# Request Model
# ----------------------------
class FitRequest(BaseModel):
    resume_text: str
    job_description: str

# ----------------------------
# Response Model
# ----------------------------
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

# ----------------------------
# Routes
# ----------------------------
@app.get("/")
def read_root():
    return {"message": "Resume–Role Fit Evaluator is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"model_version": "1.0.0"}

@app.post("/evaluate-fit", response_model=FitResponse)
def evaluate_fit(payload: FitRequest):
    resume = payload.resume_text.lower()
    job = payload.job_description.lower()

    # Extract skills by matching keywords
    matched_skills = []
    for skill in skill_keywords:
        if skill in resume and skill in job:
            matched_skills.append(skill)

    missing_skills = []
    for skill in skill_keywords:
        if skill in job and skill not in resume:
            missing_skills.append(skill)

    # TF-IDF fit score
    vect = TfidfVectorizer()
    vectors = vect.fit_transform([resume, job])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]

    # Verdict
    if score >= FIT_CUTOFFS["strong_fit"]:
        verdict = "strong_fit"
    elif score >= FIT_CUTOFFS["moderate_fit"]:
        verdict = "moderate_fit"
    else:
        verdict = "weak_fit"

    # Learning path
    track = []
    for skill in missing_skills:
        if skill in learning_paths:
            track.append(Step(skill=skill, steps=learning_paths[skill]["steps"][:4]))

    return {
        "fit_score": round(score, 2),
        "verdict": verdict,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommended_learning_track": track,
        "status": "success"
    }
