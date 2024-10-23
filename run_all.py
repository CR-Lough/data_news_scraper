import subprocess
import time
import os
import pandas as pd

def run_news_collector():
    print("Running news collector...")
    subprocess.run(["python3", "ai_scraper.py"], check=True)
    subprocess.run(["python3", "news_collector.py"], check=True)
    
    # Merge the two CSV files
    merge_csv_files()
    
    print("News collector finished.")

def merge_csv_files():
    # Read the CSV files
    ai_scraper_df = pd.read_csv('all_articles.csv')
    news_collector_df = pd.read_csv('data_news_articles.csv')
    news_collector_df['published_at'] = pd.to_datetime(news_collector_df['published_at'], errors='coerce').dt.date
    # Rename columns in ai_scraper_df to match news_collector_df
    news_collector_df = news_collector_df.rename(columns={
        'link': 'url',
        'published_at': 'publish_date'
    })

    # Add missing columns to ai_scraper_df
    ai_scraper_df['summary'] = 'No summary available'
    ai_scraper_df['collected_at'] = pd.Timestamp.now().isoformat()

    # Combine the dataframes, giving precedence to ai_scraper_df
    combined_df = pd.concat([ai_scraper_df, news_collector_df]).drop_duplicates(subset=['url'], keep='first')

    # Sort by publish_date in descending order
    combined_df['publish_date'] = pd.to_datetime(combined_df['publish_date'], errors='coerce')
    combined_df = combined_df.sort_values('publish_date', ascending=False)

    # Save the combined dataframe
    combined_df.to_csv('combined_news_articles.csv', index=False)
    print(f"Saved {len(combined_df)} combined articles to combined_news_articles.csv")

def run_streamlit():
    print("Starting Streamlit app...")
    streamlit_process = subprocess.Popen(["streamlit", "run", "app.py"])
    return streamlit_process

if __name__ == "__main__":
    try:
        run_news_collector()
        streamlit_process = run_streamlit()
        
        print("Press Ctrl+C to stop the Streamlit app and exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Streamlit app...")
        streamlit_process.terminate()
        streamlit_process.wait()
        print("Streamlit app stopped. Exiting.")
    except subprocess.CalledProcessError:
        print("An error occurred while running the news collector.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
