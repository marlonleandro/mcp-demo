# MCP Server Demo - Arquitectura Empresarial

Proyecto educativo que demuestra el uso del **Model Context Protocol (MCP)** con una arquitectura empresarial real, implementando un sistema de gestión de tareas con backend FastAPI, frontend React, **chatbot inteligente con IA**, y **consultas de clima en tiempo real**.

## 🎯 Objetivo

Aprender MCP mediante un caso práctico empresarial que muestra:
- ✅ Backend consume MCP Servers (local stdio + remoto HTTP)
- ✅ Frontend NUNCA consume MCP directamente
- ✅ Autenticación JWT y seguridad empresarial
- ✅ Separación de responsabilidades
- ✅ Rate limiting y validación de datos
- ✅ **Chatbot con IA** que usa OpenAI GPT-4 para ejecutar herramientas MCP
- ✅ **Consultas de clima** integradas en el chatbot
- ✅ **IDs secuenciales** de 6 dígitos para fácil uso
- ✅ **Múltiples herramientas en secuencia** para flujos complejos

**🤖 Chatbot Inteligente**: Interpreta comandos en lenguaje natural ("Elimina la tarea 1", "¿Qué clima hace en Madrid?", "Si hace buen tiempo, crea una tarea para salir") y ejecuta herramientas MCP automáticamente.

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Frontend       │  React + Axios
│  (Puerto 3000)  │  
└────────┬────────┘
         │ HTTPS/REST + JWT Auth
         ↓
┌─────────────────┐
│  API Server     │  FastAPI + CORS + Rate Limiting
│  (Puerto 5000)  │  + AI Chatbot Service
└────────┬────────┘
         │
         ├─→ MCP Local (stdio)
         │   └─→ Gestión de Tareas (IDs secuenciales)
         │
         └─→ MCP Remoto (HTTP :8080)
             └─→ Servicios de Clima (Weather Server)
```

## 📁 Estructura del Proyecto

```
mcp-demo/
├── backend/                      # Backend empresarial con FastAPI
│   ├── api_server.py            # API REST principal (FastAPI)
│   ├── config.py                # Configuración centralizada
│   ├── mcp_servers/
│   │   ├── local_tasks_server.py   # MCP Server local (stdio)
│   │   └── remote_weather_server.py # MCP Server remoto (HTTP)
│   ├── services/
│   │   ├── ai_chatbot_service.py   # Chatbot con OpenAI GPT-4
│   │   ├── mcp_client_service.py   # Cliente MCP unificado
│   │   └── task_manager.py         # Lógica de negocio
│   ├── middleware/
│   │   ├── auth.py                 # Autenticación JWT (FastAPI)
│   │   └── validation.py           # Validación Pydantic
│   ├── requirements.txt
│   └── .env.example
├── frontend/                     # Cliente React
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Login.jsx
│   │   │   ├── TaskForm.jsx
│   │   │   └── TaskList.jsx
│   │   └── services/
│   │       └── apiService.js       # Cliente HTTP (NO MCP directo)
│   ├── package.json
│   └── .env
├── README.md                     # Este archivo
├── ARCHITECTURE.md               # Arquitectura detallada
└── PLANNING.md                   # Diseño y planificación
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.9+
- Node.js 18+
- pip y npm
- OpenAI API Key (para chatbot)

### 1. Backend (API Server)

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
# Editar .env y agregar tu OPENAI_API_KEY

# Iniciar servidor FastAPI
python api_server.py
```

El backend estará en `http://localhost:5000`

**Documentación interactiva**:
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

### 2. Weather Server (Opcional - para clima)

```bash
# En otra terminal
cd backend/mcp_servers
python remote_weather_server.py
```

El Weather Server estará en `http://localhost:8080`

### 3. Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno (ya está configurado)
# El archivo .env ya apunta a http://localhost:5000/api

# Iniciar aplicación
npm run dev
```

El frontend estará en `http://localhost:3000` o `http://localhost:5173`

### 4. Usar la Aplicación

1. Abre el navegador en `http://localhost:3000`
2. Inicia sesión con cualquier usuario/contraseña (es demo)
3. Crea, actualiza y elimina tareas
4. Haz clic en el botón 💬 para usar el chatbot
5. Prueba comandos como:
   - "Crea una tarea para comprar leche"
   - "¿Qué clima hace en Madrid?"
   - "Si hace buen tiempo en Barcelona, crea una tarea para salir"

## 🔐 Características de Seguridad

- ✅ **Autenticación JWT**: Todas las rutas protegidas requieren token
- ✅ **Rate Limiting**: Límites por usuario/IP
- ✅ **Validación de Entrada**: Pydantic schemas
- ✅ **CORS Configurado**: Solo orígenes permitidos
- ✅ **Logging de Auditoría**: Todas las acciones registradas
- ✅ **Separación de Datos**: Cada usuario ve solo sus tareas

## 🔌 MCP Servers Implementados

### MCP Local (stdio)
- **Protocolo**: stdio (proceso local)
- **Herramientas**:
  - `list_tasks`: Lista tareas del usuario
  - `create_task`: Crea nueva tarea con ID secuencial
  - `update_task`: Actualiza tarea por ID
  - `delete_task`: Elimina tarea por ID
- **IDs**: Secuenciales de 6 dígitos (000001, 000002, ...)
- **Ventajas**: Rápido, seguro, sin latencia de red
- **Consumido por**: API Server y Chatbot IA

