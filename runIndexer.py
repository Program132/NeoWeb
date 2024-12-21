from Indexer import Indexer
import signal
import sys

def handle_stop_signal(signum, frame):
    print("\nInterruption reçue. L'indexation va être arrêtée.")
    indexer.handle_stop_signal()

if __name__ == "__main__":
    database_file = "data.json"
    occurence_file = "occurence.json"
    indexer = Indexer(database_file, occurence_file)
    signal.signal(signal.SIGINT, handle_stop_signal)
    indexer.start_indexer()