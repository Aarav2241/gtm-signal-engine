import sqlite3
import os
from config.settings import DB_PATH

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create signals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_url TEXT,
            trigger_type TEXT,
            raw_text TEXT,
            extracted_data TEXT,
            matched_account TEXT,
            confidence_score TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create accounts table (local cache)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            data TEXT
        )
    ''')
    
    # Create PE snapshots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pe_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fund_name TEXT,
            companies TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Team snapshots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT,
            content_hash TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create processed URLs table to avoid duplicate processing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_urls (
            url TEXT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create company profiles table for enriched firmographic data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            domain TEXT,
            employee_count TEXT,
            revenue_range TEXT,
            sector TEXT,
            founded_year TEXT,
            funding_raised TEXT,
            icp_score INTEGER,
            enrichment_source TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
