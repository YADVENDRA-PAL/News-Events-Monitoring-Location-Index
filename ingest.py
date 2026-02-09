# ingest.py
import feedparser
import sqlite3
from datetime import datetime, timezone
from dateutil import parser as dateparser
import spacy
from geopy.geocoders import Nominatim
from bs4 import BeautifulSoup
import time


DB = "events.db"
nlp = spacy.load("en_core_web_sm")
geolocator = Nominatim(user_agent="utils_monitoring_mvp", timeout=10)


SOURCES = [
{"name": "HindustanTimes", "url": "https://www.hindustantimes.com/rss/topnews/rssfeed.xml"},
{"name": "TheHindu", "url": "https://www.thehindu.com/news/national/?service=rss"}
]


CATEGORY_KEYWORDS = {
"power_outage": ["power outage", "power cut", "electricity outage", "grid failure", "load shedding"],
"water_issue": ["water outage", "water crisis", "leak", "flood", "contamination", "water supply"],
"logistics_delay": ["delay", "canceled", "disruption", "stranded", "port delay", "airport delay", "roadblock"]
}

def classify_category(text):
    t = (text or "").lower()
    for cat, keys in CATEGORY_KEYWORDS.items():
        for k in keys:
            if k in t:
                return cat
    return "other"




def extract_city_state(text):
    doc = nlp(text or "")
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC"):
            return ent.text, None
    return None, None

def geocode(city, state=None):
    if not city:
        return None, None
    try:
        q = f"{city}, {state}" if state else city
        loc = geolocator.geocode(q)
        if loc:
            return loc.latitude, loc.longitude
    except Exception as e:
        print("geocode error", e)
    return None, None


def clean_html(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def upsert_event(conn, ev):
    cur = conn.cursor()
    cur.execute("SELECT id FROM events WHERE url = ? OR (title = ? AND date_utc = ?)", (ev['url'], ev['title'], ev['date_utc']))
    if cur.fetchone():
        return False
    cur.execute(
        """
        INSERT INTO events (title, summary, full_text, date_utc, source, city, state, country, latitude, longitude, category, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      """,
      (
        ev['title'], ev['summary'], ev['full_text'], ev['date_utc'], ev['source'],
        ev.get('city'), ev.get('state'), ev.get('country'),
        ev.get('latitude'), ev.get('longitude'), ev.get('category'), ev.get('url')
      )
    )
    conn.commit()
    return True

def parse_feed_item(item, source_name):
    title = item.get("title") or ""
    summary = clean_html(item.get("summary") or item.get("description") or "")
    published = item.get("published") or item.get("updated") or datetime.now(timezone.utc).isoformat()
    try:
        date_utc = dateparser.parse(published).astimezone(timezone.utc).isoformat()
    except Exception:
        date_utc = datetime.now(timezone.utc).isoformat()
    link = item.get("link")
    text_for_nlp = " ".join([title, summary])
    city, state = extract_city_state(text_for_nlp)
    lat, lon = geocode(city, state) if city else (None, None)
    category = classify_category(text_for_nlp)
    return {
        "title": title,
        "summary": summary[:400],
        "full_text": summary,
        "date_utc": date_utc,
        "source": source_name,
        "city": city,
        "state": state,
        "country": None,
        "latitude": lat,
        "longitude": lon,
        "category": category,
        "url": link
    }

def run_once():
    conn = sqlite3.connect(DB)
    for s in SOURCES:
        try:
            feed = feedparser.parse(s["url"])
            for item in feed.entries[:40]:
                ev = parse_feed_item(item, s["name"])
                if upsert_event(conn, ev):
                    print("Inserted:", ev['title'])
        except Exception as e:
            print("Error fetching", s["url"], e)
    conn.close()


if __name__ == "__main__":
    # run continuously; in docker this process will keep the container alive
    while True:
        run_once()
        print("Sleeping 10 minutes...")
        time.sleep(600)