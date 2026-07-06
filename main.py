import argparse
from scrapers.rss_scraper import RSSScraper
from scrapers.news_scraper import NewsScraper
from scrapers.cdsco_scraper import CDSCOScraper
from scrapers.google_news_scraper import GoogleNewsScraper
from scrapers.pe_portfolio_scraper import PEPortfolioScraper
from scrapers.company_team_scraper import CompanyTeamScraper
from scrapers.nabh_scraper import NABHScraper
from database.db import init_db
import os

def main():
    parser = argparse.ArgumentParser(description="GTM Signal Engine CLI")
    parser.add_argument("command", choices=["scrape", "dashboard", "schedule", "initdb"], help="Command to run")
    parser.add_argument("--trigger", help="Specific trigger to scrape (e.g., funding, news)")
    parser.add_argument("--all", action="store_true", help="Run all scrapers")
    
    args = parser.parse_args()
    
    if args.command == "initdb":
        init_db()
        print("Database initialized.")
        
    elif args.command == "scrape":
        init_db()
        if args.all:
            RSSScraper().run()
            NewsScraper().run()
            GoogleNewsScraper().run()
            PEPortfolioScraper().run()
            CompanyTeamScraper().run()
            NABHScraper().run()
            CDSCOScraper().run()
        else:
            print("Please specify --all for now (PoC).")
            
    elif args.command == "dashboard":
        os.system("streamlit run dashboard/app.py")
        
    elif args.command == "schedule":
        os.system("python scheduler.py")

if __name__ == "__main__":
    main()
