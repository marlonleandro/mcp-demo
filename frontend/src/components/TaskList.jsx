function TaskList({ tasks, loading, onToggleTask, onDeleteTask, onRefresh }) {
  if (loading) {
    return (
      <div className="card">
        <h2>📋 Mis Tareas</h2>
        <div className="loading">Cargando tareas...</div>
      </div>
    )
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>📋 Mis Tareas</h2>
        <button 
          onClick={onRefresh}
          className="btn btn-small btn-primary"
          style={{ width: 'auto' }}
        >
          🔄 Actualizar
        </button>
      </div>

      {tasks.length === 0 ? (
        <div className="empty-state">
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📝</div>
          <p>No hay tareas aún. ¡Crea tu primera tarea!</p>
        </div>
      ) : (
        <div className="task-list">
          {tasks.map((task) => (
            <div 
              key={task.id} 
              className={`task-item ${task.completed ? 'completed' : ''}`}
            >
              <div className="task-header">
                <div>
                  <div className="task-title">{task.title}</div>
                  <div style={{ 
                    fontSize: '12px', 
                    color: '#666', 
                    marginTop: '4px',
                    fontFamily: 'monospace',
                    fontWeight: 'bold'
                  }}>
                    ID: {task.id}
                  </div>
                </div>
                <span className={`badge ${task.completed ? 'badge-success' : 'badge-pending'}`}>
                  {task.completed ? '✓ Completada' : '⏳ Pendiente'}
                </span>
              </div>
              
              <div className="task-description">{task.description}</div>
              
              <div className="task-actions">
                <button
                  onClick={() => onToggleTask(task.id, task.completed)}
                  className={`btn btn-small ${task.completed ? 'btn-primary' : 'btn-success'}`}
                >
                  {task.completed ? '↩️ Reabrir' : '✓ Completar'}
                </button>
                <button
                  onClick={() => onDeleteTask(task.id)}
                  className="btn btn-small btn-danger"
                >
                  🗑️ Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default TaskList
