import { useState } from 'react'

function TaskForm({ onCreateTask }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!title.trim() || !description.trim()) {
      alert('Por favor completa todos los campos')
      return
    }

    setSubmitting(true)
    try {
      await onCreateTask(title, description)
      setTitle('')
      setDescription('')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="card">
      <h2>➕ Nueva Tarea</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label htmlFor="title">Título</label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Ej: Comprar leche"
            disabled={submitting}
          />
        </div>

        <div className="input-group">
          <label htmlFor="description">Descripción</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe la tarea en detalle..."
            disabled={submitting}
          />
        </div>

        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={submitting}
        >
          {submitting ? 'Creando...' : 'Crear Tarea'}
        </button>
      </form>
    </div>
  )
}

export default TaskForm
