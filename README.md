# NeoWeb

[![Downloads](https://img.shields.io/github/downloads/Program132/NeoWebtotal?style=for-the-badge)](https://github.com/Program132/NeoWeb)
[![Code size](https://img.shields.io/github/languages/code-size/Program132/NeoWeb?style=for-the-badge)](https://github.com/Program132/NeoWeb)
[![Last Release](https://img.shields.io/github/release/Program132/NeoWeb?style=for-the-badge)](https://github.com/Program132/NeoWeb/releases)

NeoWeb a pour but de montrer le fonctionnement d'un moteur de recherche utilisant le principe de Google.
En réalité, la plupart des moteurs de recherches ne font pas de recherche sur le web mais dans une base de donné qui s'agrandit de jour en jour.
Je m'inspire de la vidéo de [V2F](https://youtu.be/O3cJUR2NimI) et utilise sa vidéo comme guide, je vous conseille de la regarder pour comprendre le fonctionnement.

# Structure

## JsonDatabase.py

Les données sont stockés dans une "base de donnée" au format JSON, vous pouvez créer la vôtre en modifiant le code en utilisant Redis ou une base de donnée SQL par exemple.

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
Pour cela, nous devons calculer le [TF-IDF](https://fr.wikipedia.org/wiki/TF-IDF) où TF signifi Term Frequency et IDF signifi Inverse Document Frequency.

En plus de ça, on doit savoir comment trouver des pages qui sont intéressantes, pour cela on sait que quand une page web a un lien vers une autre page, 
on récupère le nombre de liens qui pointe vers cette page en question.
Plus une page web est cité par d'autres sites, plus elle est intéressante.
Cependant, il est possible d'abuser de ce système donc on doit trouver une autre méthode.
On attribue un score au page, ainsi si une page est cité rarement, sa valeur pour pointer vers un site est faible, tandis que les liens des sites populaires eux valent beaucoup, 
pour cela, on utilisera le [PageRank](https://fr.wikipedia.org/wiki/PageRank).

## NeoWeb.py

Code python qui lance l'application web en utilisant Flask.

# Utilisation

Je vous invite à télécharger le code source et de le mettre sur un VPS / machine local pour vous si vous souhaitez l'utiliser.
Vous pouvez lancer plusieurs runCrawler.py et runIndexer.py, arrêter quand vous voulez.

Par ailleurs, si vous rencontrez des bugs n'hésitez pas à en faire part dans la communauté dans [Issues](https://github.com/Program132/NeoWeb/issues).
Si vous voulez voir des suggestions, vous êtes le bienvenu !

# Prochaines releases

J'ai pour but de mettre en place une API avec PHP, l'application web sera sûrement aussi sous PHP.
Améliorer l'efficacité du Crawler et de l'Indexer.