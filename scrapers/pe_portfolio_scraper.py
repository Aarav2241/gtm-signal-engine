import json
import asyncio
from crawl4ai import AsyncWebCrawler
from scrapers.base_scraper import BaseScraper
from database.queries import get_latest_pe_snapshot, insert_pe_snapshot, insert_signal
from intelligence.llm_extractor import extract_signal, extract_names_list

class PEPortfolioScraper(BaseScraper):
    def __init__(self):
        super().__init__("PEPortfolioScraper")
        with open('config/pe_funds.json', 'r') as f:
            self.funds = json.load(f)

    async def _scrape_async(self):
        self.logger.info("Starting PE Portfolio scraping...")
        async with AsyncWebCrawler() as crawler:
            for fund in self.funds:
                fund_name = fund['fund_name']
                url = fund['portfolio_url']
                self.logger.info(f"Crawling {fund_name} portfolio at {url}")
                
                try:
                    result = await crawler.arun(url=url)
                    if not result or not result.markdown:
                        self.logger.warning(f"No content extracted from {url}")
                        continue
                        
                    current_companies = extract_names_list(result.markdown, "portfolio company names or invested startups")
                    if not current_companies:
                        continue
                        
                    previous_companies = get_latest_pe_snapshot(fund_name)
                    new_companies = [c for c in current_companies if c not in previous_companies]
                    
                    for new_company in new_companies:
                        self.logger.info(f"Detected new portfolio company for {fund_name}: {new_company}")
                        
                        signal_data = extract_signal(f"{fund_name} invested in portfolio company {new_company}", "PEPortfolioAdd")
                        if signal_data:
                            insert_signal({
                                "source_url": url,
                                "trigger_type": "PEPortfolioAdd",
                                "raw_text": f"New portfolio addition: {new_company}",
                                "extracted_data": signal_data.model_dump(),
                                "matched_account": None,
                                "confidence_score": "High"
                            })
                            
                    insert_pe_snapshot(fund_name, current_companies)
                except Exception as e:
                    self.logger.error(f"Error crawling PE fund {fund_name}: {e}")
        
        self.logger.info("PE Portfolio scraping completed.")
        return True

    def scrape(self):
        return asyncio.run(self._scrape_async())
