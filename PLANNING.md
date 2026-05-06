# 📋 Planning - MCP Server Demo con Chatbot IA

## 🎯 Objetivo del Proyecto

Crear un sistema de gestión de tareas que demuestre:
1. Arquitectura empresarial backend-centric con MCP
2. Chatbot inteligente con OpenAI GPT-4
3. IDs secuenciales para fácil uso
4. Autenticación JWT y seguridad
5. Frontend React + Backend FastAPI

---

## 🚀 Prompts para Recrear el Proyecto con IA

### Prompt 1: Estructura Inicial del Proyecto

```
Crea un proyecto de gestión de tareas con arquitectura empresarial que demuestre el uso de Model Context Protocol (MCP). 

Requisitos:
1. Backend en Python con FastAPI
2. Frontend en React con Vite
3. Arquitectura backend-centric (frontend NO consume MCP directamente)
4. MCP Server local via stdio para gestión de tareas
5. Autenticación JWT
6. Estructura de carpetas profesional

Estructura esperada:
- backend/ (FastAPI + MCP Server)
- frontend/ (React + Vite)
- Documentación (README, ARCHITECTURE)

Implementa:
- Backend: API REST con endpoints de autenticación y tareas
- Frontend: Login + Lista de tareas + Formulario
- MCP Server: Herramientas CRUD para tareas
- Persistencia: JSON file storage
- Seguridad: JWT tokens, rate limiting, validación

NO incluyas OpenAI ni chatbot todavía, solo la estructura base.
```

### Prompt 2: Sistema de IDs Secuenciales

```
Implementar IDs secuenciales como identificador únicos de las tareas.

Requisitos:
1. IDs de 6 dígitos con ceros a la izquierda (000001, 000002, ...)
2. Contador independiente por usuario
3. Normalización automática: "1" → "000001"
4. Mostrar ID en la UI debajo del título de cada tarea
5. Persistencia del contador en JSON

Archivos a modificar:
- backend/services/task_manager.py: Cambiar generación de IDs
- frontend/src/components/TaskList.jsx: Mostrar ID visible
- backend/services/mcp_client_service.py: Normalización de IDs

Estructura de datos en JSON:
{
  "usuario1": {
    "tasks": {
      "000001": {...},
      "000002": {...}
    },
    "next_id": 3
  }
}

Asegúrate de que los IDs sean fáciles de usar y visibles para el usuario.
```

### Prompt 3: Chatbot con OpenAI GPT-4

```
Implementa un chatbot inteligente que use OpenAI GPT-4 para interpretar comandos en lenguaje natural y ejecutar herramientas MCP automáticamente.

Requisitos:
1. Backend: Servicio de chatbot (ai_chatbot_service.py)
2. OpenAI GPT-4 con function calling
3. Herramientas MCP disponibles: list_tasks, create_task, update_task, delete_task
4. Múltiples herramientas en secuencia (loop de hasta 5 iteraciones)
5. Frontend: Componente ChatBot flotante en esquina inferior derecha
6. Conversación contextual con historial
7. Normalización de IDs (acepta "1" o "000001")

Funcionalidades del chatbot:
- Interpretar: "Crea una tarea para comprar leche"
- Interpretar: "Elimina la tarea 1"
- Interpretar: "Completa la tarea de hacer ejercicio"
- Pedir información faltante si es necesario
- Ejecutar múltiples herramientas automáticamente

Archivos a crear/modificar:
- backend/services/ai_chatbot_service.py (NUEVO)
- backend/api_server.py: Agregar endpoint POST /api/ai/chat
- backend/middleware/validation.py: ChatRequest y ChatResponse
- backend/config.py: OPENAI_API_KEY y OPENAI_MODEL
- frontend/src/components/ChatBot.jsx (NUEVO)
- frontend/src/App.jsx: Integrar ChatBot
- frontend/src/services/apiService.js: Método aiChat()

System prompt debe enfatizar:
- Usar IDs de 6 dígitos del campo "id"
- Ejecutar múltiples herramientas en secuencia
- Pedir información faltante
- Ser conversacional y amable
```

### Prompt 4: Seguridad y Validación

```
Mejora la seguridad y validación del proyecto:

1. Rate Limiting:
   - Login: 5 por minuto
   - Tareas: 50 por minuto
   - Chat: 30 por minuto

2. Validación con Pydantic V2:
   - Todos los request/response models
   - Validación de campos
   - Ejemplos en schema

3. Autenticación JWT:
   - Tokens con expiración de 24 horas
   - Dependency injection en FastAPI
   - Verificación en todos los endpoints protegidos

4. CORS:
   - Configurar orígenes permitidos
   - Credentials habilitados

5. Logging:
   - Todas las operaciones importantes
   - Errores con stack trace
   - Auditoría de acciones

6. Variables de Entorno:
   - SECRET_KEY para JWT
   - OPENAI_API_KEY
   - Configuración de rate limits
   - No hardcodear secrets

Asegúrate de que el sistema sea seguro para producción.
```

