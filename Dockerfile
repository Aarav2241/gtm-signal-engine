FROM python:3.11-slim

WORKDIR /app

# Install required system libraries for Playwright & Crawl4AI browser automation
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    build-essential \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium browser for Crawl4AI
RUN playwright install --with-deps chromium

# Copy all project code
COPY . .

# Ensure database directory exists
RUN mkdir -p database

# Expose Streamlit dashboard port
EXPOSE 8501

# Run BOTH the background scheduler (for 24/7 live scraping) and the Streamlit dashboard
CMD ["sh", "-c", "python main.py schedule & streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0"]
