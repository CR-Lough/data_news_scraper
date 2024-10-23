import json
import os
import csv
from datetime import datetime
import pandas as pd
from pydantic import BaseModel, Field
from typing import List, Optional

api_key = os.getenv("OPENAI_API_KEY", "")

from scrapegraphai.graphs import SmartScraperGraph

# Define the configuration for the scraping pipeline
graph_config = {
    "llm": {
        "api_key": f"{api_key}",
        "model": "openai/gpt-4o-mini",
    },
    "verbose": True,
    "headless": True,
}

class Article(BaseModel):
    source: str = Field(description="The source of the article")
    url: str = Field(description="The URL of the article")
    publish_date: Optional[str] = Field(description="The publication date of the article")
    title: str = Field(description="The title of the article")

class Articles(BaseModel):
    articles: List[Article]


# Sources
sources = [
    # "https://engineering.fb.com/",
    # "https://www.notion.so/blog/topic/tech",
    # "https://netflixtechblog.com/?gi=6515e0884fa2",
    # "https://stripe.com/blog/engineering",
    # "https://www.uber.com/en-IN/blog/engineering/",
    # "https://medium.com/airbnb-engineering",
    # "https://www.figma.com/blog/engineering/",
    # "https://medium.com/pinterest-engineering",
    # "https://www.reddit.com/r/RedditEng/",
    # "https://instagram-engineering.com/",
    # "https://engineering.atspotify.com/",
    # "https://slack.engineering/",
    # "https://blog.x.com/engineering/en_us",
    # "https://engineering.ramp.com/",
    # "https://www.canva.dev/blog/engineering/",
    # "https://stackoverflow.blog/engineering/",
    # "https://www.coinbase.com/blog/landing/engineering",
    # "https://www.rippling.com/blog/topics?topics=engineering",
    # "https://medium.engineering/",
    # "https://dropbox.tech/",
    # "https://quoraengineering.quora.com/",
    # "https://hacks.mozilla.org/",
    "https://blog.cloudflare.com/",
]

all_articles = []

for source in sources:
    # Create the SmartScraperGraph instance
    smart_scraper_graph = SmartScraperGraph(
        prompt="For all articles on the page, list the source of the page, the formatted URL of the article (which should match the source) without parameters, article publish date (in format YYYY-MM-DD), and article title",
        source=source,
        config=graph_config,
        schema=Articles
    )

    # Run the pipeline
    result = smart_scraper_graph.run()
    
    # Add source to each article and extend the all_articles list
    for article in result['articles']:
        article['source'] = source
        all_articles.append(article)

# Save all articles to a CSV file
csv_filename = 'data/all_articles.csv'
fieldnames = ['url', 'title', 'source', 'publish_date']

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for article in all_articles:
        writer.writerow(article)

print(f"Saved {len(all_articles)} articles to {csv_filename}")