### Prompt 5: Documentación Completa

```
Crea documentación completa para el proyecto:

1. README.md:
   - Descripción del proyecto
   - Arquitectura
   - Instalación paso a paso
   - Configuración
   - Uso del chatbot
   - Endpoints API
   - Características de seguridad

2. ARCHITECTURE.md:
   - Diagrama de arquitectura empresarial
   - Flujo de datos completo
   - Componentes implementados
   - Tecnologías utilizadas
   - Próximas mejoras

Incluye ejemplos de código, diagramas y comandos útiles.
```

---

## 📐 Diseño Técnico

### Arquitectura General

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐      │
│  │ Login    │  │ TaskList │  │ ChatBot (Float)  │      │
│  └──────────┘  └──────────┘  └──────────────────┘      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS/REST + JWT
                     ↓
┌─────────────────────────────────────────────────────────┐
│              BACKEND (FastAPI)                          │
│  ┌──────────────────────────────────────────────┐      │
│  │ API Server                                    │      │
│  │  - /api/auth/login                           │      │
│  │  - /api/tasks (CRUD)                         │      │
│  │  - /api/ai/chat (Chatbot)                    │      │
│  └──────────────────┬───────────────────────────┘      │
│                     │                                    │
│  ┌──────────────────┴───────────────────────────┐      │
│  │ AI Chatbot Service                           │      │
│  │  - OpenAI GPT-4 Integration                  │      │
│  │  - Function Calling                          │      │
│  │  - Multi-tool Execution                      │      │
│  └──────────────────┬───────────────────────────┘      │
│                     │                                    │
│  ┌──────────────────┴───────────────────────────┐      │
│  │ MCP Client Service                           │      │
│  │  - stdio communication                       │      │
│  │  - Tool execution                            │      │
│  └──────────────────┬───────────────────────────┘      │
└────────────────────┬────────────────────────────────────┘
                     │ stdio
                     ↓
┌─────────────────────────────────────────────────────────┐
│           MCP SERVER LOCAL (stdio)                      │
│  ┌──────────────────────────────────────────────┐      │
│  │ Tools:                                        │      │
│  │  - list_tasks                                 │      │
│  │  - create_task                                │      │
│  │  - update_task                                │      │
│  │  - delete_task                                │      │
│  └──────────────────┬───────────────────────────┘      │
│                     │                                    │
│  ┌──────────────────┴───────────────────────────┐      │
│  │ Task Manager                                  │      │
│  │  - Sequential IDs (000001, 000002, ...)      │      │
│  │  - Multi-user support                        │      │
│  │  - JSON persistence                          │      │
│  └──────────────────┬───────────────────────────┘      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
              tasks_db.json
```

### Flujo de Datos: Chatbot

```
1. Usuario escribe: "Elimina la tarea 1"
   ↓
2. Frontend envía: POST /api/ai/chat
   {
     "message": "Elimina la tarea 1",
     "conversation_history": [...]
   }
   ↓
3. Backend verifica JWT
   ↓
4. AI Chatbot Service procesa:
   - Construye mensajes con system prompt
   - Llama a OpenAI GPT-4
   ↓
5. OpenAI (Iteración 1):
   - Decide usar list_tasks()
   - Retorna tool_call
   ↓
6. Backend ejecuta list_tasks via MCP
   - Obtiene: [{"id": "000001", "title": "Comprar leche"}, ...]
   ↓
7. OpenAI (Iteración 2):
   - Ve la lista de tareas
   - Identifica ID 000001
   - Decide usar delete_task("000001")
   - Retorna tool_call
   ↓
8. Backend ejecuta delete_task("000001") via MCP
   - Resultado: {"success": true, "message": "Tarea eliminada"}
   ↓
9. OpenAI (Iteración 3):
   - Ve el resultado exitoso
   - Genera respuesta natural
   - NO hay más tool_calls
   ↓
10. Backend retorna:
    {
      "response": "He eliminado la tarea 'Comprar leche' exitosamente.",
      "tool_used": "delete_task",
      "tool_result": {...}
    }
    ↓
