import sqlite3
import math
import re
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def search(query):
    logging.info(f"Searching for: {query}")
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    tokens = re.findall(r'\b\w+\b', query.lower())
    scores = defaultdict(float)
    doc_freq = {}
    total_docs = cur.execute("SELECT COUNT(*) FROM pages").fetchone()[0]

    for word in tokens:
        rows = cur.execute("SELECT url, tf FROM index_inverted WHERE word=?", (word,)).fetchall()
        df = len(rows)
        if df == 0: continue
        idf = math.log(total_docs / df)
        for url, tf in rows:
            scores[url] += tf * idf

    for url in scores:
        pr = cur.execute("SELECT rank FROM pagerank WHERE url=?", (url,)).fetchone()
        if pr:
            scores[url] += pr[0]

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    results = []
    for url, score in sorted_scores[:10]:
        title = cur.execute("SELECT title FROM pages WHERE url=?", (url,)).fetchone()[0]
        results.append({"url": url, "title": title, "score": score})

    conn.close()
    logging.info(f"Found {len(results)} results.")
    return results