import math
from JsonDatabase import JsonDatabase

def get_term_frequency(nb_occurrences: int, nb_mots: int) -> float:
    return nb_occurrences / nb_mots if nb_mots > 0 else 0

def get_inverse_document_frequency(nb_pages_dbb: int, nb_pages_with_term: int) -> float:
    return math.log10(nb_pages_dbb / (1 + nb_pages_with_term))

def get_TF_IDF_value(nb_occurrences: int, nb_mots: int, nb_pages_dbb: int, nb_pages_with_term: int) -> float:
    tf = get_term_frequency(nb_occurrences, nb_mots)
    idf = get_inverse_document_frequency(nb_pages_dbb, nb_pages_with_term)
    return tf * idf

def compute_page_tf_idf(url: str, word: str, dataDB: str = "data.json", occurenceDB: str = "occurence.json") -> float:
    db_data = JsonDatabase(dataDB)
    db_occurence = JsonDatabase(occurenceDB)

    record = db_data.get_record(url)
    if not record or "text" not in record:
        raise ValueError(f"URL '{url}' introuvable ou mal formatée dans la base de données.")

    text_page = record["text"]
    words = text_page.split()
    nb_mots = len(words)

    nb_occurrences = 0
    if word in words:
        word_data = db_occurence.get_record(word) or {}
        nb_occurrences = word_data.get(url, 0)

    nb_pages_dbb = len(db_data.get_all_keys())

    word_data = db_occurence.get_record(word)
    nb_pages_with_term = len(word_data) if word_data else 0

    return get_TF_IDF_value(nb_occurrences, nb_mots, nb_pages_dbb, nb_pages_with_term)