# Data News Scraper

A Python-based tool that aggregates technical blog posts and articles from various engineering blogs and data-related sources. The project includes a web interface built with Streamlit for easy viewing of collected articles.

## Features

- Scrapes engineering blog posts from major tech companies (Meta, Netflix, Stripe, etc.)
- Collects data engineering articles from specialized sources (KDNuggets, BigDataWire, etc.)
- Automated article collection with publish dates and titles
- Web interface for browsing recent articles
- Filters articles to show only recent content (current month and previous month)

## Prerequisites

- OpenAI API Key
- `uv` installed

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd data-news-scrapper
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -e .
```

4. Set up environment variables:
```bash
export OPENAI_API_KEY="your-api-key"  # Required for AI-powered scraping
```

## Usage

Run the application using:
```bash
python news_app.py
```

This will:
1. Start the news collection process
2. Merge articles from different sources
3. Launch the Streamlit web interface

The web interface will be available at `http://localhost:8501`

## Project Structure

- `src/ai_scraper.py`: Handles scraping of engineering blogs using AI
- `src/news_collector.py`: Collects articles from data engineering sources
- `src/app.py`: Streamlit web interface
- `news_app.py`: Main application runner

## Data Sources

### Engineering Blogs
- Meta Engineering
- Netflix Tech Blog
- Stripe Engineering
- Uber Engineering
- Airbnb Engineering
- And many more...

### Data Engineering Sources
- KDNuggets
- BigDataWire
- The Pragmatic Engineer
