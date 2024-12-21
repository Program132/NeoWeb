import math
from JsonDatabase import JsonDatabase

def get_term_frequency(nb_occurrences, nb_mots):
    return nb_occurrences / nb_mots

def get_inverse_document_frequency(nb_pages_dbb, nb_pages_with_term):
    return nb_pages_dbb / nb_pages_with_term

def get_TF_IDF_value(nb_occurrences, nb_mots, nb_pages_dbb, nb_pages_with_term):
    return get_term_frequency(nb_occurrences, nb_mots) * math.log10(get_inverse_document_frequency(nb_pages_dbb, nb_pages_with_term))

def get_Page_Rank_value():
    return 1

def get_final_value_page(url, dataDB="data.json", occurenceDB="occurence.json"):
    # Charger les bases de données
    db_data = JsonDatabase(dataDB)
    db_occurence = JsonDatabase(occurenceDB)

    # Total des mots dans la page (nb_mots)
    record = db_data.get_record(url)
    if not record or "text" not in record:
        raise ValueError(f"URL '{url}' introuvable ou mal formats dans la base de données.")
    text_page = record["text"]
    words = text_page.split()
    nb_mots = len(words)

    # Obtenir les occurrences du mot dans cette URL (nb_occurrences)
    nb_occurrences = 0
    for word in set(words):
        word_data = db_occurence.get_record(word)
        if word_data and url in word_data:
            nb_occurrences += word_data[url]

    # Nombre total de pages dans la DB (nb_pages_dbb)
    nb_pages_dbb = len(db_data.get_all_keys())

    # Nombre de pages contenant au moins un mot de cette URL (nb_pages_with_term)
    nb_pages_with_term = 0
    unique_words_in_page = set(words)  # Mots uniques de la page
    for word in unique_words_in_page:
        word_data = db_occurence.get_record(word)
        if word_data:
            nb_pages_with_term += len(word_data)

    if nb_pages_with_term == 0:
        raise ValueError("Aucun mot trouvé dans d'autres pages.")

    # Calculer le TF-IDF + Page rank
    return 0.7 * get_TF_IDF_value(nb_occurrences, nb_mots, nb_pages_dbb, nb_pages_with_term) + 0.3 * get_Page_Rank_value()





def add_new_word(word, occurenceDB, url):
    db_occurence = JsonDatabase(occurenceDB)
    db_occurence.add_record(word, {f"{url}": 1})

def add_occurence_word(word, occurenceDB, url):
    db_occurence = JsonDatabase(occurenceDB)
    existing_record_word = db_occurence.get_record(word)
    if not existing_record_word: add_new_word(word, occurenceDB, url)

    current_occurence = existing_record_word[url]
    db_occurence.update_record(word, {f"{url}": current_occurence + 1})

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

        print("### TF-IDF:" + str(get_final_value_page(url, dataDB, occurenceDB)))