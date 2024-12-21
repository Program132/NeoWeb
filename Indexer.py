from JsonDatabase import JsonDatabase

class Indexer:
    def __init__(self, data_db="data.json", occurrence_db="occurence.json"):
        self.data_db = data_db
        self.occurence_db = occurrence_db
        self.db_data = JsonDatabase(data_db)
        self.db_occurence = JsonDatabase(occurrence_db)
        self.needToStop = False

    def add_new_word(self, word, url):
        self.db_occurence.add_record(word, {url: 1})

    def add_occurrence_word(self, word, url):
        existing_record_word = self.db_occurence.get_record(word)

        if not existing_record_word:
            self.add_new_word(word, url)
        else:
            if url not in existing_record_word:
                existing_record_word[url] = 1
                self.db_occurence.update_record(word, existing_record_word)
            else:
                existing_record_word[url] += 1
                self.db_occurence.update_record(word, existing_record_word)

    def start_indexer(self):
        all_urls = self.db_data.get_all_keys()
        print(f"URLs à indexer : {all_urls}")
        if len(all_urls) == 0:
            print("Aucune URL à indexer.")
            return

        for url in all_urls:
            if self.needToStop: break

            record = self.db_data.get_record(url)
            text_page = record.get("text", "")
            words = text_page.split()

            for word in words:
                if self.needToStop: break

                self.add_occurrence_word(word, url)

        print("Indexation terminée.")

    def handle_stop_signal(self):
        self.needToStop = True