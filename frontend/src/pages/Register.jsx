import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import client from '../api/client'

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', username: '', full_name: '', password: '', confirm_password: '' })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    if (form.password !== form.confirm_password) {
      setError('Passwords do not match')
      return
    }
    setLoading(true)
    try {
      await client.post('/auth/register', form)
      // Auto login after register
      const res = await client.post('/auth/login', { email: form.email, password: form.password })
      localStorage.setItem('token', res.data.access_token)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">MultiFinance</h1>
        <p className="auth-subtitle">Create your account</p>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="alert alert-error">{error}</div>}
          <div className="field">
            <label>Full Name</label>
            <input className="input" type="text" value={form.full_name}
              onChange={e => setForm({ ...form, full_name: e.target.value })} />
          </div>
          <div className="field">
            <label>Email</label>
            <input className="input" type="email" required
              value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
          </div>
          <div className="field">
            <label>Username</label>
            <input className="input" type="text" required minLength={3}
              value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
          </div>
          <div className="field">
            <label>Password</label>
            <input className="input" type="password" required minLength={8}
              value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
          </div>
          <div className="field">
            <label>Confirm Password</label>
            <input className="input" type="password" required minLength={8}
              value={form.confirm_password} onChange={e => setForm({ ...form, confirm_password: e.target.value })} />
          </div>
          <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
