from pydantic import BaseModel, Field
from typing import List, Optional

class RegulatoryApproval(BaseModel):
    company_name: Optional[str] = Field(None, description="Clean, exact name of the company (max 5 words). Do NOT return 'Unknown' or full sentences.")
    device_name: Optional[str] = Field(None, description="Concise name of the medical device (max 8 words). Do NOT dump article paragraphs.")
    device_class: Optional[str] = Field(None, description="Class of the device if available")
    approval_date: Optional[str] = Field(None, description="Date of approval in YYYY-MM-DD or short format")

class FundingRound(BaseModel):
    company_name: Optional[str] = Field(None, description="Clean, exact name of the startup/company raising funds (max 5 words). Do NOT return 'Unknown'.")
    amount: Optional[str] = Field(None, description="Concise funding amount raised (e.g., '$10M', 'Rs 50Cr', 'Series A'). Max 5 words.")
    round_type: Optional[str] = Field(None, description="Series A, Seed, PE, etc.")
    investors: Optional[List[str]] = Field(default_factory=list, description="List of investor names (max 3 names)")
    sector: Optional[str] = Field(None, description="Short sector name (e.g., MedTech, Diagnostics)")

class PEPortfolioAdd(BaseModel):
    fund_name: Optional[str] = Field(None, description="Name of PE/VC fund")
    company_name: Optional[str] = Field(None, description="Clean, exact name of portfolio startup (max 5 words). Do NOT return 'Unknown'.")
    sector: Optional[str] = Field(None, description="Short sector name")
    description: Optional[str] = Field(None, description="1-sentence concise summary (max 15 words). Do NOT copy article body.")
    detected_date: Optional[str] = None

class LeadershipChange(BaseModel):
    company_name: Optional[str] = Field(None, description="Clean, exact name of company (max 5 words). Do NOT return 'Unknown'.")
    person_name: Optional[str] = Field(None, description="Clean name of person appointed (max 4 words)")
    new_role: Optional[str] = Field(None, description="Concise job title (e.g., Head of Sales, CEO). Max 6 words.")
    previous_company: Optional[str] = None

class ProductLaunch(BaseModel):
    company_name: Optional[str] = Field(None, description="Clean, exact name of company launching product (max 5 words). Do NOT return 'Unknown'.")
    product_name: Optional[str] = Field(None, description="Concise product name (max 6 words). Do NOT dump article text.")
    category: Optional[str] = None
    target_market: Optional[str] = None
    launch_date: Optional[str] = None

class HospitalExpansion(BaseModel):
    hospital_name: Optional[str] = Field(None, description="Clean, exact name of hospital chain (max 5 words). Do NOT return 'Unknown'.")
    location: Optional[str] = Field(None, description="City or state name (max 3 words)")
    bed_count: Optional[str] = None
    expansion_type: Optional[str] = Field(None, description="Concise expansion type (e.g., new facility, 200 beds). Max 5 words.")
    date: Optional[str] = None

class Signal(BaseModel):
    source_url: str
    trigger_type: str
    raw_text: str
    extracted_data: dict
    matched_account: Optional[str] = None
    confidence_score: str
    timestamp: str
