from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import uvicorn
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional
from db.database import get_db, GameSession, Score, User
from auth.auth import (
    hash_password, 
    authenticate_user, 
    create_access_token, 
    get_current_user,
    get_current_user_optional
)

app = FastAPI() # Création de l'application FastAPI

# Modèles Pydantic pour la validation des données

# Modèles d'authentification
class UserRegister(BaseModel):
    """Modèle pour l'inscription d'un nouvel utilisateur"""
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    """Modèle pour la connexion d'un utilisateur"""
    username: str
    password: str

class Token(BaseModel):
    """Modèle pour la réponse contenant le token d'accès"""
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    """Modèle pour la réponse contenant les informations d'un utilisateur"""
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Modèles de jeu
class GameStart(BaseModel):
    pass

class WordCheck(BaseModel):
    session_id: str
    word: str
    index: int

class GameEnd(BaseModel):
    session_id: str

@app.get("/")
def read_root():
    return FileResponse('static/index.html')

@app.get("/classement")
def read_root():
    return FileResponse('static/classement.html') # Cette route est correcte, mais nous allons l'ajuster pour la cohérence.


# === ROUTES D'AUTHENTIFICATION ==================

@app.post("/api/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur.
    
    Args:
        user_data: Les données d'inscription (username, email, password)
        db: Session de base de données
        
    Returns:
        Un token JWT pour l'authentification automatique après l'inscription
        
    Raises:
        HTTPException 400: Si le nom d'utilisateur ou l'email existe déjà
    """
    # Vérifier si le nom d'utilisateur existe déjà
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà utilisé"
        )
    
    # Vérifier si l'email existe déjà
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    # Créer le nouvel utilisateur
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Créer le token d'accès
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Connexion d'un utilisateur existant.
    
    Args:
        form_data: Les données de connexion (username, password)
        db: Session de base de données
        
    Returns:
        Un token JWT pour l'authentification
        
    Raises:
        HTTPException 401: Si les identifiants sont incorrects
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer le token d'accès
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Récupère les informations de l'utilisateur actuellement connecté.
    
    Args:
        current_user: L'utilisateur actuellement connecté (injecté par la dépendance)
        
    Returns:
        Les informations de l'utilisateur
        
    Raises:
        HTTPException 401: Si l'utilisateur n'est pas authentifié
    """
    return current_user


# ================== ROUTES DE JEU ==================

@app.post("/api/start-game")
def start_game(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Démarre une nouvelle partie et retourne le texte à taper.
    Cette route fonctionne avec ou sans authentification.
    
    Args:
        db: Session de base de données
        current_user: L'utilisateur connecté (optionnel)
        
    Returns:
        Un objet contenant l'ID de session et le texte à taper
    """
    # Charger le fichier JSON des mots
    try:
        with open('static/frequence.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Fichier de mots introuvable")
    
    # Générer un texte aléatoire
    nb_mots = 50
    texte_arr = []
    for _ in range(nb_mots):
        mot = random.choice(data)['label']
        texte_arr.append(mot)
    
    # Créer une session unique
    session_token = str(uuid.uuid4()) ## ressemblera à un truc du genre https://www.uuidgenerator.net/version4 ("f47ac10b-58cc-4372-a567-0e02b2c3d479")
    # On ne pourra "jamais" obtenir deux uuid identiques (122 bits aléatoires réels donc environ 5,32*10^36 possibilités (c'est beaucoup))
    seed = str(random.randint(100000, 999999))
    # la seed permettra de régénérer la même suite de mot au besoin
    
    # Créer la session en BDD (avec ou sans user_id)
    new_session = GameSession(
        user_id=current_user.id if current_user else None,
        session_token=session_token,
        words_sequence=json.dumps(texte_arr),
        seed=seed,
        start_time=datetime.now(),
        expected_end_time=datetime.now() + timedelta(seconds=30),
        is_completed=False
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return {
        'session_id': session_token,
        'texte': texte_arr,
        'user_authenticated': current_user is not None
    }

@app.post("/api/check-word")
def check_word(data: WordCheck, db: Session = Depends(get_db)):
    """
    Vérifie si le mot est tapé est correct.
    Cette route fonctionne avec ou sans authentification.
    
    Args:
        data: Les données de vérification (session_id, word, index)
        db: Session de base de données
        
    Returns:
        Un objet indiquant si le mot est correct et l'index suivant
        
    Raises:
        HTTPException 404: Si la session n'existe pas
        HTTPException 400: Si la session est déjà terminée ou l'index est invalide
    """
    session = db.query(GameSession).filter(GameSession.session_token == data.session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    if session.is_completed:
        raise HTTPException(status_code=400, detail="Session déjà terminée")
    
    texte_arr = json.loads(session.words_sequence)
    
    if data.index >= len(texte_arr):
        raise HTTPException(status_code=400, detail="Index hors limites")
    
    mot_attendu = texte_arr[data.index]
    is_correct = data.word == mot_attendu
    
    # Incrémenter les compteurs côté serveur
    if is_correct:
        session.words_correct_count += 1
    else:
        session.words_wrong_count += 1
    
    db.commit()
    
    return {
        'correct': is_correct,
        'index': data.index + 1
    }

@app.post("/api/end-game")
def end_game(data: GameEnd, db: Session = Depends(get_db)):
    """
    Termine la partie et sauvegarde le score en BDD.
    Cette route fonctionne avec ou sans authentification.
    
    Args:
        data: Les données de fin de partie (session_id, words_correct, words_wrong, final_score)
        db: Session de base de données
        
    Returns:
        Un objet contenant les statistiques de la partie
        
    Raises:
        HTTPException 404: Si la session n'existe pas
        HTTPException 400: Si la session est déjà terminée
    """
    session = db.query(GameSession).filter(GameSession.session_token == data.session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    if session.is_completed:
        raise HTTPException(status_code=400, detail="Session déjà terminée")
    
    # Calculer la durée réelle
    duration = int((datetime.now() - session.start_time).total_seconds())
    if duration > 35:  # Tolérance de 5 secondes
        duration = 30
    
    # Calculer le score côté serveur
    final_score = session.words_correct_count
    
    # Créer le score en BDD
    # user_id sera NULL pour les sessions anonymes, ou l'ID de l'utilisateur connecté
    new_score = Score(
        user_id=session.user_id,  # Peut être NULL pour les joueurs anonymes
        score=final_score,
        words_correct=session.words_correct_count,
        words_wrong=session.words_wrong_count,
        duration=duration,
        created_at=datetime.now()
    )
    
    db.add(new_score)
    db.commit()
    db.refresh(new_score)
    
    # Mettre à jour la session
    session.is_completed = True
    session.score_id = new_score.id
    db.commit()
    
    return {
        'score': final_score,
        'words_correct': session.words_correct_count,
        'words_wrong': session.words_wrong_count,
        'duration': duration
    }


@app.get('/api/ranking')
def ranking(db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user_optional)):
    """
    Retourne le classement global basé sur le meilleur score par joueur.
    Les sessions anonymes (user_id is NULL) sont regroupées sous le pseudo 'Inconnu'.
    Si l'utilisateur est connecté, on retourne également sa position dans le classement.
    """
    from sqlalchemy import func

    # On récupère pour chauqe users, sont score le plus haut
    # Equivalent en SQL :
    # SELECT user_id, max(score) as "best_score"
    # FROM scores
    # GROUP BY user_id
    bests = db.query(Score.user_id, func.max(Score.score).label('best_score'))\
              .group_by(Score.user_id).all()
    # bests ressemble à:
    # [(None, 24), (5, 8), (7, 21), (8, 21), (10, 23)]

    best_map = {row.user_id: row.best_score for row in bests}
    # best_map ressemble à {None: 24, 5: 8, 7: 21, 8: 21, 10: 23}

    results = []

    # Retrouver les usernames selon les ids des joueurs
    if best_map:
        user_ids = [uid for uid in best_map.keys() if uid is not None]
        if user_ids:
            users = db.query(User).filter(User.id.in_(user_ids)).all()
            for u in users:
                results.append({
                    'user_id': u.id,
                    'username': u.username,
                    'best_score': int(best_map.get(u.id, 0))
                })

    # les joueurs sans id sont marqués avec un username "Inconnu"
    anon_best = best_map.get(None)
    if anon_best is not None:
        results.append({
            'user_id': None,
            'username': 'Inconnu',
            'best_score': int(anon_best)
        })

    """
    results ressemble à :
    [
        {'user_id': 5, 'username': 'testtest', 'best_score': 8},
        {'user_id': 7, 'username': 'hjddhsdij', 'best_score': 21},
        {'user_id': 8, 'username': 'Arlette', 'best_score': 21}, 
        ...
    ]
    """

    # Tri du plus grand au plus petit selon le score
    results.sort(key=lambda x: x['best_score'], reverse=True)

    # Construction du ranking : les gens avec le même score sont placés dans la même place
    ranked = []
    rank = 0
    last_score = None
    for item in results:
        if last_score is None or item['best_score'] != last_score:
            rank += 1
            last_score = item['best_score']
        ranked.append({
            'rank': rank,
            **item
        })
        
    """
    ranked ressemble à :
    [
        {'rank': 1, 'user_id': None, 'username': 'Inconnu', 'best_score': 24}, 
        {'rank': 2, 'user_id': 10, 'username': 'jdk', 'best_score': 23}, 
        {'rank': 3, 'user_id': 7, 'username': 'hjddhsdij', 'best_score': 21}
    ]
    """

    # Trouver la position du joueur qui est allé voir le classement
    current_info = None
    if current_user:
        # essayer de trouver le score du joueur connect
        your_best = best_map.get(current_user.id)
        if your_best is None: # si le joueur n'a pas encore de score
            current_info = {'user_id': current_user.id, 'username': current_user.username or 'Inconnu', 'best_score': 0, 'rank': None}
        else:
            for r in ranked:
                if r['user_id'] == current_user.id:
                    current_info = r
                    break
    return {
        'ranking': ranked,
        'current_user': current_info
    }
    
app.mount("/static", StaticFiles(directory="static"), name="static")
    
if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
    
# uvicorn main:app --reload
