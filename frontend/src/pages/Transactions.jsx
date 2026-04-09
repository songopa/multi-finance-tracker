import { useEffect, useState } from 'react'
import { getTransactions, createTransaction, deleteTransaction } from '../api/transactions'
import { getEntities } from '../api/entities'
import { getCategories } from '../api/categories'

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [entities, setEntities] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedEntity, setSelectedEntity] = useState('')
  const [filterType, setFilterType] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState(null)
  const [form, setForm] = useState({
    entity_id: '',
    category_id: '',
    transaction_type: 'expense',
    amount: '',
    description: '',
    transaction_date: new Date().toISOString().slice(0, 10),
  })

  useEffect(() => {
    getEntities().then(data => {
      setEntities(data)
      if (data.length > 0) {
        setSelectedEntity(data[0].id)
        setForm(f => ({ ...f, entity_id: data[0].id }))
      }
    })
    getCategories().then(setCategories)
  }, [])

  useEffect(() => {
    if (!selectedEntity) return
    getTransactions({ entity_id: selectedEntity, type: filterType || undefined }).then(setTransactions)
  }, [selectedEntity, filterType])

  const filteredCategories = categories.filter(c => !form.transaction_type || c.type === form.transaction_type)

  async function handleCreate(e) {
    e.preventDefault()
    setError(null)
    try {
      await createTransaction({
        ...form,
        entity_id: Number(form.entity_id),
        category_id: Number(form.category_id),
        amount: Number(form.amount),
        transaction_date: new Date(form.transaction_date).toISOString(),
      })
      setShowForm(false)
      getTransactions({ entity_id: selectedEntity, type: filterType || undefined }).then(setTransactions)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create transaction')
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this transaction?')) return
    await deleteTransaction(id)
    getTransactions({ entity_id: selectedEntity, type: filterType || undefined }).then(setTransactions)
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Transactions</h1>
        <div className="header-actions">
          <select className="select" value={selectedEntity}
            onChange={e => setSelectedEntity(Number(e.target.value))}>
            {entities.map(en => <option key={en.id} value={en.id}>{en.name}</option>)}
          </select>
          <select className="select" value={filterType} onChange={e => setFilterType(e.target.value)}>
            <option value="">All</option>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
          </select>
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : '+ New Transaction'}
          </button>
        </div>
      </div>

      {showForm && (
        <form className="card form-card" onSubmit={handleCreate}>
          <h3>New Transaction</h3>
          {error && <p className="error">{error}</p>}
          <select className="select" required value={form.entity_id}
            onChange={e => setForm({ ...form, entity_id: e.target.value })}>
            <option value="">Select Entity *</option>
            {entities.map(en => <option key={en.id} value={en.id}>{en.name}</option>)}
          </select>
          <select className="select" value={form.transaction_type}
            onChange={e => setForm({ ...form, transaction_type: e.target.value, category_id: '' })}>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
          </select>
          <select className="select" required value={form.category_id}
            onChange={e => setForm({ ...form, category_id: e.target.value })}>
            <option value="">Select Category *</option>
            {filteredCategories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <input className="input" type="number" placeholder="Amount *" required min="0.01" step="0.01"
            value={form.amount} onChange={e => setForm({ ...form, amount: e.target.value })} />
          <input className="input" type="date" required value={form.transaction_date}
            onChange={e => setForm({ ...form, transaction_date: e.target.value })} />
          <input className="input" placeholder="Description" value={form.description}
            onChange={e => setForm({ ...form, description: e.target.value })} />
          <button className="btn btn-primary" type="submit">Add Transaction</button>
        </form>
      )}

      <div className="list">
        {transactions.length === 0 && <p className="muted">No transactions yet.</p>}
        {transactions.map(t => (
          <div key={t.id} className="card list-item">
            <div>
              <div className="transaction-header">
                <strong>{t.category.name}</strong>
                <span className={`amount ${t.transaction_type === 'income' ? 'income-text' : 'expense-text'}`}>
                  {t.transaction_type === 'income' ? '+' : '-'}${t.amount.toLocaleString()}
                </span>
              </div>
              {t.description && <p className="muted small">{t.description}</p>}
              <p className="muted small">{new Date(t.transaction_date).toLocaleDateString()}</p>
            </div>
            <button className="btn btn-danger btn-sm" onClick={() => handleDelete(t.id)}>Delete</button>
          </div>
        ))}
      </div>
    </div>
  )
}
