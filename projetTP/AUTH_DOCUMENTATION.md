# Documentation du Système d'Authentification

## Vue d'ensemble

Le système d'authentification de Dactylogame permet aux utilisateurs de créer un compte, se connecter, et jouer tout en sauvegardant leurs scores. Les utilisateurs peuvent également jouer sans authentification en mode anonyme.

## Architecture

### Backend (Python/FastAPI)

#### Modules

##### `auth.py`
Module centralisé pour toutes les fonctionnalités d'authentification :

- **`hash_password(password: str)`** : Hash un mot de passe avec bcrypt
- **`verify_password(plain_password: str, hashed_password: str)`** : Vérifie un mot de passe
- **`create_access_token(data: dict)`** : Crée un token JWT
- **`authenticate_user(db: Session, username: str, password: str)`** : Authentifie un utilisateur
- **`get_current_user(token: str, db: Session)`** : Récupère l'utilisateur depuis le token (obligatoire)
- **`get_current_user_optional(token: str, db: Session)`** : Récupère l'utilisateur depuis le token (optionnel)

##### `database.py`
Modèles SQLAlchemy pour la base de données :

- **`User`** : Stocke les informations utilisateur (username, email, password_hash)
- **`GameSession`** : Stocke les sessions de jeu (avec user_id optionnel)
- **`Score`** : Stocke les scores (avec user_id optionnel pour les joueurs anonymes)

##### `main.py`
Routes API FastAPI :

**Routes d'authentification :**
- `POST /api/auth/register` : Inscription d'un nouvel utilisateur
- `POST /api/auth/login` : Connexion d'un utilisateur existant
- `GET /api/auth/me` : Récupère les informations de l'utilisateur connecté

**Routes de jeu (avec auth optionnelle) :**
- `POST /api/start-game` : Démarre une partie (avec ou sans auth)
- `POST /api/check-word` : Vérifie un mot tapé
- `POST /api/end-game` : Termine la partie et sauvegarde le score

### Frontend (JavaScript/HTML/CSS)

#### `script.js`

**Gestion de l'authentification :**
- `initApp()` : Initialise l'application et vérifie l'authentification
- `loadAuthToken()` : Charge le token depuis localStorage
- `saveAuthToken(token)` : Sauvegarde le token dans localStorage
- `clearAuthToken()` : Supprime le token
- `checkAuthStatus()` : Vérifie si l'utilisateur est connecté
- `handleLogin(event)` : Gère la connexion
- `handleRegister(event)` : Gère l'inscription
- `logout()` : Déconnecte l'utilisateur

**Gestion du jeu :**
Toutes les requêtes API incluent automatiquement le token JWT dans les headers si l'utilisateur est connecté.

#### `index.html`

**Éléments d'authentification :**
- Panneau d'authentification en haut de la page
- Modal de connexion avec formulaire (username, password)
- Modal d'inscription avec formulaire (username, email, password)

#### `style.css`

Styles pour les modaux, formulaires, et panneau d'authentification.

## Flux d'utilisation

### Inscription d'un nouvel utilisateur

1. L'utilisateur clique sur "Inscription"
2. Il remplit le formulaire (username, email, password)
3. Le frontend envoie une requête `POST /api/auth/register`
4. Le backend :
   - Vérifie que le username et l'email ne sont pas déjà utilisés
   - Hash le mot de passe avec bcrypt
   - Crée l'utilisateur en base de données
   - Retourne un token JWT
5. Le frontend sauvegarde le token dans localStorage
6. L'utilisateur est automatiquement connecté

### Connexion d'un utilisateur existant

1. L'utilisateur clique sur "Connexion"
2. Il remplit le formulaire (username, password)
3. Le frontend envoie une requête `POST /api/auth/login`
4. Le backend :
   - Vérifie les identifiants
   - Retourne un token JWT si valides
5. Le frontend sauvegarde le token dans localStorage
6. L'utilisateur est connecté

### Jeu avec authentification

1. L'utilisateur connecté lance une partie
2. Toutes les requêtes API incluent le header `Authorization: Bearer <token>`
3. Le backend associe automatiquement la session et le score à l'utilisateur
4. Le score est sauvegardé avec le `user_id`

### Jeu sans authentification

1. L'utilisateur non connecté lance une partie
2. Les requêtes API ne contiennent pas de token
3. Le backend crée une session anonyme (`user_id = NULL`)
4. Le score est sauvegardé sans `user_id`

## Sécurité

### Hashage des mots de passe
- Utilisation de **bcrypt** via `passlib`
- Les mots de passe ne sont jamais stockés en clair

### Tokens JWT
- Tokens signés avec une clé secrète (à changer en production)
- Durée de validité : 30 jours
- Algorithme : HS256

### Validation des données
- Validation côté backend avec Pydantic
- Vérification de l'unicité des usernames et emails
- Mot de passe minimum 6 caractères côté frontend

## Installation

### Prérequis
```bash
pip install -r requirements.txt
```

### Dépendances ajoutées
- `python-jose[cryptography]` : Pour les tokens JWT
- `passlib[bcrypt]` : Pour le hashage des mots de passe
- `python-multipart` : Pour les formulaires OAuth2

### Configuration de la base de données

La table `scores` doit accepter les valeurs NULL pour `user_id` :

```sql
ALTER TABLE scores MODIFY user_id INT NULL;
```

## Configuration

### Clé secrète JWT
**⚠️ IMPORTANT** : Changez la clé secrète dans `auth.py` en production :

```python
SECRET_KEY = "votre_cle_secrete_a_changer_en_production"
```

Générez une clé sécurisée avec :
```python
import secrets
secrets.token_urlsafe(32)
```

## Tests

### Tester l'inscription
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpassword"}'
```

### Tester la connexion
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword"
```

### Tester l'accès utilisateur
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <votre_token>"
```

## Points d'amélioration futurs

1. **Réinitialisation de mot de passe** : Ajouter un système de récupération par email
2. **Tokens de rafraîchissement** : Implémenter des refresh tokens
3. **Validation email** : Ajouter une confirmation par email lors de l'inscription
4. **Rate limiting** : Limiter les tentatives de connexion
5. **2FA** : Ajouter l'authentification à deux facteurs
6. **OAuth** : Permettre la connexion via Google, GitHub, etc.
7. **Profil utilisateur** : Page de profil avec historique des scores
8. **Leaderboard** : Classement global des meilleurs joueurs
