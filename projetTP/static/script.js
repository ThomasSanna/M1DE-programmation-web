// Fonction lancée au chargement de la page : Initialise l'application (jeu + auth)
async function initApp() {
  // Charge le token depuis le localStorage
  loadAuthToken()
  // Vérifie si l'utilisateur est connecté
  await checkAuthStatus()
  // Charge un texte aléatoire pour commencer la partie
  randomText()
}

// var globales pour le jeu
let indexTexte = 0
let motWin = []
let motLost = []
let texteArr = []
let texte = ""
let score = 0
let sessionId = null

// var globales pour l'auth
let currentUser = null
let authToken = null


// --------- FONCTIONS AUTH ------

// charge le token d'auth depuis le localStorage
function loadAuthToken() {
  authToken = localStorage.getItem('authToken')
}

// Met le token d'auth dans le localStorage
function saveAuthToken(token) {
  authToken = token
  localStorage.setItem('authToken', token)
}

// Clear le token d'auth 
function clearAuthToken() {
  authToken = null
  localStorage.removeItem('authToken')
}

// vérifie si l'utilisateur est connecté
async function checkAuthStatus() {
  if (!authToken) {
    updateUIForLoggedOut()
    return
  }

  try {
    const response = await fetch('/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    })

    if (response.ok) {
      currentUser = await response.json()
      updateUIForLoggedIn()
    } else {
      clearAuthToken()
      updateUIForLoggedOut()
    }
  } catch (error) {
    console.error('Erreur lors de la vérification du statut d\'authentification:', error)
    clearAuthToken()
    updateUIForLoggedOut()
  }
}

// Met à jour l'interface quand connecté
function updateUIForLoggedIn() {
  const loggedOutEl = document.getElementById('auth-logged-out');
  const loggedInEl = document.getElementById('auth-logged-in');
  const usernameEl = document.getElementById('username-display');

  if (loggedOutEl) loggedOutEl.style.display = 'none';
  if (loggedInEl) loggedInEl.style.display = 'flex';
  if (usernameEl) usernameEl.textContent = currentUser.username;
}

// mets l'interface en mode déconnecté
function updateUIForLoggedOut() {
  const loggedOutEl = document.getElementById('auth-logged-out');
  const loggedInEl = document.getElementById('auth-logged-in');
  if (loggedOutEl) loggedOutEl.style.display = 'flex';
  if (loggedInEl) loggedInEl.style.display = 'none';
  currentUser = null
}

// Affiche le modal de connexion
function showLoginModal() {
  document.getElementById('login-modal').style.display = 'flex'
  document.getElementById('login-error').textContent = ''
}

// ferme le modal de connexion
function closeLoginModal() {
  document.getElementById('login-modal').style.display = 'none'
  document.getElementById('login-form').reset()
}

// Affiche le modal d'inscription
function showRegisterModal() {
  document.getElementById('register-modal').style.display = 'flex'
  document.getElementById('register-error').textContent = ''
}

// ferme le modal d'inscription
function closeRegisterModal() {
  document.getElementById('register-modal').style.display = 'none'
  document.getElementById('register-form').reset()
}

// Traite la connexion
async function handleLogin(event) {
  event.preventDefault()
  
  const formData = new FormData(event.target)
  const loginData = new URLSearchParams()
  loginData.append('username', formData.get('username'))
  loginData.append('password', formData.get('password'))

  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: loginData
    })

    if (response.ok) {
      const data = await response.json()
      saveAuthToken(data.access_token)
      await checkAuthStatus()
      closeLoginModal()
      window.location.reload()
    } else {
      const error = await response.json()
      document.getElementById('login-error').textContent = error.detail || 'Erreur lors de la connexion'
    }
  } catch (error) {
    console.error('Erreur lors de la connexion:', error)
    document.getElementById('login-error').textContent = 'Erreur lors de la connexion'
  }
}

// traite l'inscription
async function handleRegister(event) {
  event.preventDefault()
  
  const formData = new FormData(event.target)
  const registerData = {
    username: formData.get('username'),
    email: formData.get('email'),
    password: formData.get('password')
  }

  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(registerData)
    })

    if (response.ok) {
      const data = await response.json()
      saveAuthToken(data.access_token)
      await checkAuthStatus()
      closeRegisterModal()
      window.location.reload()
    } else {
      const error = await response.json()
      document.getElementById('register-error').textContent = error.detail || 'Erreur lors de l\'inscription'
    }
  } catch (error) {
    console.error('Erreur lors de l\'inscription:', error)
    document.getElementById('register-error').textContent = 'Erreur lors de l\'inscription'
  }
}

// Déconnecte l'utilisateur
function logout() {
  clearAuthToken()
  updateUIForLoggedOut()
}


// ================== FONCTIONS DE JEU ==================

// lance une partie
function lancerPartie(){
  launchGame()
}

