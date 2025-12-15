"""
Module d'authentification pour l'application Dactylogame.

Ce module fournit toutes les fonctionnalités liées à l'authentification des utilisateurs :
- Hashage et vérification des mots de passe
- Création et validation des tokens JWT
- Gestion des sessions utilisateur
"""

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db, User

# config du contexte de hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# xonfig OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

# config JWT
SECRET_KEY = "LACLESIUJSDIDFOS"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # 30 jours


def hash_password(password: str) -> str:
    """
    Hash un mot de passe en utilisant bcrypt.
    
    Args:
        password: Le mot de passe en clair
        
    Returns:
        Le mot de passe hashé
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe en clair correspond à son hash.
    
    Args:
        plain_password: Le mot de passe en clair à vérifier
        hashed_password: Le hash du mot de passe stocké
        
    Returns:
        True si le mot de passe est correct, False sinon
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT pour l'authentification.
    
    Args:
        data: Les données à encoder dans le token (typiquement {"sub": user_id})
        expires_delta: Durée de validité du token (optionnel)
        
    Returns:
        Le token JWT encodé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authentifie un utilisateur avec son nom d'utilisateur et mot de passe.
    
    Args:
        db: Session de base de données
        username: Nom d'utilisateur
        password: Mot de passe en clair
        
    Returns:
        L'objet User si l'authentification réussit, None sinon
    """
    # requete : chercher un seul utilisateur ayant ce nom d'utilisateur
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Récupère l'utilisateur actuel depuis le token JWT (optionnel).
    Cette fonction ne lève pas d'exception si le token est absent ou invalide.
    
    Args:
        token: Le token JWT (optionnel)
        db: Session de base de données
        
    Returns:
        L'objet User si authentifié, None sinon
    """
    if token is None:
        return None
    
    try:
        # ex token: token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImV4cCI6MTc2ODMyMDg1Mn0.sJvEML1HnBlAbkBHaA0wRaWY0ETkvUIXq8BhMcVMmvM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
            
    except JWTError:
        return None
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Récupère l'utilisateur actuel depuis le token JWT (obligatoire).
    Cette fonction lève une exception si le token est absent ou invalide.
    
    Args:
        token: Le token JWT
        db: Session de base de données
        
    Returns:
        L'objet User
        
    Raises:
        HTTPException: Si le token est invalide ou l'utilisateur n'existe pas
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Infos d'auth invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if token is None:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None:
        raise credentials_exception
    
    return user
