import feedparser
from scrapers.base_scraper import BaseScraper
from database.queries import is_url_processed, mark_url_processed
from config.settings import RSS_FEEDS
from intelligence.llm_extractor import classify_relevance, extract_signal
from database.queries import insert_signal

class RSSScraper(BaseScraper):
    def __init__(self):
        super().__init__("RSSScraper")

    def scrape(self):
        self.logger.info("Scraping RSS feeds...")
        for source, url in RSS_FEEDS.items():
            self.logger.info(f"Parsing feed: {source} ({url})")
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                link = entry.link
                if is_url_processed(link):
                    continue
                
                title = entry.title
                summary = entry.get('summary', '')
                
                # Check relevance using LLM
                is_relevant = classify_relevance(title, summary)
                if is_relevant:
                    self.logger.info(f"Relevant article found: {title}")
                    
                    # For RSS, we extract from summary.
                    signal_data = extract_signal(f"Title: {title}\nSummary: {summary}", "FundingRound") 
                    
                    if signal_data:
                        insert_signal({
                            "source_url": link,
                            "trigger_type": "FundingRound",
                            "raw_text": summary,
                            "extracted_data": signal_data.model_dump(),
                            "matched_account": None, # matcher.py will handle this later
                            "confidence_score": "High"
                        })
                
                mark_url_processed(link)
        self.logger.info("RSS scraping completed.")
        return True

if __name__ == "__main__":
    scraper = RSSScraper()
    scraper.run()
