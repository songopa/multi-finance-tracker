import { useEffect, useState } from 'react'
import { Pie, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  Title
} from 'chart.js'
import { getEntities } from '../api/entities'
import { getReport } from '../api/reports'
import { Link } from 'react-router-dom'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend, Title)

const COLORS = [
  '#3B82F6',
  '#10B981',
  '#F59E0B',
  '#EF4444',
  '#8B5CF6',
  '#EC4899',
  '#14B8A6',
  '#F97316'
]

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

  const incomeChartData = report && report.income_breakdown.length > 0 ? {
    labels: report.income_breakdown.map(c => c.category_name),
    datasets: [{
      label: 'Income by Category',
      data: report.income_breakdown.map(c => c.total),
      backgroundColor: COLORS.slice(0, report.income_breakdown.length),
      borderColor: COLORS.slice(0, report.income_breakdown.length),
      borderWidth: 2
    }]
  } : null

  const expenseChartData = report && report.expense_breakdown.length > 0 ? {
    labels: report.expense_breakdown.map(c => c.category_name),
    datasets: [{
      label: 'Expenses by Category',
      data: report.expense_breakdown.map(c => c.total),
      backgroundColor: COLORS.slice(0, report.expense_breakdown.length),
      borderColor: COLORS.slice(0, report.expense_breakdown.length),
      borderWidth: 2
    }]
  } : null


  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'bottom'
      }
    }
  }

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

          <div className="charts-grid">

            {incomeChartData && (
              <div className="chart-card">
                <h3>Income by Category</h3>
                <div className="chart-container">
                  <Pie data={incomeChartData} options={chartOptions} />
                </div>
              </div>
            )}

            {expenseChartData && (
              <div className="chart-card">
                <h3>Expenses by Category</h3>
                <div className="chart-container">
                  <Pie data={expenseChartData} options={chartOptions} />
                </div>
              </div>
            )}
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
