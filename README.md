# GTM Signal Engine PoC

Automated outbound signal detection system for Insight Tribe.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

2. Set Groq API key:
   ```bash
   export GROQ_API_KEY="your_api_key"
   ```

3. Initialize DB:
   ```bash
   python main.py initdb
   ```

## Usage

1. Run Scrapers:
   ```bash
   python main.py scrape --all
   ```

2. Start Dashboard:
   ```bash
   python main.py dashboard
   ```

3. Start Scheduler:
   ```bash
   python main.py schedule
   ```
