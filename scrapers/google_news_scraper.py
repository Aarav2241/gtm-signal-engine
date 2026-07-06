import asyncio
import urllib.parse
from crawl4ai import AsyncWebCrawler
from scrapers.base_scraper import BaseScraper
from database.queries import is_url_processed, mark_url_processed, insert_signal
from intelligence.llm_extractor import extract_signal, extract_articles_list

class GoogleNewsScraper(BaseScraper):
    def __init__(self):
        super().__init__("GoogleNewsScraper")
        self.queries = [
            '"appointed" OR "joins as" India medtech OR healthcare',
            '"launches" OR "introduces" India medtech'
        ]

    async def _scrape_async(self):
        self.logger.info("Starting Google News scraping...")
        async with AsyncWebCrawler() as crawler:
            for query in self.queries:
                encoded_query = urllib.parse.quote(query)
                url = f"https://news.google.com/search?q={encoded_query}"
                self.logger.info(f"Crawling {url}")
                
                try:
                    result = await crawler.arun(url=url)
                    if not result or not result.markdown:
                        self.logger.warning(f"No content extracted from {url}")
                        continue
                        
                    articles = extract_articles_list(result.markdown)
                    trigger_type = "LeadershipChange" if "appointed" in query or "joins" in query else "ProductLaunch"
                    
                    for art in articles:
                        title = art.get("title", "")
                        snippet = art.get("snippet", "")
                        raw_text = f"{title}. {snippet}".strip()
                        if not raw_text or len(raw_text) < 10:
                            continue
                            
                        item_url = f"{url}&item={urllib.parse.quote(title[:30])}"
                        if is_url_processed(item_url):
                            continue
                            
                        signal_data = extract_signal(raw_text, trigger_type)
                        if signal_data:
                            insert_signal({
                                "source_url": url,
                                "trigger_type": trigger_type,
                                "raw_text": raw_text,
                                "extracted_data": signal_data.model_dump(),
                                "matched_account": None,
                                "confidence_score": "High"
                            })
                        mark_url_processed(item_url)
                except Exception as e:
                    self.logger.error(f"Error scraping Google News query '{query}': {e}")
        
        self.logger.info("Google News scraping completed.")
        return True

    def scrape(self):
        return asyncio.run(self._scrape_async())
