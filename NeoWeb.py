import subprocess
import time
import requests
from flask import Flask, render_template, request

def start_php_api():
    try:
        php_process = subprocess.Popen(
            ["php", "-S", "localhost:8000", "-t", "./api"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)
        print("PHP API démarrée.")
        return php_process
    except Exception as e:
        print(f"Erreur lors du démarrage de l'API PHP : {e}")
        return None


app = Flask(__name__, template_folder="webapp")
API_URL = "http://localhost:8000/api.php/get_Score"

@app.route('/')
def index():
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')

    if not query:
        return render_template('search.html', results=[], error="Veuillez entrer un terme de recherche.")

    try:
        response = requests.post(API_URL, json={"query": query, "urls_requested_max": 50})
        response_data = response.json()

        if not response_data:
            return render_template('search.html', results=[], error="Aucune réponse de l'API.")

        if "error" in response_data:
            return render_template('search.html', results=[], error=response_data["error"])

        sorted_results = sorted(response_data, key=lambda x: x.get('score', 0))

        return render_template('search.html', results=sorted_results, reversed=False)
    except requests.exceptions.RequestException as e:
        return render_template('search.html', results=[], error=f"Erreur de connexion à l'API : {e}")
    except ValueError:
        return render_template('search.html', results=[], error="Réponse invalide de l'API.")

if __name__ == "__main__":
    php_api_process = start_php_api()

    if not php_api_process:
        print("Impossible de démarrer l'API PHP. Arrêt du programme.")
        exit(1)

    try:
        app.run(port=5000, debug=True)
    finally:
        if php_api_process:
            php_api_process.terminate()
            print("API PHP arrêtée.")