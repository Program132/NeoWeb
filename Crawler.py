import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import sqlite3
import signal
import datetime
import sys
from database import init_db

# Couleurs ANSI pour les logs
COLORS = {
    "INFO": "\033[93m",   # Jaune
    "OK": "\033[92m",     # Vert
    "ERROR": "\033[91m",  # Rouge
    "RESET": "\033[0m"
}

def print_log(msg, level="INFO"):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    color = COLORS.get(level.upper(), COLORS["INFO"])
    reset = COLORS["RESET"]
    print(f"{color}[{level.upper()} {now}]{reset} {msg}", file=sys.stdout)

# Interruption propre
stop_flag = False

RETRY_LIMIT = 5
RETRY_DELAY = 0.3

def safe_execute(cursor, query, params=()):
    for i in range(RETRY_LIMIT):
        try:
            cursor.execute(query, params)
            return
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print_log(f"Database locked, retrying ({i+1}/{RETRY_LIMIT})...", "ERROR")
                time.sleep(RETRY_DELAY * (i + 1))
            else:
                raise
    raise sqlite3.OperationalError("Failed after retries: " + query)

def is_allowed(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        resp = requests.get(robots_url, timeout=5)
        if resp.status_code != 200:
            return True
        disallow = [line.split(': ')[1] for line in resp.text.splitlines()
                    if line.startswith('Disallow')]
        for rule in disallow:
            if parsed.path.startswith(rule):
                return False
    except:
        return True
    return True

def is_valid_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if any(x in parsed.path.lower() for x in [".pdf", ".jpg", ".jpeg", ".png", ".zip", ".exe", ".svg"]):
        return False
    if parsed.query or parsed.fragment:
        return False
    return True

def crawl(seed_url=None):
    global stop_flag
    init_db()
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    if seed_url:
        cur.execute("INSERT OR IGNORE INTO queue (url) VALUES (?)", (seed_url,))
        conn.commit()

    visited = set()

    def stop_handler(sig, frame):
        global stop_flag
        print_log("Shutdown requested. Stopping after current URL...", "INFO")
        stop_flag = True

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    while not stop_flag:
        row = cur.execute("SELECT url FROM queue LIMIT 1").fetchone()
        if not row:
            print_log("Queue is empty. Waiting for new URLs...", "INFO")
            time.sleep(10)
            continue

        url = row[0]
        safe_execute(cur, "DELETE FROM queue WHERE url=?", (url,))
        conn.commit()

        if url in visited or not is_allowed(url):
            continue

        try:
            print_log(f"Crawling: {url}", "INFO")
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else ''
            text = ' '.join(p.get_text() for p in soup.find_all('p'))

            raw_links = [a['href'] for a in soup.find_all('a', href=True)]
            links = []
            for raw in raw_links:
                absolute = urljoin(url, raw)
                if is_valid_url(absolute):
                    links.append(absolute)
                    safe_execute(cur, "INSERT OR IGNORE INTO queue (url) VALUES (?)", (absolute,))

            safe_execute(cur, "REPLACE INTO pages (url, title, content, links) VALUES (?, ?, ?, ?)",
                         (url, title, text, '\n'.join(links)))
            conn.commit()

            visited.add(url)
            print_log(f"Crawled: {url} (visited: {len(visited)})", "OK")
            time.sleep(0.1)

        except Exception as e:
            print_log(f"Failed to crawl {url}: {e}", "ERROR")
            continue

    conn.close()
    print_log("Crawler stopped cleanly.", "OK")

if __name__ == "__main__":
    crawl("https://franceinfo.fr")
