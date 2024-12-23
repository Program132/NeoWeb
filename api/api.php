<?php
header("Content-Type: application/json");

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents("php://input"), true);
    $query = $input['query'] ?? '';
    $urls_requested_max = isset($input['urls_requested_max']) ? (int)$input['urls_requested_max'] : null;

    if (empty($query)) {
        echo json_encode(["error" => "La requête est vide."]);
        exit;
    }

    try {
        // Connexion à la base de données
        $db = new PDO('sqlite:../neoweb.db');
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Étape 1 : Récupérer les documents contenant le terme
        $stmt = $db->prepare("SELECT word, list_urls FROM occurrences WHERE word = :query");
        $stmt->execute([':query' => $query]);
        $result = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$result) {
            echo json_encode(["error" => "Aucun résultat trouvé pour la requête."]);
            exit;
        }

        $list_urls = json_decode($result['list_urls'], true); // Décodage des URLs et de leurs fréquences (TF)

        // Étape 2 : Calculer IDF pour le terme
        $stmt = $db->query("SELECT COUNT(*) as total_documents FROM web_pages");
        $total_documents = (int)$stmt->fetch(PDO::FETCH_ASSOC)['total_documents'];

        $num_documents_with_term = count($list_urls);
        $idf = log($total_documents / ($num_documents_with_term + 1));

        // Étape 3 : Récupérer les scores PageRank pour les URLs
        $final_scores = [];
        foreach ($list_urls as $url => $tf) {
            // TF-IDF : TF * IDF
            $tf_idf = $tf * $idf;

            // PageRank
            $stmt = $db->prepare("SELECT page_rank FROM page_rank WHERE url = :url");
            $stmt->execute([':url' => $url]);
            $page_rank_result = $stmt->fetch(PDO::FETCH_ASSOC);
            $page_rank = $page_rank_result ? (float)$page_rank_result['page_rank'] : 0.0;

            $final_score = (0.7 * $tf_idf) + (0.3 * $page_rank);

            $final_scores[] = [
                "url" => $url,
                "tf_idf" => $tf_idf,
                "page_rank" => $page_rank,
                "score" => $final_score
            ];
        }

        usort($final_scores, function ($a, $b) {
            return $b['score'] <=> $a['score'];
        });

        if ($urls_requested_max && $urls_requested_max > 0) {
            $final_scores = array_slice($final_scores, 0, $urls_requested_max);
        }

        echo json_encode($final_scores);
    } catch (PDOException $e) {
        echo json_encode(["error" => "Erreur lors de la connexion ou de l'exécution : " . $e->getMessage()]);
    }
} else {
    echo json_encode(["error" => "Méthode non autorisée."]);
}
