# News & Events Monitoring MVP (Variant E)


This project ingests news (RSS) about utility-related events, extracts location and category, stores events in SQLite, and provides a small Flask UI to query and visualize incidents.


**Variant chosen:** E — Mobile/edge-friendly model + Singer-style connectors + SQLite + Flask dashboard.


### Quick start (local)


1. Create virtualenv and install:


```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

2.  Initialize DB and seed demo data:
sqlite3 events.db < schema.sql
python seed.py

3.  Run the app:
python app.py


4.