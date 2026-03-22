import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authAPI } from '../api/auth'

export default function RegisterPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)
  const [email, setEmail] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [sex, setSex] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setLoading(true)

    try {
      const response = await authAPI.register({
        email,
        display_name: displayName,
        password,
        sex: sex || undefined,
      })
      setAuth(null, response.access_token)
      const userInfo = await authAPI.getCurrentUser()
      setAuth(
        {
          id: userInfo.id,
          email: userInfo.email,
          display_name: userInfo.display_name,
          is_active: userInfo.is_active,
          is_admin: userInfo.is_admin,
        },
        response.access_token
      )
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const inputStyle = { width: '100%', padding: '0.5rem 0.75rem', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#ffffff', fontSize: '0.875rem', boxSizing: 'border-box' as const }
  const labelStyle = { display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#9ca3af', marginBottom: '0.25rem' }

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', backgroundColor: '#030712' }}>
      <div style={{ width: '100%', maxWidth: '28rem', padding: '2rem', backgroundColor: '#111827', borderRadius: '0.75rem', border: '1px solid #1f2937' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem', textAlign: 'center', color: '#ffffff' }}>Create Account</h1>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label htmlFor="email" style={labelStyle}>Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={inputStyle}
            />
          </div>

          <div>
            <label htmlFor="displayName" style={labelStyle}>Display Name</label>
            <input
              id="displayName"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              required
              style={inputStyle}
            />
          </div>

          <div>
            <label htmlFor="sex" style={labelStyle}>Sex <span style={{ color: '#6b7280', fontWeight: 400 }}>(optional — used for reference ranges)</span></label>
            <select
              id="sex"
              value={sex}
              onChange={(e) => setSex(e.target.value)}
              style={{ ...inputStyle, backgroundColor: '#1f2937' }}
            >
              <option value="">Prefer not to say</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
            </select>
          </div>

          <div>
            <label htmlFor="password" style={labelStyle}>Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={inputStyle}
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" style={labelStyle}>Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              style={inputStyle}
            />
          </div>

          {error && (
            <div style={{ padding: '0.75rem', backgroundColor: '#7f1d1d', color: '#fca5a5', borderRadius: '0.375rem', fontSize: '0.875rem' }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{ width: '100%', padding: '0.5rem', backgroundColor: loading ? '#374151' : '#2563eb', color: '#ffffff', borderRadius: '0.375rem', border: 'none', cursor: loading ? 'not-allowed' : 'pointer', fontWeight: 500 }}
          >
            {loading ? 'Creating account...' : 'Register'}
          </button>
        </form>

        <p style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.875rem', color: '#6b7280' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: '#60a5fa', textDecoration: 'none' }}>
            Login here
          </Link>
        </p>
      </div>
    </div>
  )
}
