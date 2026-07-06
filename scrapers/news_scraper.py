import asyncio
from crawl4ai import AsyncWebCrawler
from scrapers.base_scraper import BaseScraper
from database.queries import is_url_processed, mark_url_processed, insert_signal
from intelligence.llm_extractor import classify_relevance, extract_signal, extract_articles_list

class NewsScraper(BaseScraper):
    def __init__(self):
        super().__init__("NewsScraper")
        self.sources = [
            "https://www.vccircle.com/healthcare",
            "https://www.expresshealthcare.in/"
        ]

    async def _scrape_async(self):
        self.logger.info("Starting Crawl4AI news scraping...")
        async with AsyncWebCrawler() as crawler:
            for source in self.sources:
                self.logger.info(f"Crawling {source}")
                try:
                    result = await crawler.arun(url=source)
                    if not result or not result.markdown:
                        self.logger.warning(f"No content extracted from {source}")
                        continue
                        
                    articles = extract_articles_list(result.markdown)
                    for art in articles:
                        title = art.get("title", "")
                        snippet = art.get("snippet", "")
                        raw_text = f"{title}. {snippet}".strip()
                        if not raw_text or len(raw_text) < 15:
                            continue
                            
                        item_url = f"{source}#item={hash(title)}"
                        if is_url_processed(item_url):
                            continue
                            
                        if classify_relevance(title, snippet):
                            self.logger.info(f"Relevant article: {title}")
                            signal_data = extract_signal(f"Title: {title}\nSnippet: {snippet}", "FundingRound")
                            if signal_data:
                                insert_signal({
                                    "source_url": source,
                                    "trigger_type": "FundingRound",
                                    "raw_text": snippet or title,
                                    "extracted_data": signal_data.model_dump(),
                                    "matched_account": None,
                                    "confidence_score": "High"
                                })
                        mark_url_processed(item_url)
                except Exception as e:
                    self.logger.error(f"Error crawling news source {source}: {e}")
        
        self.logger.info("News scraping completed.")
        return True

    def scrape(self):
        return asyncio.run(self._scrape_async())

if __name__ == "__main__":
    scraper = NewsScraper()
    scraper.run()
