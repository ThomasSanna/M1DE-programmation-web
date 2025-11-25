async function fetchRanking() {
  try {
    const response = await fetch('/api/ranking', {
      headers: {
        ...(authToken && { 'Authorization': `Bearer ${authToken}` })
      }
    })

    if (!response.ok) throw new Error('Erreur lors du chargement du classement')

    return await response.json()
  } catch (err) {
    console.error(err)
    return null
  }
}

function renderRanking(containerSelector, data) {
  if (!data) return

  const container = document.querySelector(containerSelector)
  if (!container) return

  container.innerHTML = ''


  if (data.current_user) {
    const you = data.current_user
    const yourTop = document.createElement('div')
    yourTop.className = 'your-position'
    yourTop.innerHTML = `<strong>Votre position :</strong> ${you.rank ? `#${you.rank}` : '—'} — ${escapeHtml(you.username || 'Inconnu')} — ${you.best_score} pts` 
    container.appendChild(yourTop)
  }

  const table = document.createElement('table')
  table.className = 'ranking-table'
  table.innerHTML = `<thead><tr><th>Rang</th><th>Pseudo</th><th>Score</th></tr></thead>`
  const tbody = document.createElement('tbody')

  const currentId = data.current_user ? data.current_user.user_id : (currentUser ? currentUser.id : null)

  data.ranking.forEach(row => {
    const tr = document.createElement('tr')
    if (currentId !== null && row.user_id === currentId) tr.className = 'highlight'
    tr.innerHTML = `<td>#${row.rank}</td><td>${escapeHtml(row.username || 'Inconnu')}</td><td>${row.best_score}</td>`
    tbody.appendChild(tr)
  })

  table.appendChild(tbody)
  container.appendChild(table)
}

function escapeHtml(text){
  return String(text).replace(/[&"'<>]/g, function(m){return {'&':'&amp;','"':'&quot;',"'":"&#39;","<":"&lt;",">":"&gt;"}[m]})
}

async function initClassement(){
  loadAuthToken()
  await checkAuthStatus()
  const data = await fetchRanking()
  renderRanking('#classement-root', data)
}