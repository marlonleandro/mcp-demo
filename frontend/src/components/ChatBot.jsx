import { useState, useRef, useEffect } from 'react'
import { apiService } from '../services/apiService'

function ChatBot({ onTasksChanged }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '¡Hola! Soy tu asistente de tareas. Puedo ayudarte a crear, listar, completar o eliminar tareas. ¿En qué puedo ayudarte?'
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    
    // Agregar mensaje del usuario
    const newMessages = [...messages, { role: 'user', content: userMessage }]
    setMessages(newMessages)
    setLoading(true)

    try {
      // Preparar historial (últimos 10 mensajes para no exceder límites)
      const history = newMessages.slice(-10).map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      // Llamar al chatbot
      const response = await apiService.aiChat(userMessage, history.slice(0, -1))
      
      // Agregar respuesta del asistente
      setMessages([...newMessages, {
        role: 'assistant',
        content: response.response,
        tool_used: response.tool_used,
        tool_result: response.tool_result
      }])

      // Si se ejecutó una herramienta que modifica tareas, actualizar la lista
      if (response.tool_used && ['create_task', 'update_task', 'delete_task'].includes(response.tool_used)) {
        onTasksChanged?.()
      }
    } catch (error) {
      setMessages([...newMessages, {
        role: 'assistant',
        content: `Error: ${error.message}`,
        error: true
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <>
      {/* Botón flotante */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          border: 'none',
          color: 'white',
          fontSize: '24px',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          zIndex: 1000,
          transition: 'transform 0.2s'
        }}
        onMouseEnter={(e) => e.target.style.transform = 'scale(1.1)'}
        onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Ventana de chat */}
      {isOpen && (
        <div style={{
          position: 'fixed',
          bottom: '90px',
          right: '20px',
          width: '400px',
          height: '600px',
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 999,
          overflow: 'hidden'
        }}>
          {/* Header */}
          <div style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '15px 20px',
            fontWeight: 'bold',
            fontSize: '16px'
          }}>
            🤖 Asistente de Tareas IA
          </div>

          {/* Mensajes */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '20px',
            background: '#f7fafc'
          }}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  marginBottom: '15px',
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
                }}
              >
                <div style={{
                  maxWidth: '80%',
                  padding: '10px 15px',
                  borderRadius: '12px',
                  background: msg.role === 'user' 
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    : msg.error 
                    ? '#fee' 
                    : 'white',
                  color: msg.role === 'user' ? 'white' : msg.error ? '#c00' : '#333',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                  wordWrap: 'break-word'
                }}>
                  {msg.content}
                  {msg.tool_used && (
                    <div style={{
                      marginTop: '8px',
                      fontSize: '12px',
                      opacity: 0.7,
                      fontStyle: 'italic'
                    }}>
                      🔧 Herramienta: {msg.tool_used}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div style={{
                display: 'flex',
                justifyContent: 'flex-start',
                marginBottom: '15px'
              }}>
                <div style={{
                  padding: '10px 15px',
                  borderRadius: '12px',
                  background: 'white',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                  <span style={{ animation: 'pulse 1.5s ease-in-out infinite' }}>
                    Pensando...
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div style={{
            padding: '15px',
            borderTop: '1px solid #e2e8f0',
            background: 'white'
          }}>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Escribe tu mensaje..."
                disabled={loading}
                style={{
                  flex: 1,
                  padding: '10px 15px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none'
                }}
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                style={{
                  padding: '10px 20px',
                  background: loading || !input.trim() 
                    ? '#cbd5e0' 
                    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold'
                }}
              >
                Enviar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default ChatBot
