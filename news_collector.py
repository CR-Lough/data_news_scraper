import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timezone, timedelta
import logging
import time
import random
import warnings
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

logging.basicConfig(level=logging.INFO)

MIN_DATE = datetime(1970, 1, 1, tzinfo=timezone.utc)

def fetch_news_articles():
    sources = [
        "https://www.kdnuggets.com/tag/data-engineering",
        "https://www.bigdatawire.com/more-articles",
        "https://newsletter.pragmaticengineer.com/s/deepdives?utm_source=substack&utm_medium=menu",
    ]
    
    articles = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for source in sources:
        try:
            logging.info(f"Fetching articles from {source}")
            response = requests.get(source, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')

            if "kdnuggets.com" in source:
                save_raw_content(source, response.text)
                new_articles = extract_kdnuggets(soup, source)
            elif "bigdatawire.com" in source:
                save_raw_content(source, response.text)
                new_articles = extract_bigdatawire(soup, source)
            elif "pragmaticengineer.com" in source:
                save_raw_content(source, response.text)
                new_articles = extract_pragmatic_engineer(soup, source)
            else:
                save_raw_content(source, response.text)
                new_articles = extract_kdnuggets(soup, source)
            
            logging.info(f"Found {len(new_articles)} articles from {source}")
            articles.extend(new_articles)
            
            logging.info(f"Total articles found so far: {len(articles)}")
            time.sleep(random.uniform(1, 3))  # Add a random delay between requests
        except Exception as e:
            logging.error(f"Error fetching from {source}: {str(e)}")
    
    # Convert string dates to datetime objects and filter recent articles
    three_weeks_ago = datetime.now(timezone.utc) - timedelta(weeks=3)
    filtered_articles = []
    for article in articles:
        if isinstance(article['published_at'], str):
            try:
                article['published_at'] = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
            except ValueError:
                article['published_at'] = MIN_DATE
        elif article['published_at'] is None:
            article['published_at'] = MIN_DATE
        elif isinstance(article['published_at'], datetime) and article['published_at'].tzinfo is None:
            article['published_at'] = article['published_at'].replace(tzinfo=timezone.utc)
        
        if article['published_at'] >= three_weeks_ago:
            filtered_articles.append(article)
    
    filtered_articles.sort(key=lambda x: x['published_at'], reverse=True)
    
    logging.info(f"Filtered {len(articles) - len(filtered_articles)} old articles. Keeping {len(filtered_articles)} recent articles.")
    return filtered_articles

def save_raw_content(source, content):
    # Create a directory for raw content if it doesn't exist
    if not os.path.exists('raw_content'):
        os.makedirs('raw_content')
    
    # Generate a filename based on the source URL
    filename = f"raw_content/{source.split('//')[1].replace('/', '_')}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logging.info(f"Saved raw content to {filename}")

def extract_kdnuggets(soup, source):
    articles = []
    for article in soup.find_all('li'):
        title_elem = article.find('a', class_=None)
        if title_elem and title_elem.b:
            title = title_elem.b.text.strip()
            link = title_elem['href']
            date_elem = article.find('font', color="#808080")
            date = date_elem.text.strip('- ') if date_elem else 'No date'
            try:
                published_at = datetime.strptime(date, '%b %d, %Y.').isoformat()
            except ValueError:
                published_at = None
            summary_elem = article.find('div', style="margin-left: 12px; font-size: small;")
            summary = summary_elem.text.strip() if summary_elem else 'No summary available'
            articles.append({
                'title': title,
                'link': link,
                'date': date,
                'summary': summary,
                'source': source,
                'published_at': published_at
            })
    return articles

def extract_bigdatawire(soup, source):
    articles = []
    for article in soup.find_all('div', class_='post'):
        title_elem = article.find('h3', class_='post-title')
        if title_elem and title_elem.a:
            title = title_elem.a.text.strip()
            link = title_elem.a['href']
            
            # Extract date from URL
            date_match = re.search(r'/(\d{4}/\d{2}/\d{2})/', link)
            if date_match:
                date_str = date_match.group(1)
                published_at = datetime.strptime(date_str, '%Y/%m/%d').isoformat()
                date = datetime.strptime(date_str, '%Y/%m/%d').strftime('%B %d, %Y')
            else:
                published_at = None
                date = 'No date'

            summary_elem = article.find('p')
            summary = summary_elem.text.strip() if summary_elem else 'No summary available'
            articles.append({
                'title': title,
                'link': link,
                'date': date,
                'summary': summary,
                'source': source,
                'published_at': published_at
            })
    logging.info(f"Extracted {len(articles)} articles from BigDataWire")
    return articles

def fetch_pragmatic_engineer():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://newsletter.pragmaticengineer.com/s/deepdives")
    
    try:
        # Wait for the "No thanks" button to appear
        no_thanks_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'No thanks')]"))
        )
        
        # Click the "No thanks" button
        no_thanks_button.click()
        
        # Wait for the content to load after dismissing the popup
        # Wait for 10 seconds to allow the page to load
        time.sleep(10)
        driver.get("https://newsletter.pragmaticengineer.com/s/deepdives?utm_source=substack&utm_medium=menu&sort=top")
        time.sleep(10)
        page_source = driver.page_source
        save_raw_content(driver.current_url, page_source)
        
        return page_source
    except TimeoutException:
        print("Timed out waiting for page to load or 'No thanks' button to appear")
    except NoSuchElementException:
        print("Could not find the 'No thanks' button")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()

def extract_pragmatic_engineer(soup, source):
    page_source = fetch_pragmatic_engineer()
    if not page_source:
        logging.error("Failed to fetch Pragmatic Engineer content")
        return []

    # Extract canonical URLs, social titles, post dates, and subtitles
    url_pattern = r'\\?"canonical_url\\?":\\?"(https?://[^\\?"]+)\\?"'
    title_pattern = r'\\?"title\\?":\\?"([^\\?"]+)\\?"'
    date_pattern = r'\\?"post_date\\?":\\?"([^\\?"]+)\\?"'

    urls = re.findall(url_pattern, page_source)
    titles = re.findall(title_pattern, page_source)
    dates = re.findall(date_pattern, page_source)

    articles = []
    for url, title, date in zip(urls, titles, dates):
        try:
            published_at = datetime.fromisoformat(date.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
            formatted_date = published_at.strftime('%Y-%m-%d %H:%M:%S+00:00')
        except ValueError:
            published_at = None

        articles.append({
            'title': title,
            'link': url,
            'date': formatted_date,
            'summary': 'None Available',
            'source': source,
            'published_at': formatted_date
        })

    logging.info(f"Extracted {len(articles)} articles from Pragmatic Engineer")
    return articles

def save_articles(articles):
    df = pd.DataFrame(articles)
    df['collected_at'] = datetime.now().isoformat()
    
    # Remove duplicate rows based on 'title' and 'link'
    df = df.drop_duplicates(subset=['title', 'link'], keep='first')
    
    # Sort by published_at in descending order (most recent first)
    df = df.sort_values('published_at', ascending=False)
    
    df.to_csv('data/data_news_articles.csv', index=False)
    logging.info(f"Saved {len(df)} unique articles to data/data_news_articles.csv")

if __name__ == "__main__":
    articles = fetch_news_articles()
    if articles:
        save_articles(articles)
        print(f"Collected {len(articles)} articles.")
    else:
        print("No articles were collected. Check the logs for more information.")