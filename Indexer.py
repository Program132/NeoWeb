import sqlite3
import re
import datetime
import sys
from collections import defaultdict

COLORS = {
    "INFO": "\033[93m",
    "OK": "\033[92m",
    "ERROR": "\033[91m",
    "RESET": "\033[0m"
}

def print_log(msg, level="INFO"):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    color = COLORS.get(level.upper(), COLORS["INFO"])
    reset = COLORS["RESET"]
    print(f"{color}[{level.upper()} {now}]{reset} {msg}", file=sys.stdout)

def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

def build_index(batch_size=500):
    print_log("Building inverted index in batches...", "INFO")
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS index_inverted (
            word TEXT,
            url TEXT,
            tf REAL,
            PRIMARY KEY (word, url)
        )
    ''')

    cur.execute("DELETE FROM index_inverted")
    conn.commit()
    print_log("Cleared old index data.", "OK")

    cur.execute("SELECT COUNT(*) FROM pages")
    total_docs = cur.fetchone()[0]
    print_log(f"Found {total_docs} documents to index.", "INFO")

    for offset in range(0, total_docs, batch_size):
        cur.execute("SELECT url, content FROM pages LIMIT ? OFFSET ?", (batch_size, offset))
        docs = cur.fetchall()

        for url, content in docs:
            tokens = tokenize(content)
            total_words = len(tokens)
            freqs = defaultdict(int)
            for word in tokens:
                freqs[word] += 1
            for word, count in freqs.items():
                tf = count / total_words
                cur.execute("REPLACE INTO index_inverted (word, url, tf) VALUES (?, ?, ?)", (word, url, tf))

        conn.commit()
        print_log(f"Processed batch offset {offset}/{total_docs}", "OK")

    conn.close()
    print_log("Inverted index built.", "OK")

if __name__ == "__main__":
    build_index()