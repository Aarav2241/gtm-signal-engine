import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from scrapers.rss_scraper import RSSScraper
from scrapers.news_scraper import NewsScraper
from scrapers.cdsco_scraper import CDSCOScraper
from scrapers.google_news_scraper import GoogleNewsScraper
from scrapers.pe_portfolio_scraper import PEPortfolioScraper
from scrapers.company_team_scraper import CompanyTeamScraper
from scrapers.nabh_scraper import NABHScraper

logging.basicConfig(level=logging.INFO)

def run_rss():
    RSSScraper().run()

def run_news():
    NewsScraper().run()
    GoogleNewsScraper().run()

def run_diffs():
    PEPortfolioScraper().run()
    CompanyTeamScraper().run()
    NABHScraper().run()

def run_cdsco():
    CDSCOScraper().run()

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(run_rss, 'interval', hours=6)
    scheduler.add_job(run_news, 'interval', hours=12)
    scheduler.add_job(run_diffs, 'interval', days=1)
    scheduler.add_job(run_cdsco, 'interval', days=1)
    
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")
    
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
