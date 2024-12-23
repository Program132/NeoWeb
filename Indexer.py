import json
import re
import argparse
import requests
from collections import Counter
from bs4 import BeautifulSoup
from Database import DatabaseManager

class Indexer:
    def __init__(self, db="neoweb.db", table="pending_indexer", refresh=False):
        self.database = DatabaseManager(db)
        self.indexer_table_name = table
        self.refresh = refresh

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

        # Vérifier si l'URL est en cours d'indexation
        query = "SELECT url FROM pending_indexer WHERE url = ? AND status = 'indexing'"
        result = self.database.execute_query(query, (url,))
        if result:
            self.database.close()
            return True

        # Vérifier si l'URL est déjà indexée via les mots-clés
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
            if url in list_urls:
                list_urls[url] += count
            else:
                list_urls[url] = count
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

        for url in urls:
            if self.is_url_pending_or_indexed(url):
                print(f"L'URL {url} est déjà en cours d'indexation ou déjà indexée.")
                continue

            print(f"Indexation de {url}...")
            self.index_url(url)
            print(f"Indexation de {url} terminée.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indexation des pages web.")
    parser.add_argument("--refresh", action="store_true", help="Force l'indexation de toutes les URLs, même celles déjà indexées.")
    args = parser.parse_args()

    indexer = Indexer(refresh=args.refresh)
    indexer.start()