<?php
require_once 'Database.php';

class PageAnalyzer {
    private $db;

    public function __construct($dbPath) {
        $this->db = new SQLite3($dbPath);
    }

    public function getAllPages() {
        $query = "SELECT url, title, text FROM web_pages";
        $results = $this->db->query($query);
        $pages = [];

        while ($row = $results->fetchArray(SQLITE3_ASSOC)) {
            $pages[] = $row;
        }

        return $pages;
    }

    private function calculateScore($page, $queryWords) {
        $text = strtolower($page['text']); // Texte de la page
        $totalWords = str_word_count($text); // Nombre total de mots dans la page
        if ($totalWords === 0) return 0;

        $occurrences = 0;
        foreach ($queryWords as $word) {
            $occurrences += substr_count($text, strtolower($word)); // Compte les occurrences des mots
        }

        $tf = $occurrences / $totalWords; // Calcul du TF
        $idf = log(1 + 1 / count($queryWords)); // Calcul d'un IDF simplifié

        return $tf * $idf; // Score TF-IDF
    }

    public function getScores($query) {
        $queryWords = explode(' ', strtolower($query)); // Découpe les mots-clés de la requête
        $pages = $this->getAllPages(); // Récupère toutes les pages
        $scores = [];

        foreach ($pages as $page) {
            $score = $this->calculateScore($page, $queryWords); // Calcule le score pour chaque page
            $scores[] = [
                'url' => $page['url'],
                'title' => $page['title'],
                'score' => $score
            ];
        }

        return $scores;
    }
}

header('Content-Type: application/json');

try {
    $dbPath = '../neoweb.db'; // Chemin vers la base de données SQLite
    $input = json_decode(file_get_contents('php://input'), true); // Récupère les données POST

    if (!isset($input['query'])) {
        throw new Exception("Le paramètre 'query' est manquant.");
    }

    $query = $input['query']; // Récupère la requête utilisateur
    $analyzer = new PageAnalyzer($dbPath);
    $scores = $analyzer->getScores($query); // Calcule les scores

    // Tri des résultats par score décroissant
    usort($scores, function($a, $b) {
        return $b['score'] <=> $a['score'];
    });

    echo json_encode($scores); // Renvoie les résultats en JSON
} catch (Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
