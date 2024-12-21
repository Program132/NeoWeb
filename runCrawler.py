from Crawler import Crawler
import signal
import sys

def handle_stop_signal(signum, frame):
    print("\nInterruption reçue. L'indexation va être arrêtée.")
    crawler.handle_stop_signal()

if __name__ == '__main__':
    url = "https://fr.wikipedia.org/"

    crawler = Crawler(start_url=url)
    signal.signal(signal.SIGINT, handle_stop_signal)
    crawler.crawl()