### MCP Remoto (HTTP)
- **Protocolo**: HTTP REST (servidor independiente)
- **Puerto**: 8080
- **Herramientas**:
  - `get_weather`: Obtiene clima actual de una ciudad
  - `get_forecast`: Pronóstico del tiempo (1-7 días)
- **Ciudades**: Madrid, Barcelona, Valencia, Sevilla, y más
- **Ventajas**: Escalable, microservicios, distribuido
- **Consumido por**: Chatbot IA via MCP Client

## 🤖 Chatbot con IA

El proyecto incluye un **chatbot inteligente** que usa OpenAI GPT-4 para:
- Interpretar comandos en lenguaje natural
- Ejecutar herramientas MCP automáticamente
- Mantener conversaciones contextuales
- Pedir información faltante al usuario
- Usar IDs secuenciales de 6 dígitos
- **Consultar clima de ciudades**
- **Combinar tareas y clima en una conversación**

**Ejemplos de uso**:

**Tareas**:
```
"Crea una tarea para comprar leche"
"Muéstrame mis tareas"
"Completa la tarea 1"
"Elimina la tarea de hacer ejercicio"
```

**Clima**:
```
"¿Qué clima hace en Madrid?"
"Pronóstico de Barcelona para 5 días"
"¿Hace calor en Sevilla?"
"Dime la temperatura de Valencia"
```

**Combinado**:
```
"Si hace buen tiempo en Madrid, crea una tarea para salir"
"Muéstrame mis tareas y el clima de Barcelona"
```

**Características**:
- ✅ IDs visibles en la UI (000001, 000002, ...)
- ✅ Acepta IDs cortos: "1" o completos: "000001"
- ✅ Múltiples herramientas en secuencia
- ✅ Conversación natural y contextual
- ✅ Consultas de clima integradas
- ✅ System prompt optimizado para mejor reconocimiento

**Configuración**:
```bash
# backend/.env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4

# MCP Remoto (Weather)
MCP_REMOTE_WEATHER_ENABLED=true
MCP_REMOTE_WEATHER_URL=http://localhost:8080
```

## 📊 Endpoints API

### Autenticación
```bash
POST /api/auth/login
Body: {"username": "user", "password": "pass"}
Response: {"token": "jwt_token", "user_id": "user"}
```

### Tareas (requiere autenticación)
```bash
GET    /api/tasks              # Listar tareas
POST   /api/tasks              # Crear tarea
PATCH  /api/tasks/{id}         # Actualizar tarea
DELETE /api/tasks/{id}         # Eliminar tarea
```

### Chatbot IA (requiere autenticación)
```bash
POST /api/ai/chat
Body: {
  "message": "Crea una tarea para comprar leche",
  "conversation_history": [...]
}
```

### Clima (requiere autenticación)
```bash
GET /api/weather?city=Madrid&units=metric
```

**Nota**: El clima también está disponible a través del chatbot con comandos naturales como "¿Qué clima hace en Madrid?"

### Utilidades
```bash
GET /api/health                # Health check
```

## 🧪 Testing

```bash
cd backend
python test_mcp.py
```

## 🚀 Deploy en Producción

### Backend con Uvicorn

```bash
cd backend
uvicorn api_server:app --host 0.0.0.0 --port 5000 --workers 4
```

### Frontend Build

```bash
cd frontend
npm run build
# Los archivos estáticos estarán en dist/
```

### Docker

```bash
# Build
docker build -t mcp-backend ./backend
docker build -t mcp-frontend ./frontend

# Run
docker-compose up -d
```

## 📚 Documentación Adicional

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitectura empresarial completa
- [PLANNING.md](./PLANNING.md) - Diseño, planificación y prompts para recrear el proyecto
- [backend/README.md](./backend/README.md) - Documentación del backend
- [frontend/README.md](./frontend/README.md) - Documentación del frontend

## 🎓 Conceptos Clave Aprendidos

1. **MCP NO se consume desde el frontend** en producción
2. **Backend actúa como puente** entre frontend y MCP
3. **stdio vs HTTP**: Cuándo usar cada protocolo
4. **Autenticación y autorización** en arquitecturas MCP
5. **Separación de responsabilidades** en aplicaciones empresariales
6. **IDs secuenciales** vs UUIDs para mejor UX
7. **Chatbot con function calling** para ejecutar herramientas MCP
8. **Múltiples herramientas en secuencia** para flujos complejos
9. **System prompt optimization** para mejor reconocimiento de herramientas
10. **Microservicios independientes** (Weather Server en puerto separado)

## ⚠️ Notas Importantes

- Este es un proyecto **educativo** con fines de aprendizaje
- En producción, usar base de datos real (no memoria)
- Configurar Redis para rate limiting en producción
- Usar HTTPS en todas las comunicaciones
- Implementar refresh tokens para JWT
- Agregar tests unitarios y de integración

## 📝 Última Actualización

**Fecha**: Mayo 6, 2026  
**Versión**: 1.2.0

**Cambios recientes**:
- ✅ Fix: Chatbot ahora reconoce correctamente consultas de clima
- ✅ System prompt optimizado para mejor reconocimiento de herramientas
- ✅ Documentación completa actualizada
- ✅ Guías de uso del clima agregadas

## Créditos

Marlon Leandro (https://mycustomdevs.com)

## 📄 Licencia

MIT - Proyecto educativo libre para aprender MCP
