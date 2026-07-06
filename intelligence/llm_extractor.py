import os
import json
from groq import Groq
from config.settings import GROQ_API_KEY, GROQ_MODEL
from models.schemas import FundingRound, RegulatoryApproval, PEPortfolioAdd, LeadershipChange, ProductLaunch, HospitalExpansion

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def classify_relevance(headline: str, snippet: str) -> bool:
    if not client:
        keywords = ['funding', 'raises', 'seed', 'series', 'startup', 'healthtech', 'medtech', 'approval', 'launch']
        text = (headline + " " + snippet).lower()
        return any(kw in text for kw in keywords)

    prompt = f"Is the following news relevant to Indian healthcare, medtech, medical devices, or healthcare startups? Reply ONLY with 'Yes' or 'No'.\n\nHeadline: {headline}\nSnippet: {snippet}"
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=GROQ_MODEL,
            temperature=0.1,
            max_tokens=10,
        )
        response = chat_completion.choices[0].message.content.strip().lower()
        return "yes" in response
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return False

def extract_signal(raw_text: str, trigger_type: str):
    schema_map = {
        "FundingRound": FundingRound,
        "RegulatoryApproval": RegulatoryApproval,
        "PEPortfolioAdd": PEPortfolioAdd,
        "LeadershipChange": LeadershipChange,
        "ProductLaunch": ProductLaunch,
        "HospitalExpansion": HospitalExpansion
    }
    
    schema_class = schema_map.get(trigger_type)
    if not schema_class:
        return None

    if not client:
        print("Offline extraction fallback: skipping signal")
        return None

    schema_json = json.dumps(schema_class.model_json_schema())
    prompt = f"""Extract structured data from the following text based on this JSON schema: {schema_json}.
CRITICAL CONSTRAINTS:
1. Every string field MUST be short and concise keywords or short titles (max 5-8 words). NEVER dump full sentences, article paragraphs, or HTML bodies into any field.
2. If the company or hospital name cannot be clearly identified, set company_name/hospital_name to null or empty string. Do NOT output the word 'Unknown'.
3. Return ONLY valid JSON matching the schema.

Text: {raw_text[:3000]}"""
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=GROQ_MODEL,
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        response_json = json.loads(chat_completion.choices[0].message.content)
        return schema_class(**response_json)
    except Exception as e:
        print(f"Error calling Groq API for extraction: {e}")
        return None

def extract_names_list(text: str, entity_type: str = "companies") -> list:
    if not client or not text:
        return []
    prompt = f"List all {entity_type} mentioned in the following webpage text. Return ONLY valid JSON in the format: {{\"items\": [\"name1\", \"name2\"]}}.\n\nText: {text[:5000]}"
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=GROQ_MODEL,
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        data = json.loads(res.choices[0].message.content)
        return data.get("items", [])
    except Exception as e:
        print(f"Error extracting {entity_type}: {e}")
        return []

def extract_articles_list(text: str) -> list:
    if not client or not text:
        return []
    prompt = f"Extract all relevant news articles, events, or regulatory approvals mentioned in the following webpage text. Return ONLY valid JSON in the format: {{\"articles\": [{{\"title\": \"...\", \"snippet\": \"...\"}}]}}.\n\nText: {text[:5000]}"
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=GROQ_MODEL,
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        data = json.loads(res.choices[0].message.content)
        return data.get("articles", [])
    except Exception as e:
        print(f"Error extracting articles: {e}")
        return []
