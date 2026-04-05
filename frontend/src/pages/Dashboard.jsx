import { useEffect, useState } from 'react'
import { getEntities } from '../api/entities'
import { getReport } from '../api/reports'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const [entities, setEntities] = useState([])
  const [selectedEntity, setSelectedEntity] = useState(null)
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    getEntities().then((data) => {
      setEntities(data)
      if (data.length > 0) setSelectedEntity(data[0])
    })
  }, [])

  useEffect(() => {
    if (!selectedEntity) return
    setLoading(true)
    setError(null)
    getReport({ entity_id: selectedEntity.id })
      .then(setReport)
      .catch(() => setError('Failed to load report'))
      .finally(() => setLoading(false))
  }, [selectedEntity])

  if (entities.length === 0) {
    return (
      <div className="page">
        <div className="empty-state">
          <h2>Welcome to MultiFinance</h2>
          <p>Create your first entity to get started.</p>
          <Link to="/entities" className="btn btn-primary">Create Entity</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <select
          className="select"
          value={selectedEntity?.id || ''}
          onChange={(e) => setSelectedEntity(entities.find(en => en.id === Number(e.target.value)))}
        >
          {entities.map(en => <option key={en.id} value={en.id}>{en.name}</option>)}
        </select>
      </div>

      {loading && <p className="loading">Loading...</p>}
      {error && <p className="error">{error}</p>}

      {report && (
        <>
          <div className="stats-grid">
            <div className="stat-card income">
              <span className="stat-label">Total Income</span>
              <span className="stat-value">${report.total_income.toLocaleString()}</span>
            </div>
            <div className="stat-card expense">
              <span className="stat-label">Total Expenses</span>
              <span className="stat-value">${report.total_expenses.toLocaleString()}</span>
            </div>
            <div className={`stat-card ${report.net_balance >= 0 ? 'positive' : 'negative'}`}>
              <span className="stat-label">Net Balance</span>
              <span className="stat-value">${report.net_balance.toLocaleString()}</span>
            </div>
          </div>

          <div className="breakdown-grid">
            <div className="breakdown-card">
              <h3>Income by Category</h3>
              {report.income_breakdown.length === 0 ? <p className="muted">No income recorded</p> : (
                <ul className="breakdown-list">
                  {report.income_breakdown.map(c => (
                    <li key={c.category_id}>
                      <span>{c.category_name}</span>
                      <span className="amount income-text">${c.total.toLocaleString()}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="breakdown-card">
              <h3>Expenses by Category</h3>
              {report.expense_breakdown.length === 0 ? <p className="muted">No expenses recorded</p> : (
                <ul className="breakdown-list">
                  {report.expense_breakdown.map(c => (
                    <li key={c.category_id}>
                      <span>{c.category_name}</span>
                      <span className="amount expense-text">${c.total.toLocaleString()}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