11. Frontend muestra respuesta y actualiza lista
```

### Estructura de Datos

#### tasks_db.json
```json
{
  "usuario1": {
    "tasks": {
      "000001": {
        "id": "000001",
        "user_id": "usuario1",
        "title": "Comprar leche",
        "description": "Ir al supermercado",
        "completed": false,
        "created_at": "2024-01-15T10:30:00"
      },
      "000002": {
        "id": "000002",
        "user_id": "usuario1",
        "title": "Estudiar MCP",
        "description": "Leer documentación",
        "completed": true,
        "created_at": "2024-01-15T11:00:00",
        "updated_at": "2024-01-15T12:00:00"
      }
    },
    "next_id": 3
  },
  "usuario2": {
    "tasks": {},
    "next_id": 1
  }
}
```

---

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.9+**
- **FastAPI**: Framework web async
- **Uvicorn**: ASGI server
- **OpenAI SDK**: GPT-4 integration
- **MCP SDK**: Model Context Protocol
- **Pydantic V2**: Data validation
- **python-jose**: JWT tokens
- **slowapi**: Rate limiting

### Frontend
- **React 18**
- **Vite**: Build tool
- **Axios**: HTTP client
- **CSS3**: Custom styles

### MCP
- **stdio**: Local communication
- **HTTP/SSE**: Remote communication (preparado)

---

## 📋 Checklist de Implementación

### Fase 1: Estructura Base
- [ ] Crear estructura de carpetas
- [ ] Configurar backend con FastAPI
- [ ] Configurar frontend con React + Vite
- [ ] Implementar autenticación JWT
- [ ] Crear MCP Server local (stdio)
- [ ] Implementar CRUD de tareas
- [ ] Persistencia en JSON

### Fase 2: IDs Secuenciales
- [ ] Formato de 6 dígitos para ID de tarea (000001)
- [ ] Contador por usuario
- [ ] Normalización automática
- [ ] Mostrar ID en UI
- [ ] Vaciar datos existentes

### Fase 3: Chatbot con IA
- [ ] Crear AI Chatbot Service
- [ ] Integrar OpenAI GPT-4
- [ ] Implementar function calling
- [ ] Loop de múltiples herramientas
- [ ] Crear componente ChatBot (frontend)
- [ ] Endpoint /api/ai/chat
- [ ] Conversación contextual

### Fase 4: Seguridad
- [ ] Rate limiting configurado
- [ ] Validación con Pydantic V2
- [ ] JWT en todos los endpoints
- [ ] CORS configurado
- [ ] Logging de auditoría
- [ ] Variables de entorno

### Fase 5: Documentación
- [ ] README.md completo
- [ ] ARCHITECTURE.md
- [ ] PLANNING.md (este archivo)

---

## 🧪 Testing

### Tests Manuales

#### 1. Autenticación
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Guardar token
TOKEN="eyJ..."
```

#### 2. Tareas
```bash
# Crear tarea
curl -X POST http://localhost:5000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","description":"Prueba"}'

# Listar tareas
curl http://localhost:5000/api/tasks \
  -H "Authorization: Bearer $TOKEN"

# Actualizar tarea
curl -X PATCH http://localhost:5000/api/tasks/000001 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# Eliminar tarea
curl -X DELETE http://localhost:5000/api/tasks/000001 \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. Chatbot
```bash
# Chat
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Crea una tarea para comprar leche",
    "conversation_history": []
  }'
```

### Tests en UI

1. **Login**: Iniciar sesión con cualquier usuario/password
2. **Crear Tarea**: Usar formulario, verificar ID 000001
3. **Listar Tareas**: Ver ID visible debajo del título
4. **Chatbot**: 
   - "Crea tarea Test"
   - "Muéstrame mis tareas"
   - "Elimina la tarea 1"
   - "Completa la tarea 2"
5. **Actualización Automática**: Verificar que la lista se actualiza después del chat

---

## 📚 Recursos

### Documentación Oficial
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [OpenAI API](https://platform.openai.com/docs)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

### Tutoriales
- [FastAPI + JWT](https://fastapi.tiangolo.com/tutorial/security/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [React Hooks](https://react.dev/reference/react)

---

## 🎯 Resultado Final

Un sistema completo de gestión de tareas que demuestra:

✅ **Arquitectura Empresarial**: Backend-centric, segura, escalable
✅ **MCP Integration**: Consumo correcto de MCP Servers
✅ **Chatbot Inteligente**: OpenAI GPT-4 con function calling
✅ **IDs Usables**: Secuenciales de 6 dígitos, visibles en UI
✅ **Seguridad**: JWT, rate limiting, validación
✅ **UX Excelente**: Chatbot natural, IDs fáciles de usar
✅ **Documentación Completa**: Guías, ejemplos, troubleshooting

**Tiempo estimado**: 8-12 horas con IA asistente
**Nivel**: Intermedio-Avanzado
**Tecnologías**: Python, FastAPI, React, OpenAI, MCP
