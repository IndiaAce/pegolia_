import os
import json
from datetime import datetime
import feedparser
import requests

# === CONFIGURATION ===

RSS_FEEDS = {
    "PhishLabs": "http://blog.phishlabs.com/rss.xml",
    "Proofpoint": "https://www.proofpoint.com/us/rss.xml",
    "Cisco Talos": "https://blog.talosintelligence.com/feeds/posts/default"
}

HN_QUERY = "email security"
HN_URL = f"https://hn.algolia.com/api/v1/search_by_date?query={HN_QUERY}&tags=story"

# === COLLECT RSS DATA ===

def fetch_rss_articles():
    articles = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            articles.append({
                "source": source,
                "title": entry.get("title"),
                "link": entry.get("link"),
                "published": entry.get("published", "N/A")
            })
    return articles

# === COLLECT HACKER NEWS STORIES ===

def fetch_hn_articles():
    response = requests.get(HN_URL)
    data = response.json()
    articles = []
    for hit in data.get("hits", []):
        articles.append({
            "source": "Hacker News",
            "title": hit.get("title"),
            "link": hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}",
            "published": hit.get("created_at", "N/A")
        })
    return articles

# === SAVE RESULTS TO JSON ===

def save_results(rss_data, hn_data):
    all_articles = rss_data + hn_data
    today = datetime.utcnow().strftime("%Y-%m-%d")
    os.makedirs("results", exist_ok=True)
    output_path = f"results/{today}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2)
    print(f"[+] Saved {len(all_articles)} articles to {output_path}")

# === MAIN EXECUTION ===

if __name__ == "__main__":
    rss_articles = fetch_rss_articles()
    hn_articles = fetch_hn_articles()
    save_results(rss_articles, hn_articles)