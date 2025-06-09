import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fit_score_engine import evaluate_fit

class EvaluateRequest(BaseModel):
    resume_text: str
    job_description: str

class LearningTrack(BaseModel):
    skill: str
    steps: list[str]

class EvaluateResponse(BaseModel):
    fit_score: float
    verdict: str
    matched_skills: list[str]
    missing_skills: list[str]
    recommended_learning_track: list[LearningTrack]
    status: str

# Load JSON config
BASE_DIR = os.path.dirname(os.path.abspath(_file_))
with open(os.path.join(BASE_DIR, 'skills.json')) as f:
    SKILLS_DATA = json.load(f)

with open(os.path.join(BASE_DIR, 'learning_paths.json')) as f:
    LEARNING_PATHS = json.load(f)

app = FastAPI(title="Resume–Role Fit Evaluator")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/version")
async def version():
    return {"model_version": "1.0.0"}

@app.post("/evaluate-fit", response_model=EvaluateResponse)
async def evaluate_fit_endpoint(req: EvaluateRequest):
    try:
        result = evaluate_fit(
            resume_text=req.resume_text,
            job_description=req.job_description,
            skills_config=SKILLS_DATA,
            learning_paths=LEARNING_PATHS
        )
        return EvaluateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
