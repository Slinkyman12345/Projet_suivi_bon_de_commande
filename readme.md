# PGB - Programme de gestion de bons de commande - Version 1

## Description

Ce programme est une application de gestion et de suivi des bons de commande développée en Python avec une interface graphique moderne grâce à **CustomTkinter**.  
Il permet de créer, modifier, rechercher, filtrer, supprimer et exporter des bons de commande enregistrés dans une base de données SQLite locale.

---

## Fonctionnalités principales

- **Visualisation** de tous les bons de commande avec affichage détaillé (ID, année, numéro de bon, montants, fournisseur, statut d’envoi, facturation, description, commentaire, etc.).
- **Recherche** et filtrage par année comptable, fournisseur, numéro de bon.
- **Modification** des bons existants, incluant mise à jour des statuts d’envoi à la ville ou à l’entreprise, informations de facturation, commentaires, etc.
- **Suppression** des bons sélectionnés.
- **Export** des résultats de recherche ou de la liste complète au format Excel (.xlsx).
- Affichage clair des colonnes avec des tailles adaptées pour une meilleure lisibilité.
- Gestion des montants engagés, facturés et restants avec calcul automatique.
- Interface utilisateur intuitive et réactive.

---

## Technologies utilisées

- **Python 3.11**
- **CustomTkinter** pour une interface graphique moderne
- **Tkinter** pour la gestion des widgets classiques
- **SQLite3** comme base de données embarquée
- **openpyxl** (ou autre lib) pour l’export Excel
- **PyInstaller** pour la création de l’exécutable Windows

---

## Installation & Exécution

### Prérequis

- Python 3 installé (version recommandée : 3.8+)
- Modules Python requis (à installer via pip) :
- pip install customtkinter openpyxl
- Base de données SQLite (fichier `bons.db`) est créé automatiquement au premier lancement.

### Lancement en mode développement

1. Cloner ou télécharger le projet.
2. Dans un terminal, se placer dans le dossier du projet.
3. Lancer le script principal (exemple : `main.py`) :
4. python main.py


### Création de l’exécutable Windows

1. Installer PyInstaller :
 pip install pyinstaller
2. Dans le dossier du projet, exécuter la commande :
 python -m PyInstaller --onefile --windowed --name "PGB_V1" --add-data "assets;assets" --add-data "bons.db;." main.py
3. L’exécutable se trouve ensuite dans le dossier `dist/` sous le nom `programme_suivi_v2.exe`.

---

## Structure du projet

/mon_projet/
│
├── main.py # Script principal pour lancer l’application
├── db.py # Gestion de la base de données SQLite (création, requêtes)
├── gui/search_window.py # Fenêtre de recherche et affichage des bons
├── gui/edit_window.py # Fenêtre d’édition/modification d’un bon
├── gui/main_window.py # Fenêtre du menu
├── gui/encode_window.py # Fenêtre d'encodage
├── gui/gestion_technique.py
├── gui/tech_log.py
├── export.py # Fonctions d’export Excel
├── bons.db # Fichier base de données SQLite (généré automatiquement)
├── README.md # Ce fichier
└── ...


---

## Utilisation

- **Rechercher** un bon via les filtres en haut (année, fournisseur, numéro de bon).
- **Double-cliquer** sur une ligne pour modifier un bon.
- **Cocher/décocher** les statuts envoyés (ville/entreprise), livré, facturé.
- **Sauvegarder** les modifications via le bouton “Mettre à jour”.
- **Supprimer** un bon sélectionné avec le bouton rouge en bas.
- **Exporter** les résultats visibles en fichier Excel.

---

## Explications supplémentaires

- Les colonnes **Ville** et **Entreprise** indiquent si le bon de commande a été envoyé respectivement à la ville ou à l’entreprise (valeurs “oui”/“non”).
- Les montants sont affichés avec le symbole euro (€).
- La colonne **Commentaire** permet d’ajouter des remarques supplémentaires sur chaque bon.
- Le calcul automatique met à jour le montant restant à payer en fonction du montant engagé et facturé.


---

## Licence

Ce projet est libre d’utilisation et modification au sein de la ZP Namur.
