import pytest
import psycopg
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Ajouter le répertoire parent au path pour importer main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app as application, hacherPassword, verifierPassword

# === Configuration des tests ===
@pytest.fixture
def client():
    """Client de test FastAPI"""
    return TestClient(application)

# === Tests de base ===
def testConnexionDb():
    """Test de connexion à la base de données PostgreSQL"""
    try:
        dbConn = psycopg.connect(
            dbname="2025_M1",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5430"
        )
        dbCur = dbConn.cursor()
        dbCur.execute("SELECT 1")
        result = dbCur.fetchone()
        assert result[0] == 1
        dbCur.close()
        dbConn.close()
    except Exception as e:
        pytest.fail(f"Impossible de se connecter à la base de données: {e}")

def testHacherPassword():
    """Test de hachage des mots de passe"""
    password = "motdepasse123"
    passwordHache = hacherPassword(password)

    assert passwordHache != password
    assert passwordHache.startswith("$2b$")

def testVerifierPassword():
    """Test de vérification des mots de passe"""
    password = "motdepasse123"
    passwordHache = hacherPassword(password)

    assert verifierPassword(password, passwordHache) == True
    assert verifierPassword("mauvais", passwordHache) == False

# === Tests des routes ===
def testRouteAccueil(client):
    """Test de la route d'accueil"""
    response = client.get("/")
    assert response.status_code == 200

def testRouteLoginGet(client):
    """Test d'affichage du formulaire de connexion"""
    response = client.get("/login")
    assert response.status_code == 200
    assert "login" in response.text

def testRouteRegisterGet(client):
    """Test d'affichage du formulaire d'inscription"""
    response = client.get("/register")
    assert response.status_code == 200
    assert "email" in response.text

def testDeconnexion(client):
    """Test de déconnexion"""
    response = client.get("/logout", follow_redirects=False) # Ne pas suivre les redirections pour vérifier le code de statut
    assert response.status_code == 303

# === Tests avec validation ===
@patch('main.obtenirDb') 
def testInscriptionLoginTropCourt(mockDbDependency, client):
    """Test d'inscription avec un login trop court"""
    mockDb = Mock()
    mockDbDependency.return_value.__enter__.return_value = mockDb

    response = client.post("/register", data={
        "login": "ab",
        "email": "test@test.com",
        "password": "password123"
    })

    assert "Le login doit faire au moins 3 caractères" in response.text

@patch('main.obtenirDb')
def testInscriptionPasswordTropCourt(mockDbDependency, client):
    """Test d'inscription avec un mot de passe trop court"""
    mockDb = Mock()
    mockDbDependency.return_value.__enter__.return_value = mockDb

    response = client.post("/register", data={
        "login": "testuser",
        "email": "test@test.com",
        "password": "123"
    })

    assert response.status_code == 200
    assert "Le mot de passe doit faire au moins 6 caractères" in response.text

if __name__ == "__main__":
    pytest.main([__file__])
