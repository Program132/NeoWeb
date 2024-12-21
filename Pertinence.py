import math
from JsonDatabase import JsonDatabase

def get_term_frequency(nb_occurrences, nb_mots):
    return nb_occurrences / nb_mots

def get_inverse_document_frequency(nb_pages_dbb, nb_pages_with_term):
    return nb_pages_dbb / nb_pages_with_term

def get_TF_IDF_value(nb_occurrences, nb_mots, nb_pages_dbb, nb_pages_with_term):
    return get_term_frequency(nb_occurrences, nb_mots) * math.log10(
        get_inverse_document_frequency(nb_pages_dbb, nb_pages_with_term))


def get_Page_Rank_value(url, query, dataDB="data.json"):
    db_data = JsonDatabase(dataDB)

    all_urls = db_data.get_all_keys()
    nb_pages = len(all_urls)

    if nb_pages == 0:
        return 1

    page_rank = {url: 1 / nb_pages for url in all_urls}
    damping_factor = 0.85
    iterations = 20

    outgoing_links = {url: [] for url in all_urls}
    for current_url in all_urls:
        record = db_data.get_record(current_url)
        if record and "links" in record:
            outgoing_links[current_url] = record["links"]

    for _ in range(iterations):
        new_page_rank = {}
        for current_url in all_urls:
            rank_sum = 0
            for other_url in all_urls:
                if current_url in outgoing_links[other_url]:
                    rank_sum += page_rank[other_url] / len(outgoing_links[other_url])

            new_page_rank[current_url] = (1 - damping_factor) / nb_pages + damping_factor * rank_sum

        page_rank = new_page_rank

    record = db_data.get_record(url)
    if record and "text" in record:
        text_page = record["text"]
        words_in_page = set(text_page.split())

        common_words = set(query.split()) & words_in_page
        query_relevance = len(common_words) / len(set(query.split()))

        return page_rank.get(url, 1 / nb_pages) * (1 + query_relevance)

    return page_rank.get(url, 1 / nb_pages)


def get_final_value_page(url, query, dataDB="data.json", occurenceDB="occurence.json"):
    db_data = JsonDatabase(dataDB)
    db_occurence = JsonDatabase(occurenceDB)

    record = db_data.get_record(url)
    if not record or "text" not in record:
        raise ValueError(f"URL '{url}' introuvable ou mal formatée dans la base de données.")
    text_page = record["text"]
    words = text_page.split()
    nb_mots = len(words)

    nb_occurrences = 0
    for word in set(words):
        word_data = db_occurence.get_record(word)
        if word_data and url in word_data:
            nb_occurrences += word_data[url]

    nb_pages_dbb = len(db_data.get_all_keys())

    nb_pages_with_term = 0
    unique_words_in_page = set(words)
    for word in unique_words_in_page:
        word_data = db_occurence.get_record(word)
        if word_data:
            nb_pages_with_term += len(word_data)

    if nb_pages_with_term == 0:
        raise ValueError("Aucun mot trouvé dans d'autres pages.")

    tf_idf = get_TF_IDF_value(nb_occurrences, nb_mots, nb_pages_dbb, nb_pages_with_term)

    page_rank_value = get_Page_Rank_value(url, query, dataDB)

    return 0.7 * tf_idf + 0.3 * page_rank_value