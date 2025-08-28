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
      const data =
        q
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
    } catch (e) {
      toast.error(String(e.message || e))
      setRows([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [q, page, sort])

  // ... resto del componente sin markers
}
