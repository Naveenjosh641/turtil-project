from skill_extractor import extract_skills

def evaluate_fit(resume_text, job_description, skills_config, learning_paths):
    resume_skills = extract_skills(resume_text, skills_config)
    job_skills = extract_skills(job_description, skills_config)

    matched = list(resume_skills & job_skills)
    missing = list(job_skills - resume_skills)

    fit_score = len(matched) / max(len(job_skills), 1)
    verdict = (
        "strong_fit" if fit_score >= 0.75 else
        "moderate_fit" if fit_score >= 0.4 else
        "weak_fit"
    )

    track = []
    for skill in missing:
        steps = learning_paths.get(skill.lower(), {}).get("steps", [])
        if steps:
            track.append({
                "skill": skill,
                "steps": steps[:4]
            })

    return {
        "fit_score": round(fit_score, 2),
        "verdict": verdict,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommended_learning_track": track,
        "status": "success"
    }
