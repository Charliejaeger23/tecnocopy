export async function fetchClients({ limit = 100, offset = 0 } = {}) {
  const res = await fetch(`/api/clients?limit=${limit}&offset=${offset}`, {
    cache: 'no-store'
  })
  if (!res.ok) throw new Error('Failed to fetch clients')
  return res.json()
}
