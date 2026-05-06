import { useState, useEffect } from 'react'
import TaskForm from './components/TaskForm'
import TaskList from './components/TaskList'
import Login from './components/Login'
import ChatBot from './components/ChatBot'
import { apiService } from './services/apiService'

function App() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // Verificar autenticación al iniciar
  useEffect(() => {
    setIsAuthenticated(apiService.isAuthenticated())
    if (apiService.isAuthenticated()) {
      loadTasks()
    }
  }, [])

  const handleLogin = async (username, password) => {
    try {
      await apiService.login(username, password)
      setIsAuthenticated(true)
      await loadTasks()
    } catch (err) {
      throw err
    }
  }

  const handleLogout = () => {
    apiService.logout()
    setIsAuthenticated(false)
    setTasks([])
  }

  const loadTasks = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiService.listTasks()
      setTasks(result)
    } catch (err) {
      setError('Error al cargar las tareas: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTask = async (title, description) => {
    setError(null)
    try {
      await apiService.createTask(title, description)
      await loadTasks()
    } catch (err) {
      setError('Error al crear la tarea: ' + err.message)
    }
  }

  const handleToggleTask = async (taskId, completed) => {
    setError(null)
    try {
      await apiService.updateTask(taskId, !completed)
      await loadTasks()
    } catch (err) {
      setError('Error al actualizar la tarea: ' + err.message)
    }
  }

  const handleDeleteTask = async (taskId) => {
    setError(null)
    try {
      await apiService.deleteTask(taskId)
      await loadTasks()
    } catch (err) {
      setError('Error al eliminar la tarea: ' + err.message)
    }
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <div className="container">
      <header className="header">
        <div>
          <h1>🚀 MCP Server Demo - Arquitectura Empresarial</h1>
          <p>Gestión de Tareas con Model Context Protocol</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <span style={{ color: 'white', opacity: 0.9 }}>
            👤 {apiService.getUserId()}
          </span>
          <button 
            onClick={handleLogout}
            className="btn btn-small"
            style={{ background: 'rgba(255,255,255,0.2)', color: 'white' }}
          >
            Cerrar Sesión
          </button>
        </div>
      </header>

      {error && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <div className="error">{error}</div>
        </div>
      )}

      <div className="main-content">
        <TaskForm onCreateTask={handleCreateTask} />
        <TaskList
          tasks={tasks}
          loading={loading}
          onToggleTask={handleToggleTask}
          onDeleteTask={handleDeleteTask}
          onRefresh={loadTasks}
        />
      </div>

      <div className="card">
        <h2>📚 Arquitectura Empresarial</h2>
        <p style={{ color: '#555', lineHeight: '1.6', marginBottom: '15px' }}>
          Esta aplicación demuestra una <strong>arquitectura empresarial real</strong> con MCP:
        </p>
        <div style={{ background: '#f7fafc', padding: '15px', borderRadius: '8px', fontFamily: 'monospace', fontSize: '14px' }}>
          Frontend (React) → API Server (FastAPI) → MCP Servers<br/>
          &nbsp;&nbsp;↓ HTTPS/REST + JWT<br/>
          &nbsp;&nbsp;├─→ MCP Local (stdio) - Tareas<br/>
          &nbsp;&nbsp;└─→ MCP Remoto (HTTP) - Servicios Externos
        </div>
        <p style={{ color: '#555', lineHeight: '1.6', marginTop: '15px' }}>
          ✅ El frontend <strong>NUNCA</strong> consume MCP directamente<br/>
          ✅ Backend consume MCP via stdio (local) y HTTP (remoto)<br/>
          ✅ Autenticación JWT en todas las peticiones<br/>
          ✅ Rate limiting y validación de datos<br/>
          ✅ Separación de responsabilidades
        </p>
      </div>

      {/* Chatbot flotante con IA */}
      <ChatBot onTasksChanged={loadTasks} />
    </div>
  )
}

export default App
