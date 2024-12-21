# NeoWeb

[![Downloads](https://img.shields.io/github/downloads/Program132/NeoWeb/total?style=for-the-badge)](https://github.com/Program132/NeoWeb)
[![Code size](https://img.shields.io/github/languages/code-size/Program132/NeoWeb?style=for-the-badge)](https://github.com/Program132/NeoWeb)
[![Last Release](https://img.shields.io/github/release/Program132/NeoWeb?style=for-the-badge)](https://github.com/Program132/NeoWeb/releases)

NeoWeb a pour but de montrer le fonctionnement d'un moteur de recherche s'inspirant du principe de Google. 
En réalité, la plupart des moteurs de recherche ne font pas de recherche sur le web, mais dans une base de données qui s'agrandit de jour en jour.
Je m'inspire de la vidéo de [V2F](https://youtu.be/O3cJUR2NimI) et utilise sa vidéo comme guide.  Je vous conseille de la regarder pour mieux comprendre le fonctionnement.

# Structure

## JsonDatabase.py

Les données sont stockées dans une "base de données" au format JSON. Vous pouvez créer la vôtre en modifiant le code pour utiliser Redis ou une base de données SQL, par exemple.

## Crawler.py

Le crawler va permettre de récupérer les informations sur chaque page web. Il récupère :
- le titre
- les "sous-titres" (h1)
- les métadonnées
- le texte de la page
- les liens (href)

Il sauvegarde ces données dans un fichier .json dans ce projet. Comme dit plus tôt, vous pouvez modifier le code pour utiliser une base de données SQL ou NoSQL, comme Redis.

## Indexer.py

Son rôle va être d'analyser le texte de chaque URL pour trouver les occurrences de chaque mot et en indiquer la pertinence. 
Pour cela, nous devons calculer le [TF-IDF](https://fr.wikipedia.org/wiki/TF-IDF), où TF signifie Term Frequency et IDF signifie Inverse Document Frequency.

En plus de cela, on doit savoir comment trouver des pages intéressantes. 
Pour cela, on sait que lorsqu'une page web contient un lien vers une autre page, on récupère le nombre de liens qui pointent vers cette page en question. 
Plus une page web est citée par d'autres sites, plus elle est intéressante. Cependant, il est possible d'abuser de ce système, donc on doit trouver une autre méthode. 
On attribue un score à la page, ainsi si une page est citée rarement, sa valeur en tant que lien vers un site est faible, tandis que les liens des sites populaires valent beaucoup. 
Pour cela, on utilisera le [PageRank](https://fr.wikipedia.org/wiki/PageRank).



## NeoWeb.py

Lance l'application web en utilisant Flask.

# Utilisation

Je vous invite à télécharger le code source et à le mettre sur un VPS ou une machine locale si vous souhaitez l'utiliser. 
Vous pouvez lancer plusieurs `runCrawler.py` et `runIndexer.py` et les arrêter quand vous le souhaitez.

Par ailleurs, si vous rencontrez des bugs, n'hésitez pas à en faire part à la communauté dans [Issues](https://github.com/Program132/NeoWeb/issues). 
Si vous voulez soumettre des suggestions, vous êtes le bienvenu !

# Prochaines Releases

J'ai pour but de mettre en place une API avec PHP, et l'application web sera sûrement aussi sous PHP. 
Améliorer l'efficacité du Crawler et de l'Indexer, utiliser une base de donnée SQL.