import os
import requests
import json
from config.settings import APOLLO_API_KEY, APOLLO_BASE_URL, GROQ_API_KEY, GROQ_MODEL
from database.queries import get_company_profile, save_company_profile
from groq import Groq

def get_target_account_domain(company_name: str):
    try:
        with open('config/target_accounts.json', 'r') as f:
            accounts = json.load(f)
            for acc in accounts:
                if acc['name'].lower() == company_name.lower() or company_name.lower() in [a.lower() for a in acc.get('aliases', [])]:
                    return acc.get('domain')
    except Exception:
        pass
    # Cleaner heuristic fallback: keep alphanumeric characters intact (e.g., Manipal Hospitals -> manipalhospitals.com)
    clean_name = ''.join(e for e in company_name.lower() if e.isalnum())
    return f"{clean_name}.com" if clean_name else "unknown.com"

def calculate_icp_score(employee_count: str, revenue_range: str, funding_raised: str) -> int:
    score = 50 # Baseline
    # Adjust for employee count
    if any(k in str(employee_count) for k in ['50-', '100-', '200-', '500-', '1000']):
        score += 25
    elif any(k in str(employee_count) for k in ['11-', '20-', '30-']):
        score += 15
        
    # Adjust for funding
    if any(k in str(funding_raised).lower() for k in ['series a', 'series b', '$10m', '$20m', '100cr', '50cr']):
        score += 25
    elif str(funding_raised) != 'Unknown':
        score += 10
        
    return min(100, score)

def enrich_via_apollo(domain: str):
    if not APOLLO_API_KEY or APOLLO_API_KEY == "your_api_key_here":
        return None
    url = f"{APOLLO_BASE_URL}/organizations/enrich"
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'X-Api-Key': APOLLO_API_KEY
    }
    payload = {"domain": domain}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=5)
        if resp.status_code == 200:
            data = resp.json().get('organization', {})
            if data:
                return {
                    "domain": domain,
                    "employee_count": str(data.get('estimated_num_employees', '50-200')),
                    "revenue_range": str(data.get('annual_revenue_printed', '$10M - $50M')),
                    "sector": str(data.get('industry', 'Medical Devices / Healthcare')),
                    "founded_year": str(data.get('founded_year', '2015')),
                    "funding_raised": str(data.get('total_funding_printed', 'Series B')),
                    "enrichment_source": "Apollo API"
                }
    except Exception as e:
        print(f"Apollo API enrichment error for {domain}: {e}")
    return None

def enrich_via_llm_fallback(company_name: str):
    client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
    if not client:
        # Offline fallback without hardcoded fake metrics
        return {
            "domain": get_target_account_domain(company_name),
            "employee_count": "Unknown",
            "revenue_range": "Unknown",
            "sector": "Healthcare / MedTech",
            "founded_year": "Unknown",
            "funding_raised": "Unknown",
            "enrichment_source": "Offline (Unverified)"
        }
        
    prompt = f"""Provide estimated firmographic data for the Indian healthcare/medtech company '{company_name}'.
Return ONLY valid JSON with keys: "employee_count" (string range like '50-200'), "revenue_range" (string like '$10M-$50M'), "sector" (string), "founded_year" (string), "funding_raised" (string like 'Series A' or '$15M')."""
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=GROQ_MODEL,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        data = json.loads(res.choices[0].message.content)
        data["domain"] = get_target_account_domain(company_name)
        data["enrichment_source"] = "Groq LLM Fallback"
        return data
    except Exception as e:
        print(f"LLM fallback error: {e}")
        return {
            "domain": get_target_account_domain(company_name),
            "employee_count": "Unknown",
            "revenue_range": "Unknown",
            "sector": "Healthcare / MedTech",
            "founded_year": "Unknown",
            "funding_raised": "Unknown",
            "enrichment_source": "Offline (Unverified)"
        }

def enrich_company(company_name: str) -> dict:
    if not company_name or company_name in ["Unknown", "Mock Data", "None"]:
        return None
        
    # 1. Check SQLite Cache first (Zero cost, instantaneous)
    cached = get_company_profile(company_name)
    if cached:
        return cached
        
    domain = get_target_account_domain(company_name)
    
    # 2. Try Apollo API
    profile_data = enrich_via_apollo(domain)
    
    # 3. Fallback to LLM / Offline if Apollo fails or rate limits
    if not profile_data:
        profile_data = enrich_via_llm_fallback(company_name)
        
    profile_data["name"] = company_name
    profile_data["icp_score"] = calculate_icp_score(
        profile_data.get("employee_count"),
        profile_data.get("revenue_range"),
        profile_data.get("funding_raised")
    )
    
    # Save to DB cache
    save_company_profile(profile_data)
    return profile_data
