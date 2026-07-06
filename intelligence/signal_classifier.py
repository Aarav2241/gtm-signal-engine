def classify_signal_type(raw_text: str) -> str:
    text = raw_text.lower()
    if 'funding' in text or 'raises' in text or 'series' in text:
        return 'FundingRound'
    elif 'approval' in text or 'cdsco' in text or 'cleared' in text:
        return 'RegulatoryApproval'
    elif 'invested' in text or 'acquired' in text or 'portfolio' in text:
        return 'PEPortfolioAdd'
    elif 'appoints' in text or 'joins' in text or 'head of' in text:
        return 'LeadershipChange'
    elif 'launches' in text or 'introduces' in text:
        return 'ProductLaunch'
    elif 'hospital' in text and ('new' in text or 'expansion' in text or 'beds' in text):
        return 'HospitalExpansion'
    
    return 'Unknown'
