import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BaseScraper:
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.max_retries = 3
        self.retry_delay = 5 # seconds

    def run(self):
        self.logger.info(f"Starting scraper: {self.name}")
        retries = 0
        while retries < self.max_retries:
            try:
                return self.scrape()
            except Exception as e:
                self.logger.error(f"Error scraping {self.name}: {e}")
                retries += 1
                if retries < self.max_retries:
                    self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"Failed to scrape {self.name} after {self.max_retries} retries.")
                    return None

    def scrape(self):
        raise NotImplementedError("Subclasses must implement the scrape method.")
