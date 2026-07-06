import json
import hashlib
import asyncio
from crawl4ai import AsyncWebCrawler
from scrapers.base_scraper import BaseScraper
from database.queries import insert_signal, get_conn
from intelligence.llm_extractor import extract_signal

class CompanyTeamScraper(BaseScraper):
    def __init__(self):
        super().__init__("CompanyTeamScraper")
        with open('config/target_accounts.json', 'r') as f:
            self.accounts = json.load(f)

    def get_last_hash(self, account_name):
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT content_hash FROM team_snapshots WHERE account_name = ? ORDER BY timestamp DESC LIMIT 1', (account_name,))
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else None

    def save_hash(self, account_name, content_hash):
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO team_snapshots (account_name, content_hash) VALUES (?, ?)', (account_name, content_hash))
        conn.commit()
        conn.close()

    async def _scrape_async(self):
        self.logger.info("Starting Company Team scraping...")
        async with AsyncWebCrawler() as crawler:
            for account in self.accounts:
                if 'team_page_url' not in account or not account['team_page_url']:
                    continue
                    
                url = account['team_page_url']
                self.logger.info(f"Crawling team page for {account['name']}")
                try:
                    result = await crawler.arun(url=url)
                    if not result or not result.markdown:
                        continue
                        
                    content = result.markdown
                    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                    
                    last_hash = self.get_last_hash(account['name'])
                    if last_hash and last_hash != content_hash:
                        self.logger.info(f"Team page changed for {account['name']}!")
                        signal_data = extract_signal(f"Leadership changes detected on {account['name']} team page: {content[:3000]}", "LeadershipChange")
                        if signal_data:
                            insert_signal({
                                "source_url": url,
                                "trigger_type": "LeadershipChange",
                                "raw_text": f"Team page change detected for {account['name']}",
                                "extracted_data": signal_data.model_dump(),
                                "matched_account": account['name'],
                                "confidence_score": "High"
                            })
                    
                    self.save_hash(account['name'], content_hash)
                except Exception as e:
                    self.logger.error(f"Error crawling team page for {account['name']}: {e}")
        
        self.logger.info("Company Team scraping completed.")
        return True

    def scrape(self):
        return asyncio.run(self._scrape_async())
