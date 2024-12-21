import math
from JsonDatabase import JsonDatabase

# Fonction de fréquence de terme
def get_term_frequency(nb_occurrences, nb_mots):
    return nb_occurrences / nb_mots


# Fonction pour l'IDF
def get_inverse_document_frequency(nb_pages_dbb, nb_pages_with_term):
    return nb_pages_dbb / nb_pages_with_term


# Fonction pour calculer le TF-IDF
def get_TF_IDF_value(nb_occurrences, nb_mots, nb_pages_dbb, nb_pages_with_term):
    return get_term_frequency(nb_occurrences, nb_mots) * math.log10(
        get_inverse_document_frequency(nb_pages_dbb, nb_pages_with_term))


# Calcul du PageRank en fonction de la requête
def get_Page_Rank_value(url, query, dataDB="data.json"):
    db_data = JsonDatabase(dataDB)

    # Nombre total de pages dans la base de données
    all_urls = db_data.get_all_keys()
    nb_pages = len(all_urls)

    if nb_pages == 0:
        return 1  # Retourne un PageRank arbitraire si aucune page n'est disponible

    # Initialisation des PageRank de toutes les pages
    page_rank = {url: 1 / nb_pages for url in all_urls}
    damping_factor = 0.85
    iterations = 20  # Nombre d'itérations pour affiner les scores de PageRank

    # Créer un dictionnaire des liens sortants de chaque page
    outgoing_links = {url: [] for url in all_urls}
    for current_url in all_urls:
        record = db_data.get_record(current_url)
        if record and "links" in record:  # Supposons que chaque enregistrement contient une liste de liens
            outgoing_links[current_url] = record["links"]

    # Effectuer des itérations pour raffiner le PageRank
    for _ in range(iterations):
        new_page_rank = {}
        for current_url in all_urls:
            # PageRank initial basé sur les pages qui pointent vers la page courante
            rank_sum = 0
            for other_url in all_urls:
                if current_url in outgoing_links[other_url]:  # Si "other_url" pointe vers "current_url"
                    rank_sum += page_rank[other_url] / len(outgoing_links[other_url])

            # Appliquer la formule de PageRank
            new_page_rank[current_url] = (1 - damping_factor) / nb_pages + damping_factor * rank_sum

        page_rank = new_page_rank

    # Adapter le PageRank en fonction de la requête
    record = db_data.get_record(url)
    if record and "text" in record:
        text_page = record["text"]
        words_in_page = set(text_page.split())

        # Calculer une pondération basée sur la correspondance des termes de la requête
        common_words = set(query.split()) & words_in_page
        query_relevance = len(common_words) / len(set(query.split()))  # Proportion de termes de la requête dans la page

        # Appliquer cette pondération au PageRank
        return page_rank.get(url, 1 / nb_pages) * (1 + query_relevance)

    return page_rank.get(url, 1 / nb_pages)  # Retourner la valeur calculée ou une valeur par défaut si non trouvé


# Fonction pour obtenir la valeur finale de la page (TF-IDF + PageRank)
def get_final_value_page(url, query, dataDB="data.json", occurenceDB="occurence.json"):
    # Charger les bases de données
    db_data = JsonDatabase(dataDB)
    db_occurence = JsonDatabase(occurenceDB)

    # Total des mots dans la page (nb_mots)
    record = db_data.get_record(url)
    if not record or "text" not in record:
        raise ValueError(f"URL '{url}' introuvable ou mal formatée dans la base de données.")
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

    # Calculer le TF-IDF
    tf_idf = get_TF_IDF_value(nb_occurrences, nb_mots, nb_pages_dbb, nb_pages_with_term)

    # Calculer le PageRank ajusté par la requête
    page_rank_value = get_Page_Rank_value(url, query, dataDB)

    # Retourner la somme pondérée du TF-IDF et du PageRank
    return 0.7 * tf_idf + 0.3 * page_rank_value