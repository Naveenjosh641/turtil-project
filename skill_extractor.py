import re

def extract_skills(text, skills_config):
    text = text.lower()
    found = set()
    for canonical, variants in skills_config.items():
        for variant in variants:
            if re.search(r'\b' + re.escape(variant.lower()) + r'\b', text):
                found.add(canonical)
                break
    return found
