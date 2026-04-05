import { useEffect, useState } from 'react'
import { getReport } from '../api/reports'
import { getEntities } from '../api/entities'

export default function Reports() {
  const [entities, setEntities] = useState([])
  const [selectedEntity, setSelectedEntity] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    getEntities().then(data => {
      setEntities(data)
      if (data.length > 0) setSelectedEntity(data[0].id)
    })
  }, [])

  function handleGenerate(e) {
    e.preventDefault()
    if (!selectedEntity) return
    setLoading(true)
    setError(null)
    const params = { entity_id: selectedEntity }
    if (dateFrom) params.date_from = new Date(dateFrom).toISOString()
    if (dateTo) params.date_to = new Date(dateTo).toISOString()
    getReport(params)
      .then(setReport)
      .catch(() => setError('Failed to generate report'))
      .finally(() => setLoading(false))
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Reports</h1>
      </div>

      <form className="card form-card" onSubmit={handleGenerate}>
        <div className="form-row">
          <select className="select" value={selectedEntity}
            onChange={e => setSelectedEntity(Number(e.target.value))}>
            {entities.map(en => <option key={en.id} value={en.id}>{en.name}</option>)}
          </select>
          <input className="input" type="date" placeholder="From" value={dateFrom}
            onChange={e => setDateFrom(e.target.value)} />
          <input className="input" type="date" placeholder="To" value={dateTo}
            onChange={e => setDateTo(e.target.value)} />
          <button className="btn btn-primary" type="submit">Generate</button>
        </div>
      </form>

      {loading && <p className="loading">Generating report...</p>}
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
              <h3>Income Breakdown</h3>
              {report.income_breakdown.length === 0
                ? <p className="muted">No income in this period</p>
                : <ul className="breakdown-list">
                    {report.income_breakdown.map(c => (
                      <li key={c.category_id}>
                        <span>{c.category_name} <span className="muted">({c.transaction_count})</span></span>
                        <span className="income-text">${c.total.toLocaleString()}</span>
                      </li>
                    ))}
                  </ul>
              }
            </div>
            <div className="breakdown-card">
              <h3>Expense Breakdown</h3>
              {report.expense_breakdown.length === 0
                ? <p className="muted">No expenses in this period</p>
                : <ul className="breakdown-list">
                    {report.expense_breakdown.map(c => (
                      <li key={c.category_id}>
                        <span>{c.category_name} <span className="muted">({c.transaction_count})</span></span>
                        <span className="expense-text">${c.total.toLocaleString()}</span>
                      </li>
                    ))}
                  </ul>
              }
            </div>
          </div>
        </>
      )}
    </div>
  )
}
