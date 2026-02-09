# app.py
from asyncio import events

from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta


DB = "events.db"
app = Flask(__name__)




def get_db():
    return sqlite3.connect(DB)


@app.route("/")
def index():
    city = request.args.get("city")
    category = request.args.get("category")
    days = int(request.args.get("days") or 7)
    params = []
    q = "SELECT id, title, summary, date_utc, source, city, category, url FROM events WHERE 1=1"
    if city:
        q += " AND city = ?"
        params.append(city)
    if category:
        q += " AND category = ?"
        params.append(category)
    if days:
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        q += " AND date_utc >= ?"
        params.append(cutoff)
    q += " ORDER BY date_utc DESC LIMIT 200"
    conn = get_db()
    cur = conn.cursor()
    cur.execute(q, params)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    events = [dict(zip(cols, r)) for r in rows]
    conn.close()
    return render_template("index.html", events=events, filters={"city": city, "category": category, "days": days})

@app.route("/stats")
def stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT city, COUNT(*) as cnt FROM events GROUP BY city ORDER BY cnt DESC LIMIT 50")
    by_city = cur.fetchall()
    cur.execute("SELECT category, COUNT(*) as cnt FROM events GROUP BY category")
    by_cat = cur.fetchall()
    conn.close()
    return jsonify({
        "by_city": [{ "city": r[0], "count": r[1] } for r in by_city],
        "by_category": [{ "category": r[0], "count": r[1] } for r in by_cat]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)