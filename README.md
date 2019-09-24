# Interface pour AuCaSe

Interface pour le projet Auction Catalog Segmentation (AuCaSe).

## Installation

L'interface requiert `flask`, `flask-sqlalchemy`, `python-dateutil` et `mysqlclient`. Il est possible d'installer les quatre en installant [pipenv](https://pipenv.readthedocs.io/en/latest/) et lançant `pipenv install`.

Il faut également une base de donnée MySQL avec le contenu du dump présent dans la repo sous `aucase.sql.zip`. Une fois les données chargées, il faut encore éditer le fichier `app/config.py` avec les identifiants d'un utilisateur ayant les droits `SELECT` sur la base.

## Utilisation
L'interface est une application [Flask](https://flask.palletsprojects.com/en/1.1.x/), elle se lance avec la commande `flask run -p PORT` ou `pipenv run flask run -p PORT` si on utilise pipenv.

## Description du répertoire
```bash
.
├── app
│   ├── config.py
│   ├── __init__.py
│   ├── main
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── search.py
│   ├── models.py
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   └── js
│   │       ├── aucase.js
│   │       └── jquery.simplePagination.js
│   └── templates
│       ├── index.html
│       ├── layout.html
│       ├── _object.html
│       ├── object-results.html
│       └── search.html
├── aucase.sql.gz
├── Pipfile
├── Pipfile.lock
├── README.md
└── shell.py
```
- Les fichiers `Pipfile` et `Pipfile.lock` contiennent les dépendences pour pipenv.
- Le fichier `aucase.sql.zip` contient un dump compressé de la base de donnée.
- Les fichiers `shell.py`, `app/__init__.py` et `app/main/__init__.py` sont des fichiers d'initialisation standard de Flask.
- Le fichier `app/config.py` contient la configuration de l'application Flask, avec entre autre les informations de la base MySQL à compléter. Pour les autres options, se référer à la documentation de Flask.
- Le fichier `app/models.py` contient la description du modèle de donnée présent dans la base MySQL pour pouvoir interopérer avec Flask via sqlalchemy.
- Le fichier `app/main/routes.py` contient les "routes" vers les différentes pages de l'application, à savoir la homepage avec la description du projet, la page `/search` avec l'interface de recherche et la page qui ne sert qu'à faire des requête et qui contient l'API `/api`, cette dernière est décrite plus en détail dans la section suivante.
- Le fichier `app/main/search.py` contient la logique pour effectuer une recherche dans la base de donnée avec du plein texte, une période temporelle et des acteurs.
- Les fichiers dans `app/templates` contiennent du HTML qui est utilisé par l'application. Le framework de CSS utilisé est [Bootstrap 4](http://getbootstrap.com/).
  - Le fichier `app/templates/layout.html` est le template de base, il contient la barre de navigation.
  - Les fichiers `app/templates/object-results.html` et `app/templates/_object.html` sont deux fichiers qui sont utilisé directement par Flask pour générer le HTML nécessaire qui est donnée par l'API et qui sert à afficher les résultats.
  - Le fichier `app/templates/index.html` qui contient la homepage et la description du projet.
  - Le fichier `app/templates/search.html` qui contient l'interface de recherche avec les différents champs ainsi que les différents fichiers javascript nécessaires au bon fonctionnement de l'application (`jquery`, `popper`, `bootstrap`, `jquery-throttle-debounce`, `bootstrap-datepicker`, `bootstrap-select`).
- Le fichier `app/static/js/jquery.simplePagination.js` contient un script javascript pour de la pagination (pas disponible sur un CDN donc mis directement dans le répertoire).
- Le fichier `app/static/js/aucase.js` contient toute la logique javascript de l'application, le fichier est commenté.
- Le fichier `app/static/css/style.css` contient les règles CSS propres à l'application.

## Description de l'API
L'API de recherche est appelée avec une fonction POST qui prend un objet JSON avec les arguments suivants:
- `sectioncategorysearch` qui contient le texte de recherche dans les sections de type catégories.
- `sectionauthorsearch` qui contient le texte de recherche dans les sections de type auteurs/écoles.
- `objectsearch` qui contient le texte de recherche dans les titres et descriptions des objets.
- `startdate` qui contient la date de début
- `enddate` qui contient la date de fin
- `actors` qui est une liste des id (de la base de données) des acteurs recherchés
- `sortingorder` qui détermine le tri des résultat par défaut (n'importe quelle valeur) ou par date ("date").
- `page` détermine la page, l'API pagine les résultats par 20 objets.

L'API retourne un objet JSON contenant un attribut `results_count` qui est le nombre de résultat de la recherche et `html` qui contient le HTML nécessaire pour montrer les résultats.
