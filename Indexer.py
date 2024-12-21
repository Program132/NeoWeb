from JsonDatabase import JsonDatabase

def add_new_word(word, occurenceDB, url):
    db_occurence = JsonDatabase(occurenceDB)
    db_occurence.add_record(word, {f"{url}": 1})

def add_occurence_word(word, occurenceDB, url):
    db_occurence = JsonDatabase(occurenceDB)
    existing_record_word = db_occurence.get_record(word)

    if not existing_record_word:
        add_new_word(word, occurenceDB, url)
        return

    if url not in existing_record_word:
        existing_record_word[url] = 1
        db_occurence.update_record(word, existing_record_word)
    else:
        current_occurence = existing_record_word[url]
        existing_record_word[url] = current_occurence + 1
        db_occurence.update_record(word, existing_record_word)

def start_indexer(dataDB="data.json", occurenceDB="occurence.json"):
    db = JsonDatabase(dataDB)
    all_urls = db.get_all_keys()
    print(all_urls)
    if len(all_urls) == 0: return

    for url in all_urls:
        record = db.get_record(url)
        text_page = record["text"]
        words = text_page.split()
        db_occurence = JsonDatabase(occurenceDB)

        for w in words:
            existing_record_word = db_occurence.get_record(w)
            if not existing_record_word: add_new_word(w, occurenceDB, url)
            add_occurence_word(w, occurenceDB, url)