# Dactylogame - README

## Présentation

**Dactylogame** est un jeu de dactylographie multijoueur simple implémenté en utilisant FastAPI pour le côté serveur et WebSocket pour la communication en temps réel entre les clients. Le jeu met au défi les joueurs de taper rapidement des mots aléatoires, et les scores sont mis à jour en temps réel. Le projet se compose d'un serveur FastAPI (`main.py`) et d'un fichier JavaScript côté client (`script.js`).

## Fonctionnalités

- **Jeu de Dactylographie Multijoueur :** Les joueurs peuvent rejoindre une session de jeu, rivaliser les uns contre les autres en tapant des mots, et voir leurs scores mis à jour en temps réel.

- **Communication WebSocket :** WebSocket est utilisé pour la communication bidirectionnelle entre le serveur et les clients, permettant des mises à jour en temps réel et la synchronisation de l'état du jeu.

- **Mises à Jour Dynamiques de l'UI :** L'interface utilisateur se met à jour dynamiquement en fonction des messages WebSocket, offrant une expérience utilisateur fluide et réactive.

## Structure du Projet

- **`main.py` :** L'implémentation du serveur FastAPI avec des points d'extrémité WebSocket pour gérer la logique du jeu, les connexions des joueurs et les mises à jour en temps réel.

- **`script.js` :** Le fichier JavaScript côté client responsable de la gestion des messages WebSocket, de la mise à jour de l'interface utilisateur et de la gestion des interactions des joueurs.

- Les autres fichiers incluent des dépendances, des fichiers statiques et des modèles HTML pour l'interface utilisateur.

## Démarrage

1. **Cloner le Dépôt :**
    ```bash
    git clone https://github.com/ThomasSanna/reseaux_python
    cd  reseaux_python/ProtocolesWeb/exercice-5-dactylogame
    ```

2. **Installer les Dépendances :**
    ```bash
    pip install fastapi uvicorn
    ```

3. **Lancer le Serveur :**
    ```bash
    uvicorn main:app --reload
    ```

4. **Ouvrir dans le Navigateur :**
   - Ouvrez votre navigateur web et accédez à `http://localhost:8000`.
   - Les joueurs peuvent rejoindre le jeu en accédant à cette URL.

## Comment Jouer

1. **Rejoindre le Jeu :**
   - Accédez à l'URL fournie (`http://localhost:8000`) dans votre navigateur web.
   - Vous recevrez un numéro de joueur et verrez les autres joueurs connectés.

2. **Début du Jeu :**
   - Une fois que tous les joueurs sont connectés, le jeu peut être démarré en cliquant sur le bouton "Commencer".
   - Un compte à rebours commencera, et le jeu démarrera après le compte à rebours.

3. **Défi de Dactylographie :**
   - Tapez les mots affichés le plus rapidement possible.
   - Les mots correctement tapés augmentent votre score.

4. **Fin du Jeu :**
   - Le jeu se termine après un temps défini.
   - Les scores finaux et le gagnant sont affichés.

5. **Rejouer :**
   - Les joueurs peuvent choisir de rejouer en cliquant sur le bouton "Rejouer".

## Notes Additionnelles

- Le projet utilise un simple fichier JSON (`frequence.json`) contenant des mots français pour le défi de dactylographie. Vous pouvez modifier ou remplacer ce fichier pour personnaliser l'ensemble de mots.

- Pour le développement, envisagez de lancer le serveur avec l'option `--reload` pour activer le rechargement automatique du code lors des modifications.

N'hésitez pas à explorer et à modifier le code pour ajouter de nouvelles fonctionnalités ou personnaliser davantage le jeu !
