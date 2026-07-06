import json
from rapidfuzz import fuzz

def load_target_accounts():
    with open('config/target_accounts.json', 'r') as f:
        return json.load(f)

def match_account(company_name: str) -> dict:
    if not company_name or company_name == "Mock Data":
        return None
        
    accounts = load_target_accounts()
    best_match = None
    highest_score = 0
    
    for account in accounts:
        score = fuzz.ratio(company_name.lower(), account['name'].lower())
        
        for alias in account.get('aliases', []):
            alias_score = fuzz.ratio(company_name.lower(), alias.lower())
            score = max(score, alias_score)
            
        if score > highest_score:
            highest_score = score
            best_match = account
            
    if highest_score > 85:
        return best_match
    return None
