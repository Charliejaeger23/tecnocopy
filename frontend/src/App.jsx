import { useEffect, useState } from 'react'
import { fetchClients, searchClients, fetchHealth } from './api'
import toast, { Toaster } from 'react-hot-toast'

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
        return sort.dir === 'asc' ? String(v1).localeCompare(String(v2)) : String(v2).localeCompare(String(v1))
      })
      setRows(data)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function loadHealth() {
    try {
      const h = await fetchHealth()
      setLastSync(h.last_sync_at || '')
    } catch (err) {
      toast.error('Health check failed')
    }
  }

  useEffect(() => {
    load()
    loadHealth()
  }, [page, q])

  useEffect(() => {
    const id = setInterval(() => {
      load()
      loadHealth()
    }, 15000)
    return () => clearInterval(id)
  })

  function exportCsv() {
    const headers = ['client_id', 'name', 'email', 'phone', 'address', 'updated_at']
    const csv = [headers.join(',')]
    rows.forEach(r => {
      csv.push(headers.map(h => JSON.stringify(r[h] || '')).join(','))
    })
    const blob = new Blob([csv.join('\n')], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'clientes.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="p-4">
      <Toaster position="top-right" />
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
        <h1 className="text-2xl font-bold">Clientes</h1>
        <div className="text-sm text-gray-600">Última sync: {lastSync}</div>
      </div>
      <div className="flex flex-col sm:flex-row gap-2 mb-4">
        <input
          value={q}
          onChange={e => setQ(e.target.value)}
          placeholder="Buscar..."
          className="border p-2 flex-1"
        />
        <button onClick={exportCsv} className="bg-blue-500 text-white px-3 py-2 rounded">
          Exportar CSV
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2 text-left cursor-pointer" onClick={() => setSort({ field: 'client_id', dir: sort.dir === 'asc' ? 'desc' : 'asc' })}>ID</th>
              <th className="p-2 text-left cursor-pointer" onClick={() => setSort({ field: 'name', dir: sort.dir === 'asc' ? 'desc' : 'asc' })}>Nombre</th>
              <th className="p-2 text-left hidden md:table-cell cursor-pointer" onClick={() => setSort({ field: 'email', dir: sort.dir === 'asc' ? 'desc' : 'asc' })}>Email</th>
              <th className="p-2 text-left hidden md:table-cell cursor-pointer" onClick={() => setSort({ field: 'phone', dir: sort.dir === 'asc' ? 'desc' : 'asc' })}>Teléfono</th>
              <th className="p-2 text-left cursor-pointer" onClick={() => setSort({ field: 'updated_at', dir: sort.dir === 'asc' ? 'desc' : 'asc' })}>Actualizado</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="5" className="p-4">
                  <div className="animate-pulse h-4 bg-gray-200" />
                </td>
              </tr>
            ) : (
              rows.map(r => (
                <tr key={r.client_id} className="border-b">
                  <td className="p-2">{r.client_id}</td>
                  <td className="p-2">{r.name}</td>
                  <td className="p-2 hidden md:table-cell">{r.email}</td>
                  <td className="p-2 hidden md:table-cell">{r.phone}</td>
                  <td className="p-2">{r.updated_at}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-4 flex gap-2">
        <button
          onClick={() => setPage(p => Math.max(0, p - 1))}
          className="px-3 py-1 border rounded"
          disabled={page === 0}
        >
          Prev
        </button>
        <span>Página {page + 1}</span>
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={rows.length < PAGE_SIZE}
          className="px-3 py-1 border rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  )
}
