import { useEffect, useState } from 'react'
import { getEntities, createEntity, deleteEntity } from '../api/entities'

export default function Entities() {
  const [entities, setEntities] = useState([])
  const [form, setForm] = useState({ name: '', description: '', entity_type: '' })
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState(null)

  function load() {
    getEntities().then(setEntities)
  }

  useEffect(() => { load() }, [])

  async function handleCreate(e) {
    e.preventDefault()
    setError(null)
    try {
      await createEntity(form)
      setForm({ name: '', description: '', entity_type: '' })
      setShowForm(false)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create entity')
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this entity and all its transactions?')) return
    await deleteEntity(id)
    load()
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Entities</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ New Entity'}
        </button>
      </div>

      {showForm && (
        <form className="card form-card" onSubmit={handleCreate}>
          <h3>New Entity</h3>
          {error && <p className="error">{error}</p>}
          <input className="input" placeholder="Name *" required value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })} />
          <input className="input" placeholder="Description" value={form.description}
            onChange={e => setForm({ ...form, description: e.target.value })} />
          <select className="select" value={form.entity_type}
            onChange={e => setForm({ ...form, entity_type: e.target.value })}>
            <option value="">Type (optional)</option>
            <option value="personal">Personal</option>
            <option value="freelance">Freelance</option>
            <option value="business">Business</option>
          </select>
          <button className="btn btn-primary" type="submit">Create</button>
        </form>
      )}

      <div className="list">
        {entities.length === 0 && <p className="muted">No entities yet.</p>}
        {entities.map(en => (
          <div key={en.id} className="card list-item">
            <div>
              <strong>{en.name}</strong>
              {en.entity_type && <span className="badge">{en.entity_type}</span>}
              {en.description && <p className="muted small">{en.description}</p>}
            </div>
            <div className="item-actions">
              <span className={`status ${en.is_active ? 'active' : 'inactive'}`}>
                {en.is_active ? 'Active' : 'Inactive'}
              </span>
              <button className="btn btn-danger btn-sm" onClick={() => handleDelete(en.id)}>Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
