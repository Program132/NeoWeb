from flask import Flask, request, jsonify, render_template
from JsonDatabase import JsonDatabase
from Pertinence import get_final_value_page

app = Flask(__name__)

dataDB = "data.json"
occurenceDB = "occurence.json"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # Récupérer le champ 'query' du formulaire envoyé via POST
    query = request.form.get('query')  # Utilisation correcte de 'form' pour récupérer la requête
    if not query:
        return jsonify({"error": "Veuillez fournir une requête de recherche."}), 400

    # Charger la base de données
    db_data = JsonDatabase(dataDB)
    all_urls = db_data.get_all_keys()

    if not all_urls:
        return jsonify({"error": "Aucune URL indexée dans la base de données."}), 404

    # Calculer la valeur finale pour chaque URL
    results = []
    for url in all_urls:
        try:
            score = get_final_value_page(url, query, dataDB, occurenceDB)
            results.append({"url": url, "score": score})
        except ValueError as e:
            print(f"Erreur pour l'URL {url}: {e}")

    # Trier les résultats par score descendant
    results = sorted(results, key=lambda x: x['score'], reverse=True)

    # Rendre les résultats sur la page HTML
    return render_template('index.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
