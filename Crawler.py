import json
import argparse
import signal
import sys
from Database import DatabaseManager
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from threading import Lock
import re

class Crawler:
    def __init__(self, start_url, database="neoweb.db"):
        self.db = DatabaseManager(database)
        self.visited = set()
        self.queue = []
        self.data = []
        self.lock = Lock()
        self.robot_parsers = {}
        self.running = True
        self.add_to_pending(start_url)

    def can_fetch(self, url):
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        if base_url not in self.robot_parsers:
            robots_url = urljoin(base_url, "/robots.txt")
            rp = RobotFileParser()
            try:
                rp.set_url(robots_url)
                rp.read()
            except Exception as e:
                print(f"Erreur lors du chargement de robots.txt pour {base_url}: {e}")
                rp = None
            self.robot_parsers[base_url] = rp

        rp = self.robot_parsers.get(base_url)
        if rp:
            return rp.can_fetch("*", url)
        return True

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        if not parsed_url.path:
            return False

        clean_path_pattern = re.compile(r"^/wiki(/[a-zA-Z0-9_-]+)?$")
        return bool(clean_path_pattern.match(parsed_url.path))

    def add_to_pending(self, url):
        self.db.connect()
        query = """
            INSERT OR IGNORE INTO pending (url, status)
            VALUES (?, 'pending')
        """
        self.db.execute_query(query, (url,))
        self.db.close()

    def is_url_crawled(self, url):
        self.db.connect()
        query = "SELECT 1 FROM web_pages WHERE url = ?"
        result = self.db.execute_query(query, (url,))
        self.db.close()
        return len(result) > 0

    def crawl_page(self, url):
        if not self.can_fetch(url):
            print(f"Accès refusé par robots.txt : {url}")
            return

        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                print(f"Erreur HTTP {response.status_code} pour {url}")
                return
        except requests.RequestException as e:
            print(f"Erreur lors de la requête {url}: {e}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('title').text if soup.find('title') else "No Title"
        h1_tags = [h1.text for h1 in soup.find_all('h1')]
        metadata = {meta.get('name'): meta.get('content') for meta in soup.find_all('meta', attrs={'name': True})}
        text = soup.get_text()

        links = soup.find_all('a', href=True)
        found_links = []
        for link in links:
            href = link.get('href')
            absolute_url = urljoin(url, href)


            if not self.is_url_crawled(absolute_url) and self.is_valid_url(absolute_url):
                self.add_to_pending(absolute_url)
                found_links.append(absolute_url)

        self.db.connect()
        data = {
            'url': url,
            'title': title,
            'subtitles': ', '.join(h1_tags),
            'metadata': str(metadata),
            'text': text.strip(),
            'links': json.dumps(found_links)
        }
        query = """
        INSERT OR IGNORE INTO web_pages (url, title, subtitles, metadata, text, links)
        VALUES (:url, :title, :subtitles, :metadata, :text, :links)
        """
        self.db.execute_query(query, data)

        query = "DELETE FROM pending WHERE url = ?"
        self.db.execute_query(query, (url,))
        self.db.close()

    def fill_queue(self):
        self.db.connect()
        query = "SELECT url FROM pending WHERE status = 'pending' LIMIT 50"
        result = self.db.execute_query(query)
        self.db.close()

        for row in result:
            url = row[0]
            if url not in self.visited and url not in self.queue:
                self.queue.append(url)
                self.add_to_pending(url)

    def stop_crawling(self, signal, frame):
        print("\nArrêt du crawling...")
        self.running = False
        self.db.close()
        sys.exit(0)

    def start(self):
        signal.signal(signal.SIGINT, self.stop_crawling)

        while self.running:
            if len(self.queue) <= 3:
                print("La file d'attente est presque vide, remplissage...")
                self.fill_queue()

            if not self.queue:
                print("Aucune URL à explorer.")
                break

            url = self.queue.pop(0)
            print(f"Crawling {url}...")

            self.db.connect()
            update_query = "UPDATE pending SET status = 'crawling' WHERE url = ?"
            self.db.execute_query(update_query, (url,))
            self.db.close()

            self.crawl_page(url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lance un crawler pour explorer les pages web.")
    parser.add_argument("--url", type=str, help="L'URL de départ pour le crawling.")
    args = parser.parse_args()

    crawler = Crawler(start_url=args.url)
    crawler.start()
