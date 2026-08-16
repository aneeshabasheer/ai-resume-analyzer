# nlp_parser.py
import spacy
from spacy.matcher import PhraseMatcher

try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

SKILL_DATABASE = [
    "Python", "Django", "Flask", "React", "Node.js", "JavaScript", "JS",
    "HTML", "HTML5", "CSS", "CSS3", "PostgreSQL", "MySQL", "SQL", "MongoDB", "AWS", 
    "Docker", "Git", "GitHub", "REST API", "Communication", "Problem Solving", "Teamwork",
    "C", "C++", "Java", "OOPs", "B.Tech", "M.Tech", "BCA", "MCA",
]

def extract_skills_with_spacy(text):
    if not text or len(str(text).strip()) == 0:
        return []
        
    doc = nlp(str(text))
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER") # Case-insensitive matching
    
    patterns = [nlp.make_doc(skill) for skill in SKILL_DATABASE]
    matcher.add("SKILL_PATTERN", patterns)
    
    matches = matcher(doc)
    extracted_skills = set()
    
    for match_id, start, end in matches:
        span = doc[start:end]
        matched_text = span.text.strip().lower()
        
        for skill in SKILL_DATABASE:
            if skill.lower() == matched_text:
                extracted_skills.add(skill)
                
    return list(extracted_skills)