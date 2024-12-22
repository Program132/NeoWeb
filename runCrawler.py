from Crawler import Crawler
import signal
import argparse

def handle_stop_signal(signum, frame):
    print("\nInterruption reçue. L'indexation va être arrêtée.")
    crawler.handle_stop_signal()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Crawler de site Web")
    parser.add_argument('--url', type=str, required=True, help="L'URL de départ pour le crawling")

    args = parser.parse_args()
    url = args.url

    crawler = Crawler(start_url=url)
    signal.signal(signal.SIGINT, handle_stop_signal)
    crawler.crawl()