# main.py
from fastapi import FastAPI, Form, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse # permettra de faire des redirections
from fastapi.templating import Jinja2Templates # pour utiliser les templates Jinja2 pour les fichiers HTML (pip install jinja2)
from fastapi.staticfiles import StaticFiles # pour servir les fichiers statiques (CSS, JS, images)
from passlib.context import CryptContext # pour le hachage des mots de passe (pip install passlib[bcrypt])
import psycopg # pour se connecter à PostgreSQL (pip install psycopg[binary])
from psycopg.rows import dict_row # pour obtenir des résultats sous forme de dictionnaire
from starlette.middleware.sessions import SessionMiddleware # pour gérer les sessions utilisateur (pip install starlette)
from datetime import datetime # c'est compris

# === Config FastAPI ===
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="une_clef_secrete_très_longue")


# Servir les fichiers statiques (CSS, JS, images)
# "servir" un fichier = le rendre accessible via une URL
app.mount("/static", StaticFiles(directory="static"), name="static")

modelesTemplates = Jinja2Templates(directory="templates")

# === Config hachage ===
contextePassword = CryptContext(schemes=["bcrypt"], deprecated="auto")

# === Connexion PostgreSQL ===
def obtenirDb():
    with psycopg.connect(
        dbname="2025_M1",
        user="postgres",
        password="postgres",
        host="localhost", 
        port="5430",
        row_factory=dict_row
    ) as connexion:
        yield connexion # yield permet de retourner une valeur tout en garantissant que la connexion sera fermée après usage

# === Utils ===
def verifierPassword(passwordClair, passwordHache):
    return contextePassword.verify(passwordClair, passwordHache)

def hacherPassword(password):
    return contextePassword.hash(password)

def creerSessionUtilisateur(request, utilisateur):
    """Fonction utilitaire pour créer une session utilisateur"""
    request.session["user"] = {
        "id": utilisateur["user_id"], 
        "login": utilisateur["user_login"], 
        "email": utilisateur["user_mail"]
    }

# === Routes ===
@app.get("/", response_class=HTMLResponse)
def accueil(request: Request):
    utilisateur = request.session.get("user")
    return modelesTemplates.TemplateResponse("index.html", {"request": request, "user": utilisateur})

@app.get("/login", response_class=HTMLResponse)
def formulaireConnexion(request: Request):
    utilisateur = request.session.get("user")
    if utilisateur:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return modelesTemplates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def connexion(request: Request, login: str = Form(...), password: str = Form(...), baseDonnees=Depends(obtenirDb)): # Depends() appelle la fonction obtenirDb et fournis son résultat comme argument
    try:
        utilisateur = baseDonnees.execute("SELECT * FROM \"user\" WHERE user_login = %s", (login,)).fetchone()
        if not utilisateur or not verifierPassword(password, utilisateur["user_password"]):
            return modelesTemplates.TemplateResponse("login.html", {"request": request, "error": "Login ou mot de passe incorrect"})
        
        # Mise à jour de la date de dernière connexion
        baseDonnees.execute(
            "UPDATE \"user\" SET user_date_login = %s WHERE user_id = %s",
            (datetime.now(), utilisateur["user_id"])
        )
        baseDonnees.commit()
        
        creerSessionUtilisateur(request, utilisateur)
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    except Exception as erreur:
        baseDonnees.rollback()
        return modelesTemplates.TemplateResponse("login.html", {"request": request, "error": "Erreur de connexion"})

@app.get("/logout")
def deconnexion(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# === Exemple d'inscription rapide ===
@app.get("/register", response_class=HTMLResponse)
def formulaireInscription(request: Request):
    utilisateur = request.session.get("user")
    if utilisateur:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return modelesTemplates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def inscription(request: Request, login: str = Form(...), email: str = Form(...), password: str = Form(...), baseDonnees=Depends(obtenirDb)):
    try:
        # Validation basique des champs
        if len(login.strip()) < 3:
            return modelesTemplates.TemplateResponse("register.html", {
                "request": request, 
                "error": "Le nom d'utilisateur doit faire au moins 3 caractères"
            })
        
        if len(password) < 6:
            return modelesTemplates.TemplateResponse("register.html", {
                "request": request, 
                "error": "Le mot de passe doit faire au moins 6 caractères"
            })
        
        # Vérifier si l'utilisateur existe déjà
        utilisateurExistant = baseDonnees.execute(
            "SELECT user_id FROM \"user\" WHERE user_login = %s OR user_mail = %s", 
            (login, email)
        ).fetchone()
        
        if utilisateurExistant:
            return modelesTemplates.TemplateResponse("register.html", {
                "request": request, 
                "error": "Ce login ou cette adresse email est déjà utilisé(e)"
            })
        
        # Créer l'utilisateur
        passwordHache = hacherPassword(password)
        curseur = baseDonnees.execute(
            "INSERT INTO \"user\" (user_login, user_password, user_mail) VALUES (%s, %s, %s) RETURNING user_id, user_login, user_mail",
            (login, passwordHache, email)
        )
        nouvelUtilisateur = curseur.fetchone()
        baseDonnees.commit()
        
        # Vérifier que l'insertion a réussi
        if nouvelUtilisateur:
            creerSessionUtilisateur(request, nouvelUtilisateur)
            return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return modelesTemplates.TemplateResponse("register.html", {
                "request": request, 
                "error": "Erreur lors de la création du compte"
            })
            
    except psycopg.IntegrityError:
        # Erreur de contrainte (doublon, etc.)
        baseDonnees.rollback()
        return modelesTemplates.TemplateResponse("register.html", {
            "request": request, 
            "error": "Ce login ou cette adresse email est déjà utilisé(e)"
        })
    except Exception as erreur:
        # Autres erreurs de base de données
        baseDonnees.rollback()
        return modelesTemplates.TemplateResponse("register.html", {
            "request": request, 
            "error": "Erreur lors de la création du compte"
        })

# cmd : uvicorn main:app --reload