from flask import Flask, render_template, request, jsonify
from langchain_community.llms import LlamaCpp
from search import search

app = Flask(__name__)

verbose = False

general_model = LlamaCpp(
    model_path="models/mistral-7b-v0.1.Q5_K_S.gguf",
    n_ctx=32768,
    n_gpu_layers=32,
    n_batch=1024,
    f16_kv=True,
    verbose=verbose,
)

code_model = LlamaCpp(
    model_path="models/starcoder2-3b-Q5_K_S.gguf",
    n_ctx=32768,
    n_gpu_layers=32,
    n_batch=1024,
    f16_kv=True,
    verbose=verbose,
)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST" and request.form.get("action") == "chat":
        user_message = request.form.get("message")
        model_type = request.form.get("model_type")

        if model_type == "general":
            model = general_model
            prompt = f"""Vous êtes un assistant intelligent. Répondez toujours en français.
            Contexte de la conversation : {request.form.get('conversation_history', '')}
            Utilisateur : {user_message}
            Assistant :"""
        elif model_type == "code":
            model = code_model
            prompt = f"""Vous êtes un assistant spécialisé dans le code. Répondez toujours en français.
            Contexte de la conversation : {request.form.get('conversation_history', '')}
            Utilisateur : {user_message}
            Assistant :"""
        else:
            return jsonify({"response": "Modèle non reconnu"})

        output = model.invoke(
            prompt,
            stop=["Utilisateur :", "Assistant :"],
            max_tokens=100,
            temperature=0.7,
            top_p=0.9
        )
        return jsonify({"response": output})

    query = request.args.get("q")
    results = search(query) if query else []
    return render_template("search.html", query=query, results=results)

if __name__ == "__main__":
    app.run(debug=True)