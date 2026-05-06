import { useState } from 'react'

function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!username.trim() || !password.trim()) {
      setError('Por favor completa todos los campos')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      await onLogin(username, password)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1>🚀 MCP Server Demo</h1>
        <p>Arquitectura Empresarial</p>
      </header>

      <div style={{ maxWidth: '400px', margin: '0 auto' }}>
        <div className="card">
          <h2>🔐 Iniciar Sesión</h2>
          
          {error && (
            <div className="error" style={{ marginBottom: '20px' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label htmlFor="username">Usuario</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Ingresa tu usuario"
                disabled={loading}
                autoFocus
              />
            </div>

            <div className="input-group">
              <label htmlFor="password">Contraseña</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Ingresa tu contraseña"
                disabled={loading}
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
            </button>
          </form>

          <div style={{ marginTop: '20px', padding: '15px', background: '#f7fafc', borderRadius: '8px', fontSize: '14px', color: '#555' }}>
            <strong>💡 Demo:</strong> Usa cualquier usuario y contraseña para acceder
          </div>
        </div>

        <div className="card" style={{ marginTop: '20px' }}>
          <h2>🏢 Arquitectura Empresarial</h2>
          <p style={{ color: '#555', lineHeight: '1.6' }}>
            Esta aplicación implementa una arquitectura empresarial real:
          </p>
          <ul style={{ color: '#555', lineHeight: '1.8', marginLeft: '20px' }}>
            <li>✅ Autenticación JWT</li>
            <li>✅ Backend consume MCP (no el frontend)</li>
            <li>✅ MCP Local (stdio) + Remoto (HTTP)</li>
            <li>✅ Rate limiting y validación</li>
            <li>✅ Separación de responsabilidades</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Login
