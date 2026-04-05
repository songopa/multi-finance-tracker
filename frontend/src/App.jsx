import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Entities from './pages/Entities'
import Categories from './pages/Categories'
import Transactions from './pages/Transactions'
import Reports from './pages/Reports'
import Login from './pages/Login'
import Register from './pages/Register'

function PrivateRoute({ children }) {
  const token = localStorage.getItem('token')
  return token ? children : <Navigate to="/login" replace />
}

function PublicRoute({ children }) {
  const token = localStorage.getItem('token')
  return token ? <Navigate to="/" replace /> : children
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

        <Route path="/" element={<PrivateRoute><Navbar /><Dashboard /></PrivateRoute>} />
        <Route path="/entities" element={<PrivateRoute><Navbar /><Entities /></PrivateRoute>} />
        <Route path="/categories" element={<PrivateRoute><Navbar /><Categories /></PrivateRoute>} />
        <Route path="/transactions" element={<PrivateRoute><Navbar /><Transactions /></PrivateRoute>} />
        <Route path="/reports" element={<PrivateRoute><Navbar /><Reports /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  )
}
