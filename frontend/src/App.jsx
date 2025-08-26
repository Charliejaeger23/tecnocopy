import { useEffect, useState } from 'react'
import { fetchClients } from './api'

export default function App() {
  const [rows, setRows] = useState([])

  async function load() {
    try {
      const data = await fetchClients({})
      setRows(data)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    load()
    const id = setInterval(load, 15000)
    return () => clearInterval(id)
  }, [])

  return (
    <div>
      <h1>Clientes</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Email</th>
            <th>Teléfono</th>
            <th>Actualizado</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.client_id}>
              <td>{r.client_id}</td>
              <td>{r.name}</td>
              <td>{r.email}</td>
              <td>{r.phone}</td>
              <td>{r.updated_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
