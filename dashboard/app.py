import streamlit as st
import sys
import os
import json
import pandas as pd
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.queries import get_all_signals
from intelligence.matcher import match_account
from intelligence.enricher import enrich_company

st.set_page_config(page_title="GTM Signal Engine - Insight Tribe", layout="wide")

# Header & Styling
st.title("🚀 GTM Automated Signal Engine")
st.markdown("Monitor high-priority healthcare and medtech triggers to automate personalized outreach. Enriched live via **Apollo.io API** & **Groq AI**.")

signals = get_all_signals()

# Sidebar Filters
st.sidebar.header("🔍 Filter Signals")
trigger_types = list(set([s['trigger_type'] for s in signals])) if signals else []
selected_triggers = st.sidebar.multiselect(
    "Trigger Type", 
    trigger_types, 
    default=trigger_types,
    help="Select the signal types you want to view."
)

st.sidebar.markdown("---")
st.sidebar.header("🏢 Firmographic Filters")
min_icp_score = st.sidebar.slider("⭐ Minimum ICP Fit Score", 0, 100, 50, help="Filter out leads below this score.")
only_matched = st.sidebar.checkbox("🎯 Show Only CRM Target Accounts", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Live Lead Automation")
if st.sidebar.button("🚀 Trigger Cloud Scraper Now", use_container_width=True):
    gh_token = ""
    try:
        if "GITHUB_TOKEN" in st.secrets:
            gh_token = st.secrets["GITHUB_TOKEN"]
    except Exception:
        pass
    if not gh_token:
        gh_token = os.environ.get("GITHUB_TOKEN", "")
        
    if gh_token:
        with st.spinner("📡 Sending signal to wake up GitHub Cloud Scraper..."):
            url = "https://api.github.com/repos/Aarav2241/gtm-signal-engine/actions/workflows/daily_scrape.yml/dispatches"
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {gh_token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            try:
                resp = requests.post(url, headers=headers, json={"ref": "main"})
                if resp.status_code == 204:
                    st.sidebar.success("✅ Cloud scraper triggered! New leads will arrive in ~2 mins.")
                else:
                    st.sidebar.error(f"GitHub API Error: {resp.status_code}")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
    else:
        with st.spinner("🤖 Crawling live news feeds, PE portfolios, and CDSCO registries..."):
            try:
                import subprocess
                res = subprocess.run([sys.executable, "main.py", "scrape", "--all"], capture_output=True, text=True)
                if res.returncode == 0:
                    st.sidebar.success("✅ Live scrape completed successfully!")
                    st.rerun()
                else:
                    if "No module named 'crawl4ai'" in res.stderr or "No module named" in res.stderr:
                        st.sidebar.info("💡 You are on Streamlit Cloud! To enable 1-click cloud scraping from this button, add `GITHUB_TOKEN` (a GitHub Personal Access Token) to your Streamlit Secrets.")
                    else:
                        st.sidebar.error("Scrape error. Check server logs.")
            except Exception as e:
                st.sidebar.error(f"Execution error: {e}")

if signals:
    table_data = []
    
    with st.spinner("Enriching company firmographics via Apollo API / Cache..."):
        for s in signals:
            if s['trigger_type'] not in selected_triggers:
                continue
                
            try:
                ext_data = json.loads(s['extracted_data']) if isinstance(s['extracted_data'], str) else s['extracted_data']
            except:
                ext_data = {}
                
            entity_name = ext_data.get('company_name') or ext_data.get('hospital_name') or ext_data.get('fund_name') or ""
            entity_name = str(entity_name).strip()
            if not entity_name or entity_name.lower() in ["unknown", "unknown (offline)", "unknown company", "none", "null", "n/a", "mock data"] or len(entity_name) > 45:
                continue
            
            # Enrich company firmographics
            profile = enrich_company(entity_name)
            if not profile:
                profile = {"employee_count": "Unknown", "revenue_range": "Unknown", "sector": "MedTech", "icp_score": 50, "enrichment_source": "None"}
                
            # Filter by ICP score
            if profile.get('icp_score', 0) < min_icp_score:
                continue
                
            # Determine target match
            matched = s.get('matched_account')
            if not matched and entity_name:
                match_obj = match_account(entity_name)
                if match_obj:
                    matched = f"{match_obj['name']} (Tier {match_obj['tier']})"
            
            if only_matched and not matched:
                continue
                
            # Format key details (concise keywords only, discard full article dumps)
            details = []
            if s['trigger_type'] == 'FundingRound':
                if ext_data.get('amount'): details.append(f"Amount: {ext_data['amount']}")
                if ext_data.get('round_type'): details.append(f"Round: {ext_data['round_type']}")
                if ext_data.get('investors'): details.append(f"Investors: {', '.join(ext_data['investors']) if isinstance(ext_data['investors'], list) else ext_data['investors']}")
            elif s['trigger_type'] == 'RegulatoryApproval':
                if ext_data.get('device_name'): details.append(f"Device: {ext_data['device_name']}")
                if ext_data.get('approval_date'): details.append(f"Date: {ext_data['approval_date']}")
            elif s['trigger_type'] == 'PEPortfolioAdd':
                if ext_data.get('company_name'): details.append(f"Added: {ext_data['company_name']}")
                if ext_data.get('sector'): details.append(f"Sector: {ext_data['sector']}")
            elif s['trigger_type'] == 'HospitalExpansion':
                if ext_data.get('location'): details.append(f"Location: {ext_data['location']}")
                if ext_data.get('expansion_type'): details.append(f"Type: {ext_data['expansion_type']}")
            elif s['trigger_type'] == 'LeadershipChange':
                if ext_data.get('person_name'): details.append(f"Person: {ext_data['person_name']}")
                if ext_data.get('new_role'): details.append(f"Role: {ext_data['new_role']}")
                
            cleaned_details = []
            for d in details:
                d_clean = str(d).strip().replace('\n', ' ')
                if len(d_clean) > 50: d_clean = d_clean[:47] + "..."
                cleaned_details.append(d_clean)
                
            detail_str = " | ".join(cleaned_details) if cleaned_details else str(s.get('raw_text', ''))[:70].replace('\n', ' ') + "..."
            
            table_data.append({
                "Date": s['timestamp'][:10],
                "Trigger": s['trigger_type'],
                "Company / Entity": entity_name,
                "Key Details": detail_str,
                "Employees": profile.get('employee_count', 'Unknown'),
                "Revenue Est.": profile.get('revenue_range', 'Unknown'),
                "ICP Score": f"⭐ {profile.get('icp_score', 50)}",
                "CRM Status": f"🎯 {matched}" if matched else "Prospect",
                "Confidence": s.get('confidence_score', 'High'),
                "Source URL": s['source_url']
            })
        
    df = pd.DataFrame(table_data)
    if not df.empty:
        # Deduplicate signals by company and trigger type so companies don't appear multiple times
        df = df.drop_duplicates(subset=['Trigger', 'Company / Entity']).reset_index(drop=True)
        # High-level Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Enriched Signals", len(df))
        col2.metric("CRM Target Account Hits", len(df[df['CRM Status'].str.contains('🎯')]))
        col3.metric("Avg ICP Fit Score", f"{int(df['ICP Score'].str.replace('⭐ ', '').astype(int).mean())}/100")
        col4.metric("Active Triggers", df['Trigger'].nunique())
        
        st.markdown("---")
        
        # Display Interactive Table
        st.dataframe(
            df,
            column_config={
                "Source URL": st.column_config.LinkColumn("Source Link", display_text="Open Link ↗"),
                "CRM Status": st.column_config.TextColumn("CRM Status"),
                "ICP Score": st.column_config.TextColumn("ICP Fit"),
                "Confidence": st.column_config.TextColumn("Confidence")
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Detailed Drilldown Tab
        st.markdown("### 📋 Detailed Signal & Firmographic Drilldown")
        selected_row = st.selectbox("Select a company to view full enriched profile & raw JSON:", df['Company / Entity'].unique())
        if selected_row:
            matching_signals = [s for s in signals if (json.loads(s['extracted_data']) if isinstance(s['extracted_data'], str) else s['extracted_data']).get('company_name') == selected_row or (json.loads(s['extracted_data']) if isinstance(s['extracted_data'], str) else s['extracted_data']).get('hospital_name') == selected_row]
            profile_data = enrich_company(selected_row)
            
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.markdown(f"#### 🏢 Enriched Profile (`{profile_data.get('enrichment_source', 'Cache')}`)")
                st.write(f"**Domain:** `{profile_data.get('domain', 'N/A')}`")
                st.write(f"**Employees:** `{profile_data.get('employee_count', 'Unknown')}`")
                st.write(f"**Revenue Range:** `{profile_data.get('revenue_range', 'Unknown')}`")
                st.write(f"**Sector:** `{profile_data.get('sector', 'Healthcare')}`")
                st.write(f"**Founded Year:** `{profile_data.get('founded_year', 'Unknown')}`")
                st.write(f"**Funding Raised:** `{profile_data.get('funding_raised', 'Unknown')}`")
                st.success(f"**ICP Fit Score: {profile_data.get('icp_score', 50)}/100**")
                
            with col_b:
                st.markdown("#### 📄 Signal Record & JSON")
                for ms in matching_signals:
                    with st.expander(f"{ms['trigger_type']} ({ms['timestamp'][:10]})", expanded=True):
                        st.markdown(f"**Raw Text Snippet:**\n> {ms['raw_text']}")
                        st.json(json.loads(ms['extracted_data']) if isinstance(ms['extracted_data'], str) else ms['extracted_data'])
    else:
        st.warning("No signals match the current filter selection.")
else:
    st.info("No signals found in the database. Run `python main.py scrape --all` to populate data.")
