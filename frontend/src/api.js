const API_BASE = import.meta.env.VITE_API_BASE || ''

export async function fetchClients({ limit = 100, offset = 0 } = {}) {
  const res = await fetch(`${API_BASE}/api/clients?limit=${limit}&offset=${offset}`, {
    cache: 'no-store'
  })
  if (!res.ok) throw new Error('Failed to fetch clients')
  return res.json()
}

export async function searchClients({ q, fields = 'name,email', limit = 100, offset = 0 }) {
  const res = await fetch(
    `${API_BASE}/api/clients/search?q=${encodeURIComponent(q)}&fields=${fields}&limit=${limit}&offset=${offset}`,
    { cache: 'no-store' }
  )
  if (!res.ok) throw new Error('Search failed')
  return res.json()
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/api/health`, { cache: 'no-store' })
  if (!res.ok) throw new Error('Health failed')
  return res.json()
}
