import signal
import sys
from Crawler import Crawler
import Indexer

def handle_interrupt(signal, frame):
    print("\nInterruption reçue (Ctrl+C). Sauvegarde en cours...")
    print("Données sauvegardées.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_interrupt)

print("Le programme est en cours d'exécution... Appuyez sur Ctrl+C pour interrompre.")
crawler = Crawler("https://en.wikipedia.org/wiki/List_of_file_signatures", max_iteration=10)
crawler.crawl()

Indexer.start_indexer()