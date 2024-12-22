import signal
import sys

from Crawler import Crawler
from Database import DatabaseManager

def handle_signal(sig, frame):
    print("\nArrêt demandé (Ctrl+C). Arrêt en cours...")
    crawler.handle_stop_signal()
    sys.exit(0)  # Quitte proprement le programme avec un code de sortie 0

db = DatabaseManager("neoweb.db")
db.connect()

table_name = "web_pages"
columns = {
    "url": "TEXT PRIMARY KEY",
    "links": "TEXT",
    "title": "TEXT",
    "subtitles": "TEXT",
    "metadata": "TEXT",
    "text": "TEXT"
}
db.create_table(table_name, columns)

table_name = "pending"
columns = {
    "url": "TEXT PRIMARY KEY",
    "status": "TEXT",
}
db.create_table(table_name, columns)

db.close()


if __name__ == '__main__':
    crawler = Crawler("https://fr.wikipedia.org/")
    signal.signal(signal.SIGINT, handle_signal)
    crawler.crawl()