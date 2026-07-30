import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def clean_skills_list(skills_input):
    """
    Parses a comma-separated skills string or list into a clean list of lowercased skills.
    """
    if not skills_input:
        return []
    if isinstance(skills_input, list):
        return [str(skill).strip().lower() for skill in skills_input if str(skill).strip()]
    return [skill.strip().lower() for skill in str(skills_input).split(',') if skill.strip()]


def calculate_match(resume_text, resume_skills, job_description, required_skills=None):
    """
    Matches resume text and skills against custom Job Description text.
    Returns:
        score (int 0-100)
        matched_skills (list)
        missing_skills (list)
    """
    # 1. Skill Overlap Matching
    job_skills = clean_skills_list(required_skills) if required_skills else []
    resume_skills_lower = [s.lower() for s in resume_skills]

    matched_skills = []
    missing_skills = []

    for js in job_skills:
        if any(js in rs or rs in js for rs in resume_skills_lower):
            matching_original = next((rs for rs in resume_skills if js in rs.lower() or rs.lower() in js), js)
            matched_skills.append(matching_original)
        else:
            missing_skills.append(js)

    if job_skills:
        skill_overlap_score = len(matched_skills) / len(job_skills)
    else:
        skill_overlap_score = 0.5  # Default fallback if explicit skills aren't listed

    # 2. Text Cosine Similarity using TF-IDF
    if not resume_text or not job_description:
        cosine_score = 0.0
    else:
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            cosine_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception as e:
            print(f"Error calculating Cosine Similarity: {e}")
            cosine_score = 0.0

    # 3. Hybrid Scoring Model (60% Skill Overlap + 40% Text Cosine Similarity)
    if job_skills:
        hybrid_score = (skill_overlap_score * 0.6) + (cosine_score * 0.4)
    else:
        # If no explicit skill list provided, rely purely on TF-IDF Cosine similarity
        hybrid_score = cosine_score

    final_score = int(np.clip(hybrid_score * 100, 0, 100))

    return final_score, matched_skills, missing_skills


def generate_suggestions(score, matched_skills, missing_skills):
    """
    Generates actionable bullet-point suggestions based on matched and missing skills.
    """
    suggestions = []

    if score >= 85:
        suggestions.append("Outstanding match! Your profile aligns exceptionally well with this position.")
        if matched_skills:
            suggestions.append("Highlight your projects involving: " + ", ".join(matched_skills[:3]) + " in your resume summary.")
        suggestions.append("Tailor your work experience section to mirror the specific action verbs in the job description.")
    elif score >= 60:
        suggestions.append("Good match! You have the core qualifications for this role.")
        if missing_skills:
            suggestions.append(f"Consider learning or highlighting: {', '.join(missing_skills[:3])} to raise your score.")
        if matched_skills:
            suggestions.append("Describe a project in your resume where you applied " + ", ".join(matched_skills[:2]))
    else:
        suggestions.append("Low match score. You have some skill gaps for this specific position.")
        if missing_skills:
            suggestions.append(f"Action Item: Learn {', '.join(missing_skills[:4])} and create mini-projects to list on your resume.")
        suggestions.append("Add more detail to your education and project descriptions to include industry keywords.")

    return "\n".join([f"• {s}" for s in suggestions])


def get_default_comparison_scores(resume_skills):
    """
    Generates comparison scores for standard roles (used for Dashboard Chart.js rendering).
    """
    roles = {
        'Python Developer': ['python', 'django', 'git', 'sql', 'html', 'css'],
        'Backend Developer': ['python', 'django', 'postgresql', 'apis', 'docker', 'git'],
        'Data Analyst': ['python', 'pandas', 'numpy', 'sql', 'data analysis', 'excel'],
        'Machine Learning Engineer': ['python', 'scikit-learn', 'machine learning', 'nlp', 'numpy', 'pandas']
    }

    scores = {}
    resume_skills_lower = [s.lower() for s in resume_skills]

    for role, req_skills in roles.items():
        matched = [s for s in req_skills if any(s in rs for rs in resume_skills_lower)]
        score = int((len(matched) / len(req_skills)) * 100) if req_skills else 0
        if 'python' in resume_skills_lower and score < 30:
            score += 15
        scores[role] = min(score, 100)

    return scores