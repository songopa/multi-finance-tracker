import { useEffect, useState } from 'react'
import { getCategories, createCategory, deleteCategory } from '../api/categories'

export default function Categories() {
  const [categories, setCategories] = useState([])
  const [filter, setFilter] = useState('')
  const [form, setForm] = useState({ name: '', description: '', type: 'expense' })
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState(null)

  function load() {
    getCategories(filter || undefined).then(setCategories)
  }

  useEffect(() => { load() }, [filter])

  async function handleCreate(e) {
    e.preventDefault()
    setError(null)
    try {
      await createCategory(form)
      setForm({ name: '', description: '', type: 'expense' })
      setShowForm(false)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create category')
    }
  }

  async function handleDelete(id) {
    try {
      await deleteCategory(id)
      load()
    } catch (err) {
      alert(err.response?.data?.detail || 'Cannot delete category')
    }
  }

  const income = categories.filter(c => c.type === 'income')
  const expense = categories.filter(c => c.type === 'expense')

  return (
    <div className="page">
      <div className="page-header">
        <h1>Categories</h1>
        <div className="header-actions">
          <select className="select" value={filter} onChange={e => setFilter(e.target.value)}>
            <option value="">All</option>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
          </select>
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : '+ New Category'}
          </button>
        </div>
      </div>

      {showForm && (
        <form className="card form-card" onSubmit={handleCreate}>
          <h3>New Category</h3>
          {error && <p className="error">{error}</p>}
          <input className="input" placeholder="Name *" required value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })} />
          <input className="input" placeholder="Description" value={form.description}
            onChange={e => setForm({ ...form, description: e.target.value })} />
          <select className="select" value={form.type}
            onChange={e => setForm({ ...form, type: e.target.value })}>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
          </select>
          <button className="btn btn-primary" type="submit">Create</button>
        </form>
      )}

      <div className="breakdown-grid">
        <div className="breakdown-card">
          <h3>Income Categories</h3>
          {income.length === 0 ? <p className="muted">None yet</p> : income.map(c => (
            <div key={c.id} className="card list-item">
              <div>
                <strong>{c.name}</strong>
                {c.description && <p className="muted small">{c.description}</p>}
              </div>
              <button className="btn btn-danger btn-sm" onClick={() => handleDelete(c.id)}>Delete</button>
            </div>
          ))}
        </div>
        <div className="breakdown-card">
          <h3>Expense Categories</h3>
          {expense.length === 0 ? <p className="muted">None yet</p> : expense.map(c => (
            <div key={c.id} className="card list-item">
              <div>
                <strong>{c.name}</strong>
                {c.description && <p className="muted small">{c.description}</p>}
              </div>
              <button className="btn btn-danger btn-sm" onClick={() => handleDelete(c.id)}>Delete</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
