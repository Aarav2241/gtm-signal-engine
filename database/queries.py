import sqlite3
import json
from config.settings import DB_PATH

def get_conn():
    return sqlite3.connect(DB_PATH)

def insert_signal(signal: dict):
    ext_data = signal.get('extracted_data', {})
    if isinstance(ext_data, str):
        try: ext_data = json.loads(ext_data)
        except: ext_data = {}
        
    # Step 1: Discard if entity is Unknown, empty, null, or > 45 characters (prevents article dumping into entity name)
    entity_name = ext_data.get('company_name') or ext_data.get('hospital_name') or ext_data.get('fund_name') or ""
    entity_name = str(entity_name).strip()
    
    if not entity_name or entity_name.lower() in ["unknown", "unknown (offline)", "unknown company", "none", "null", "n/a", "mock data"] or len(entity_name) > 45:
        print(f"Discarding signal due to invalid entity name: '{entity_name}'")
        return
        
    # Step 2: Clean and truncate fields in extracted_data so no single detail dumps a full article
    cleaned_ext_data = {}
    for k, v in ext_data.items():
        if isinstance(v, str):
            clean_v = v.strip().replace('\n', ' ')
            if len(clean_v) > 120:
                clean_v = clean_v[:117] + "..."
            cleaned_ext_data[k] = clean_v
        else:
            cleaned_ext_data[k] = v
            
    # Step 3: Clean raw_text
    raw_text = str(signal.get('raw_text', '')).strip().replace('\n', ' ')
    if len(raw_text) > 200:
        raw_text = raw_text[:197] + "..."
        
    conn = get_conn()
    cursor = conn.cursor()
    # Avoid inserting duplicate signals
    cursor.execute('''
        SELECT id FROM signals WHERE trigger_type = ? AND source_url = ? AND raw_text = ?
    ''', (signal.get('trigger_type'), signal.get('source_url'), raw_text))
    if cursor.fetchone():
        conn.close()
        return
        
    cursor.execute('''
        INSERT INTO signals (source_url, trigger_type, raw_text, extracted_data, matched_account, confidence_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        signal.get('source_url'),
        signal.get('trigger_type'),
        raw_text,
        json.dumps(cleaned_ext_data),
        signal.get('matched_account'),
        signal.get('confidence_score')
    ))
    conn.commit()
    conn.close()

def get_all_signals():
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM signals ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def is_url_processed(url: str) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM processed_urls WHERE url = ?', (url,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_url_processed(url: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO processed_urls (url) VALUES (?)', (url,))
    conn.commit()
    conn.close()

def get_latest_pe_snapshot(fund_name: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT companies FROM pe_snapshots WHERE fund_name = ? ORDER BY timestamp DESC LIMIT 1', (fund_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return json.loads(result[0])
    return []

def insert_pe_snapshot(fund_name: str, companies: list):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pe_snapshots (fund_name, companies) VALUES (?, ?)', (fund_name, json.dumps(companies)))
    conn.commit()
    conn.close()

def get_company_profile(name: str):
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM company_profiles WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_company_profile(profile: dict):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO company_profiles (
            name, domain, employee_count, revenue_range, sector, founded_year, funding_raised, icp_score, enrichment_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            domain=excluded.domain,
            employee_count=excluded.employee_count,
            revenue_range=excluded.revenue_range,
            sector=excluded.sector,
            founded_year=excluded.founded_year,
            funding_raised=excluded.funding_raised,
            icp_score=excluded.icp_score,
            enrichment_source=excluded.enrichment_source
    ''', (
        profile.get('name'),
        profile.get('domain', ''),
        profile.get('employee_count', 'Unknown'),
        profile.get('revenue_range', 'Unknown'),
        profile.get('sector', 'Healthcare / MedTech'),
        profile.get('founded_year', 'Unknown'),
        profile.get('funding_raised', 'Unknown'),
        profile.get('icp_score', 50),
        profile.get('enrichment_source', 'Apollo')
    ))
    conn.commit()
    conn.close()

def get_all_company_profiles():
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM company_profiles')
    rows = cursor.fetchall()
    conn.close()
    return {row['name']: dict(row) for row in rows}
