from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Configuration de la base de données
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/dactylogame"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() # permettra de créer les modèles

# Models SQLAlchemy
class User(Base):
    __tablename__ = "users" # la table mysql associée
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    # relationship permet de lier une table à une autre dans le but de faciliter les jointures.
    # la mise en place des foreign keys dans les autres tables permet de faire le lien entre les tables.
    game_sessions = relationship("GameSession", back_populates="user")
    # au dessus, il faudra mettre un foreign key dans l'attribut user_id de la table GameSession pour que l'ORM comprenne automatiquement le lien entre les deux tables.
    scores = relationship("Score", back_populates="user")


class GameSession(Base):
    __tablename__ = "game_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    session_token = Column(String(64), unique=True, nullable=False, index=True)
    words_sequence = Column(Text, nullable=False)  # JSON stringifié des mots
    seed = Column(String(32), nullable=False)
    start_time = Column(DateTime, default=datetime.now)
    expected_end_time = Column(DateTime, nullable=False)
    is_completed = Column(Boolean, default=False)
    score_id = Column(Integer, ForeignKey("scores.id", ondelete="SET NULL"), nullable=True)
    words_correct_count = Column(Integer, default=0)  # Compteur sécurisé côté serveur
    words_wrong_count = Column(Integer, default=0)  # Compteur sécurisé côté serveur
    
    # Relations
    user = relationship("User", back_populates="game_sessions")
    score = relationship("Score", back_populates="game_session", foreign_keys=[score_id])


class Score(Base):
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # Nullable pour les joueurs anonymes
    score = Column(Integer, default=0)
    words_correct = Column(Integer, default=0)
    words_wrong = Column(Integer, default=0)
    duration = Column(Integer, default=30, comment="Durée en secondes")
    created_at = Column(DateTime, default=datetime.now)
    
    # Relations
    user = relationship("User", back_populates="scores")
    game_session = relationship("GameSession", back_populates="score", foreign_keys="GameSession.score_id")


# Fonction pour obtenir une session de BDD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
