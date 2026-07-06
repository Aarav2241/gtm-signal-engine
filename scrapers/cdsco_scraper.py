import asyncio
from crawl4ai import AsyncWebCrawler
from scrapers.base_scraper import BaseScraper
from database.queries import is_url_processed, mark_url_processed, insert_signal
from intelligence.llm_extractor import extract_signal, extract_articles_list

class CDSCOScraper(BaseScraper):
    def __init__(self):
        super().__init__("CDSCOScraper")
        self.url = "https://cdscomdonline.gov.in/"

    async def _scrape_async(self):
        self.logger.info("Starting CDSCO scraping...")
        async with AsyncWebCrawler() as crawler:
            try:
                result = await crawler.arun(url=self.url)
                if result and result.markdown:
                    articles = extract_articles_list(result.markdown)
                    for art in articles:
                        title = art.get("title", "")
                        snippet = art.get("snippet", "")
                        raw_text = f"{title}. {snippet}".strip()
                        if not raw_text or len(raw_text) < 15:
                            continue
                            
                        item_id = f"cdsco_{hash(title)}"
                        if not is_url_processed(item_id):
                            signal_data = extract_signal(raw_text, "RegulatoryApproval")
                            if signal_data:
                                insert_signal({
                                    "source_url": self.url,
                                    "trigger_type": "RegulatoryApproval",
                                    "raw_text": raw_text,
                                    "extracted_data": signal_data.model_dump(),
                                    "matched_account": None,
                                    "confidence_score": "High"
                                })
                            mark_url_processed(item_id)
            except Exception as e:
                self.logger.error(f"Error crawling CDSCO: {e}")
        
        self.logger.info("CDSCO scraping completed.")
        return True

    def scrape(self):
        return asyncio.run(self._scrape_async())