// Recharge la page pour rejouer
function rejouer(){
  window.location.reload()
}

// démarre le chrono et le jeu
function launchGame(){
  document.querySelector('.btnCommencer').style.display = 'none'

  let start = 4
  document.querySelector('.startC').innerHTML = "Lancement de la partie..."
  let startInterval = setInterval(() => {
    document.querySelector('.startC').innerHTML = start==4 ? "Prêt ?" : start
    start--
    if(start < 0){
      clearInterval(startInterval)
      document.querySelector('.startC').innerHTML = ""
      document.querySelector('#texteEntrer').style.display = 'block'
      document.querySelector('#texteEntrer').focus()

      let chrono = 29
      document.querySelector('.chrono').innerHTML = 30
      let chronoInterval = setInterval(() => {
        document.querySelector('.chrono').innerHTML = chrono<-1 ? 0 : chrono
        chrono--
        if(chrono < -1){
          finPartie()
          clearInterval(chronoInterval)
        }
      }, 1000);
    }
  }, 1000);
}

// Termine la partie et envoie les stats
function finPartie(){
  document.querySelector('.chrono').innerHTML = ""
  document.querySelector('#texteEntrer').style.display = 'none'
  document.querySelector('#texteEntrer').value = ""
  document.querySelector('.finPartie').style.display = 'flex'
  document.querySelector('.btnPage').style.display = 'flex'

  // Envoyer la fin de partie au serveur (le score est calculé côté serveur, sécurisé)
  fetch("/api/end-game", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(authToken && { 'Authorization': `Bearer ${authToken}` })
    },
    body: JSON.stringify({
      session_id: sessionId
    })
  })
    .then(response => response.json())
    .then(data => {
      document.querySelector('.messageFin').innerHTML = `Partie terminée !`
      document.querySelector('.scoresFin').innerHTML = `Votre score : ${data.score} point(s)<br>Mots corrects : ${data.words_correct}<br>Mots incorrects : ${data.words_wrong}`
    })
    .catch(error => {
      console.error('Erreur lors de la fin de partie:', error)
      document.querySelector('.messageFin').innerHTML = `Partie terminée !`
      document.querySelector('.scoresFin').innerHTML = `Votre score : ${score} point(s)`
    })
}

// convertit tableau de mots en chaîne
function arrToString(arr){
  return arr.join(' ')
}

// Convertit chaîne en tableau de mots
// ex: "Bonjour à tous" => ["Bonjour", "à", "tous"]
function stringToArr(str){
  return str.split(' ')
}

// demande un texte aléatoire et init la partie
function randomText(){
  fetch("/api/start-game", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(authToken && { 'Authorization': `Bearer ${authToken}` })
    }
  })
    .then(response => response.json())
    .then(data => {
      sessionId = data.session_id
      texteArr = data.texte
      texte = arrToString(texteArr)
      affichageTexte()
    })
    .catch(error => {
      console.error('Erreur lors du démarrage de la partie:', error)
      alert('Erreur lors du démarrage de la partie')
    })
}

// Gère la saisie et valide les mots
function taptap(){
  if(event.key == ' ' || event.key == 'Enter'){
    let texteEntrer = document.querySelector('#texteEntrer')
    let motTape = texteEntrer.value.split(' ')[0]
    
    // Envoyer le mot au serveur pour validation
    fetch("/api/check-word", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authToken && { 'Authorization': `Bearer ${authToken}` })
      },
      body: JSON.stringify({
        session_id: sessionId,
        word: motTape,
        index: indexTexte
      })
    })
      .then(response => response.json())
      .then(data => {
        if(data.correct){
          motWin.push(indexTexte)
          score++
        } else {
          motLost.push(indexTexte)
        }
        document.querySelector('#scoreJoueur').innerHTML = score
        indexTexte = data.index
        texteEntrer.value = ""
        affichageTexte()
      })
      .catch(error => {
        console.error('Erreur lors de la validation du mot:', error)
      })
  }
}

// affiche texte avec couleurs mots
function affichageTexte(){
  let textePlacer = document.querySelector('#textePlacer')
  let textePlacerArr = []
  for(let i = Math.max(indexTexte-1, 0); i < texteArr.length; i++){
    if(motWin.includes(i)){
      textePlacerArr.push(`<span class='surligneVert'>${texteArr[i]}</span>`)
    } else if(motLost.includes(i)){
      textePlacerArr.push(`<span class='surligneRouge'>${texteArr[i]}</span>`)
    } else if (i == indexTexte){
      textePlacerArr.push(`<span class='enBorder'>${texteArr[i]}</span>`)
    } else{
      textePlacerArr.push(`<span>${texteArr[i]}</span>`)
    }
  }
  textePlacer.innerHTML = arrToString(textePlacerArr)
}

// Ferme le panneau de fin de partie
function closeFinPartie(){
  document.querySelector('.finPartie').style.display = 'none'
}