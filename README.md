# NeoWeb

NeoWeb a pour but de montrer le fonctionnement d'un moteur de recherche utilisant le principe de google.
Je m'inspire de la vidéo de [V2F](https://youtu.be/O3cJUR2NimI) et utilise sa vidéo comme guide, je vous conseille de la regarder pour comprendre le fonctionnement.

# Structure

## JsonDatabase.py

Les données sont stockés dans une grande base de donnée, vous pouvez créer la vôtre en modifiant le code en utilisant Redis ou une base de donnée SQL par exemple.

## Crawler.py

Le crawler va permettre de récupérer les informations sur chaque page web, il récupère : 
- le titre
- les "sous-titres" (h1)
- les meta données
- le texte de la page
- les liens (href)

Il sauvegarde ces données dans un fichier .json dans ce projet, comme dit plus tôt, vous pouvez modifier le code pour avoir une base de donnée SQL ou NoSQl par exemple Redis.

## Indexer.py

Son rôle va être d'analyser le texte de chaque URL pour trouver les occurrences de chaque mot et d'indiquer la pertinence de ce dernier.