import streamlit as st
import pandas as pd
from datetime import datetime, timezone

def load_articles():
    try:
        df = pd.read_csv('combined_news_articles.csv')
        return df
    except FileNotFoundError:
        st.error("No articles found. Please run the news collector first.")
        return pd.DataFrame()

def main():
    st.title("Data News Collector")
    
    df = load_articles()
    
    if df.empty:
        st.warning("No articles available. Please run the news collector to fetch articles.")
    else:
        # Convert publish_date to datetime
        df['publish_date'] = pd.to_datetime(df['publish_date'], errors='coerce')
        
        # Get current month and year
        current_date = datetime.now(timezone.utc)
        
        # Filter articles from current month or month before
        df_filtered = df[
            ((df['publish_date'].dt.month == current_date.month)) |
            ((df['publish_date'].dt.month == (current_date.month - 1 if current_date.month > 1 else 12)))
        ]
        
        # Sort articles by published date, most recent first
        df_filtered = df_filtered.sort_values('publish_date', ascending=False)
        
        if df_filtered.empty:
            st.warning("No articles found for the current month or the month before.")
        else:
            for _, row in df_filtered.iterrows():
                st.subheader(row['title'])
                st.write(f"Source: {row['source']}")
                if pd.notnull(row['publish_date']):
                    st.write(f"Published: {row['publish_date'].strftime('%Y-%m-%d')}")
                else:
                    st.write("Published: Date not available")
                st.markdown(f"[Read more]({row['url']})")
                st.markdown("---")

if __name__ == "__main__":
    main()
