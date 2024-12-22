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
    query = request.form.get('query')
    if not query: return jsonify({"error": "Veuillez fournir une requête de recherche."}), 400

    try:
        db_data = JsonDatabase(dataDB)
        all_urls = db_data.get_all_keys()

        if not all_urls: return jsonify({"error": "Aucune URL indexée dans la base de données."}), 404

        results = []
        for url in all_urls:
            try:
                score = get_final_value_page(url, query, dataDB, occurenceDB)

                record = db_data.get_record(url)
                title = extract_title(record)
                excerpt = extract_excerpt(record.get("text", ""))

                results.append({"url": url, "title": title, "excerpt": excerpt, "score": score})
            except ValueError as e: print(f"Erreur pour l'URL {url}: {e}")

        results = sorted(results, key=lambda x: x['score'], reverse=True)

        return render_template('index.html', results=results)
    except FileNotFoundError: return jsonify({"error": "Le fichier data.json est introuvable."}), 500
    except Exception as e: return jsonify({"error": f"Erreur lors du traitement de la requête : {str(e)}"}), 500


def extract_title(record):
    return record["title"]

def extract_excerpt(text_page):
    lines = text_page.splitlines()
    return ' '.join(lines[:3])

if __name__ == '__main__':
    app.run(debug=True)
