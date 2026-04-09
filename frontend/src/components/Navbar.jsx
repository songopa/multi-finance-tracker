import { NavLink, useNavigate } from 'react-router-dom'

export default function Navbar() {
  const navigate = useNavigate()

  function logout() {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <span className="navbar-brand">MultiFinance</span>
      <div className="navbar-links">
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/entities">Entities</NavLink>
        <NavLink to="/categories">Categories</NavLink>
        <NavLink to="/transactions">Transactions</NavLink>
        <NavLink to="/reports">Reports</NavLink>
      </div>
      <button className="btn btn-ghost" onClick={logout}>Logout</button>
    </nav>
  )
}
