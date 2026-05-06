import axios from 'axios'

/**
 * Servicio para interactuar con el API Server Backend
 * 
 * ARQUITECTURA EMPRESARIAL:
 * Frontend (React) → API Server (FastAPI) → MCP Servers (Local stdio + Remoto HTTP)
 * 
 * ⚠️ IMPORTANTE: El frontend NUNCA consume MCP directamente
 * Todo el consumo de IA y MCP se realiza desde el backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

class APIService {
  constructor() {
    this.token = localStorage.getItem('auth_token')
    
    // Configurar axios con interceptores
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // Interceptor para agregar token a todas las peticiones
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Interceptor para manejar errores de autenticación
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout()
          window.location.href = '/'
        }
        return Promise.reject(error)
      }
    )
  }

  // ============================================================================
  // AUTENTICACIÓN
  // ============================================================================

  async login(username, password) {
    try {
      const response = await this.client.post('/auth/login', {
        username,
        password
      })
      
      this.token = response.data.token
      localStorage.setItem('auth_token', this.token)
      localStorage.setItem('user_id', response.data.user_id)
      
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Error al iniciar sesión')
    }
  }

  logout() {
    this.token = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_id')
  }

  isAuthenticated() {
    return !!this.token
  }

  getUserId() {
    return localStorage.getItem('user_id')
  }

  // ============================================================================
  // TAREAS (MCP Local - stdio)
  // Backend consume MCP Server local via stdio
  // ============================================================================

  async listTasks() {
    try {
      const response = await this.client.get('/tasks')
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Error al listar tareas')
    }
  }

  async createTask(title, description) {
    try {
      const response = await this.client.post('/tasks', {
        title,
        description
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Error al crear tarea')
    }
  }

  async updateTask(taskId, completed) {
    try {
      const response = await this.client.patch(`/tasks/${taskId}`, {
        completed
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Error al actualizar tarea')
    }
  }

  async deleteTask(taskId) {
    try {
      const response = await this.client.delete(`/tasks/${taskId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Error al eliminar tarea')
    }
  }

  // ============================================================================
  // CHATBOT CON IA
  // Backend usa OpenAI para interpretar comandos y ejecutar herramientas MCP
  // ============================================================================

  async aiChat(message, conversationHistory = null) {
    try {
      const response = await this.client.post('/ai/chat', {
        message,
        conversation_history: conversationHistory
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Error al procesar mensaje')
    }
  }

  // ============================================================================
  // CLIMA (MCP Remoto - HTTP/SSE)
  // Backend consume MCP Server remoto via HTTP
  // ============================================================================

  async getWeather(city, units = 'metric') {
    try {
      const response = await this.client.get('/weather', {
        params: { city, units }
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Error al obtener clima')
    }
  }

  // ============================================================================
  // UTILIDADES
  // ============================================================================

  async healthCheck() {
    try {
      const response = await this.client.get('/health')
      return response.data
    } catch (error) {
      throw new Error('Error al verificar estado del servidor')
    }
  }
}

export const apiService = new APIService()
