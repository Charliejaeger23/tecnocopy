// frontend/src/App.jsx
import { useEffect, useState } from 'react'
import { fetchClients, searchClients, fetchHealth } from './api'
import { Toaster } from 'react-hot-toast'

const PAGE_SIZE = 50

export default function App() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(false)
  const [q, setQ] = useState('')
  const [page, setPage] = useState(0)
  const [lastSync, setLastSync] = useState('')
  const [sort, setSort] = useState({ field: 'updated_at', dir: 'desc' })

  async function load() {
    setLoading(true)
    try {
      const data = q
        ? await searchClients({ q, limit: PAGE_SIZE, offset: page * PAGE_SIZE })
        : await fetchClients({ limit: PAGE_SIZE, offset: page * PAGE_SIZE })

      data.sort((a, b) => {
        const v1 = a[sort.field]
        const v2 = b[sort.field]
        return sort.dir === 'asc'
          ? String(v1).localeCompare(String(v2))
          : String(v2).localeCompare(String(v1))
      })
      setRows(data)
    } finally {
      setLoading(false)
    }
  }

  // usa fetchHealth para que no quede “sin usar”
  useEffect(() => {
    fetchHealth().then((h) => {
      // si tu /api/health devuelve {status:"ok"}
      setLastSync(h && h.status ? 'ok' : 'unknown')
    }).catch(() => setLastSync('unknown'))
  }, [])

  useEffect(() => { load() }, [q, page, sort])

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif' }}>
      <Toaster />
      <h1>Tekno Sync</h1>

      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <input
          placeholder="Buscar..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <select
          value={`${sort.field}:${sort.dir}`}
          onChange={(e) => {
            const [field, dir] = e.target.value.split(':')
            setSort({ field, dir })
          }}
        >
          <option value="updated_at:desc">Recientes</option>
          <option value="updated_at:asc">Antiguos</option>
        </select>
        <button onClick={() => setPage((p) => Math.max(0, p - 1))}>Prev</button>
        <button onClick={() => setPage((p) => p + 1)}>Next</button>
      </div>

      <div style={{ marginBottom: 8 }}>
        Estado: {loading ? 'Cargando…' : `Filas: ${rows.length}`} · Health: {lastSync}
      </div>

      <table border="1" cellPadding="6">
        <thead>
          <tr>
            <th>#</th>
            <th>Referencia</th>
            <th>Nombre</th>
            <th>Actualizado</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={`${r.id ?? r.full_reference ?? i}`}>
              <td>{page * PAGE_SIZE + i + 1}</td>
              <td>{r.full_reference ?? r.reference ?? '-'}</td>
              <td>{r.name ?? r.title ?? '-'}</td>
              <td>{r.updated_at ?? r.date ?? '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
