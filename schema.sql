CREATE TABLE IF NOT EXISTS events (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
summary TEXT,
full_text TEXT,
date_utc TEXT,
source TEXT,
city TEXT,
state TEXT,
country TEXT,
latitude REAL,
longitude REAL,
category TEXT,
url TEXT,
inserted_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_events_city ON events(city);
CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(date_utc);