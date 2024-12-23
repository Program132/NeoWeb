import json
import re
import argparse
from concurrent.futures import ThreadPoolExecutor

import requests
from collections import Counter
from bs4 import BeautifulSoup
from Database import DatabaseManager

import sqlite3
from collections import defaultdict


class PageRankCalculator:
    def __init__(self, db_path, damping_factor=0.85, max_iterations=10, tolerance=1e-6, max_workers=6):
        self.db_path = db_path
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.graph = defaultdict(list)
        self.urls = []
        self.max_workers = max_workers

    def load_graph(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT url, links FROM web_pages")
        rows = cursor.fetchall()

        for url, links in rows:
            self.urls.append(url)
            if links:
                linked_urls = json.loads(links)
                self.graph[url].extend(linked_urls)

        conn.close()

    def compute_rank_for_url(self, url, pagerank, num_urls):
        """Calcule le PageRank pour une URL spécifique."""
        rank_sum = 0
        for referring_url in self.graph:
            if url in self.graph[referring_url]:
                rank_sum += pagerank[referring_url] / len(self.graph[referring_url])

        return (1 - self.damping_factor) / num_urls + self.damping_factor * rank_sum

    def calculate_pagerank(self):
        num_urls = len(self.urls)
        pagerank = {url: 1 / num_urls for url in self.urls}
        new_pagerank = pagerank.copy()

        for iteration in range(self.max_iterations):
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_url = {
                    executor.submit(self.compute_rank_for_url, url, pagerank, num_urls): url
                    for url in self.urls
                }

                for future in future_to_url:
                    url = future_to_url[future]
                    new_pagerank[url] = future.result()

            diff = sum(abs(new_pagerank[url] - pagerank[url]) for url in self.urls)
            pagerank = new_pagerank.copy()

            print(f"Iteration {iteration + 1}, Différence: {diff}")
            if diff < self.tolerance:
                print(f"Convergence atteinte après {iteration + 1} itérations.")
                break

        return pagerank

    def save_pagerank_to_db(self, pagerank):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS page_rank (url TEXT PRIMARY KEY, page_rank REAL)")
        for url, rank in pagerank.items():
            cursor.execute(
                "INSERT OR REPLACE INTO page_rank (url, page_rank) VALUES (?, ?)",
                (url, rank),
            )

        conn.commit()
        conn.close()

    def run(self):
        self.load_graph()
        pagerank = self.calculate_pagerank()
        self.save_pagerank_to_db(pagerank)


class Indexer:
    def __init__(self, db="neoweb.db", table="pending_indexer", refresh=False, max_workers=6):
        self.database = DatabaseManager(db)
        self.indexer_table_name = table
        self.refresh = refresh
        self.max_workers = max_workers

    def get_urls_to_index(self):
        self.database.connect()
        query = "SELECT url FROM web_pages"
        result = self.database.execute_query(query)
        self.database.close()
        return [row[0] for row in result]

    def extract_words(self, text):
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())
        words = text.split()
        return words

    def is_url_pending_or_indexed(self, url):
        self.database.connect()

        query = "SELECT url FROM pending_indexer WHERE url = ? AND status = 'indexing'"
        result = self.database.execute_query(query, (url,))
        if result:
            self.database.close()
            return True

        query = "SELECT list_urls FROM occurrences WHERE list_urls LIKE ?"
        result = self.database.execute_query(query, ('%' + url + '%',))
        if result:
            self.database.close()
            return True

        self.database.close()
        return False

    def update_occurrences(self, word, url, count):
        self.database.connect()
        query = "SELECT list_urls FROM occurrences WHERE word = ?"
        result = self.database.execute_query(query, (word,))

        if result:
            list_urls = json.loads(result[0][0])
            list_urls[url] = list_urls.get(url, 0) + count
            query = "UPDATE occurrences SET list_urls = ? WHERE word = ?"
            self.database.execute_query(query, (json.dumps(list_urls), word))
        else:
            list_urls = {url: count}
            query = "INSERT INTO occurrences (word, list_urls) VALUES (?, ?)"
            self.database.execute_query(query, (word, json.dumps(list_urls)))
        self.database.close()

    def index_url(self, url):
        self.database.connect()
        update_query = "INSERT OR IGNORE INTO pending_indexer (url, status) VALUES (?, 'indexing')"
        self.database.execute_query(update_query, (url,))
        self.database.close()

        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                print(f"Erreur HTTP {response.status_code} pour {url}")
                return
        except requests.RequestException as e:
            print(f"Erreur lors de la requête {url}: {e}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        words = self.extract_words(text)
        word_counts = Counter(words)

        for word, count in word_counts.items():
            self.update_occurrences(word, url, count)

        self.database.connect()
        delete_query = "DELETE FROM pending_indexer WHERE url = ?"
        self.database.execute_query(delete_query, (url,))
        self.database.close()

    def start(self):
        urls = self.get_urls_to_index()
        if not urls:
            print("Aucune URL à indexer.")
            return

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.index_url, url): url for url in urls}
            for future in futures:
                try:
                    future.result()
                    print(f"Indexation de {futures[future]} terminée.")
                except Exception as e:
                    print(f"Erreur lors de l'indexation de {futures[future]}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indexation des pages web.")
    parser.add_argument("--refresh", action="store_true", help="Force l'indexation de toutes les URLs, même celles déjà indexées.")
    parser.add_argument("--max-workers", type=int, default=5, help="Nombre maximal de threads pour l'indexation parallèle.")
    args = parser.parse_args()

    indexer = Indexer(refresh=args.refresh, max_workers=args.max_workers)
    indexer.start()