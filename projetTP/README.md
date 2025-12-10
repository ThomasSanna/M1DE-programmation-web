# Projet TP - Developpement Web : Dactylogame

Ce projet est une application web de dactylogame développée avec FastAPI pour le backend et HTML/CSS/JavaScript pour le frontend. L'application permet aux utilisateurs de s'inscrire, de se connecter, de jouer à un jeu de dactylographie et de suivre leurs scores. Le projet inclut également des fonctionnalités d'authentification sécurisée avec JWT.

## Fonctionnalités

- Inscription et connexion des utilisateurs
- Jeu de dactylographie avec génération aléatoire de texte utilisant le fichier json "frequence.json" accessible [ici](https://github.com/nmondon/mots-frequents/blob/7b5b62125a1724cdd12a1a145764dfc177ed39f1/data/frequence.json#L1).
- Suivi des scores des utilisateurs et affichage du classement

## Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/ThomasSanna/M1DE-programmation-web.git
   cd M1DE-programmation-web/projetTP
   ```
2. Créer un environnement virtuel et l'activer :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Démarrer l'application :
   ```bash
   uvicorn main:app --reload
   ```

## Spécificités base de données

Utilisation de MySQL pour la gestion des utilisateurs, des sessions de jeu, et des scores. SQLAlchemy est utilisé comme ORM pour interagir avec la base de données.

### Tables + Dictionnaire de données

#### Tables principales

| Table           | Description                                 |
|-----------------|---------------------------------------------|
| `users`         | Stocke les informations des utilisateurs    |
| `scores`        | Enregistre les scores des parties           |
| `game_sessions` | Gère les sessions de jeu en cours           |

#### Dictionnaire de données

##### `users`

| Champ          | Type           | Description                                 |
|----------------|----------------|---------------------------------------------|
| id             | int(11)        | Identifiant unique (PK, auto-incrémenté)    |
| username       | varchar(50)    | Nom d'utilisateur (unique)                  |
| email          | varchar(100)   | Email de l'utilisateur (unique)             |
| password_hash  | varchar(255)   | Hash du mot de passe                        |
| created_at     | timestamp      | Date de création                            |
| updated_at     | timestamp      | Date de dernière modification               |

##### `scores`

| Champ         | Type         | Description                                  |
|---------------|--------------|----------------------------------------------|
| id            | int(11)      | Identifiant unique (PK, auto-incrémenté)     |
| user_id       | int(11)      | Référence à l'utilisateur (FK)               |
| score         | int(11)      | Score obtenu                                 |
| words_correct | int(11)      | Nombre de mots corrects                      |
| words_wrong   | int(11)      | Nombre de mots incorrects                    |
| duration      | int(11)      | Durée de la partie (en secondes)             |
| created_at    | timestamp    | Date de création du score                    |

##### `game_sessions`

| Champ           | Type         | Description                                 |
|-----------------|--------------|---------------------------------------------|
| id              | int(11)      | Identifiant unique (PK, auto-incrémenté)    |
| user_id         | int(11)      | Référence à l'utilisateur (FK)              |
| session_token   | varchar(64)  | Token unique de session                     |
| words_sequence  | text         | Séquence de mots pour la session            |
| seed            | varchar(32)  | Graine utilisée pour la génération          |
| start_time      | timestamp    | Début de la session                         |
| expected_end_time | timestamp  | Fin prévue de la session                    |
| is_completed    | tinyint(1)   | Session terminée (0/1)                      |
| score_id        | int(11)      | Référence au score associé (FK, nullable)   |

#### Vues

- **`v_leaderboard`** : Vue pour le classement général, calculant le WPM (mots/minute) et la précision pour chaque score.
- **`v_user_stats`** : Vue pour les statistiques globales par utilisateur (nombre de parties, meilleur score, moyenne, précision, etc.).

#### Contraintes et index

- Clés primaires sur les identifiants (`id`)
- Clés étrangères pour relier `scores` et `game_sessions` à `users`
- Index sur les champs de recherche fréquente (`username`, `email`, `score`, etc.)
- Unicité sur `username`, `email` et `session_token`

#### Exemple de relations

- Un utilisateur peut avoir plusieurs scores et sessions de jeu.
- Une session de jeu appartient à un utilisateur et peut référencer un score.
- Les suppressions d'utilisateur entraînent la suppression en cascade de ses scores et sessions.

### Autres informations

Pour 