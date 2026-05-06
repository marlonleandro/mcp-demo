# Backend - Arquitectura Empresarial MCP con FastAPI

Backend empresarial que implementa el Model Context Protocol con múltiples servidores MCP (local via stdio y remoto via HTTP/SSE).

## 🏗️ Arquitectura

```
Frontend (React)
    ↓ HTTPS/REST + JWT Auth
API Server (FastAPI) :5000
    ├─→ MCP Server Local (stdio) - Gestión de Tareas
    └─→ MCP Server Remoto (HTTP) - Servicios Externos
```

## 📁 Estructura del Proyecto

```
backend/
├── api_server.py              # API REST principal con FastAPI
├── mcp_servers/
│   ├── local_tasks_server.py  # MCP Server local (stdio) - Tareas
│   └── remote_weather_server.py # MCP Server remoto (HTTP/SSE) - Clima
├── services/
│   ├── mcp_client_service.py  # Cliente MCP unificado
│   └── task_manager.py        # Lógica de negocio de tareas
├── middleware/
│   ├── auth.py                # Autenticación JWT (FastAPI)
│   └── validation.py          # Validación de datos (Pydantic)
├── config.py                  # Configuración centralizada
├── requirements.txt           # Dependencias
└── test_mcp.py               # Tests de integración
```

## 🚀 Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## ⚙️ Configuración

Crea un archivo `.env` en el directorio `backend`:

```env
# API Server
API_HOST=0.0.0.0
API_PORT=5000
SECRET_KEY=your-secret-key-change-in-production

# OpenAI (para chatbot)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4

# Database
DATABASE_URL=sqlite:///tasks.db

# MCP Servers
MCP_LOCAL_TASKS_ENABLED=true
MCP_REMOTE_WEATHER_ENABLED=true
MCP_REMOTE_WEATHER_URL=http://localhost:8080

# Logging
LOG_LEVEL=INFO
```

## ▶️ Ejecución

### Modo Desarrollo

```bash
# Iniciar API Server con auto-reload
python api_server.py
```

El servidor estará disponible en `http://localhost:5000`

### Modo Producción

```bash
# Usar Uvicorn directamente
uvicorn api_server:app --host 0.0.0.0 --port 5000 --workers 4

# O con configuración avanzada
uvicorn api_server:app \
  --host 0.0.0.0 \
  --port 5000 \
  --workers 4 \
  --log-level info \
  --access-log
```

### Iniciar MCP Server Remoto (opcional)

Si quieres probar el MCP Server remoto:

```bash
# En otra terminal
cd mcp_servers
python remote_weather_server.py
```

## 📚 Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc
- **OpenAPI JSON**: http://localhost:5000/openapi.json

## 🔧 Endpoints API

### Autenticación

```bash
# Login
POST /api/auth/login
Content-Type: application/json

{
  "username": "usuario",
  "password": "password"
}

# Respuesta
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": "usuario",
  "expires_in": 86400
}
```

### Tareas (MCP Local - stdio)

```bash
# Listar tareas
GET /api/tasks
Authorization: Bearer <token>

# Crear tarea
POST /api/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Mi tarea",
  "description": "Descripción detallada"
}

# Actualizar tarea
PATCH /api/tasks/{task_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "completed": true
}

# Eliminar tarea
DELETE /api/tasks/{task_id}
Authorization: Bearer <token>
```

### Chatbot IA (OpenAI + MCP)

```bash
# Chat con IA
POST /api/ai/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Crea una tarea para comprar leche",
  "conversation_history": [
    {"role": "user", "content": "Hola"},
    {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte?"}
  ]
}

# Respuesta
{
  "response": "He creado la tarea 'Comprar leche' exitosamente.",
  "tool_used": "create_task",
  "tool_result": {
    "success": true,
    "task": {...}
  }
}
```

### Clima (MCP Remoto - HTTP/SSE)

```bash
# Obtener clima
GET /api/weather?city=Madrid&units=metric
Authorization: Bearer <token>
```

### Utilidades

```bash
# Health check
GET /api/health

# Root (información del servidor)
GET /
```

## 🧪 Testing

```bash
# Ejecutar tests de integración
python test_mcp.py

# Tests con pytest (opcional)
pytest tests/ -v
```

## 🔐 Seguridad Implementada

- ✅ Autenticación JWT en todos los endpoints protegidos
- ✅ Rate limiting por IP (slowapi)
- ✅ Validación de entrada con Pydantic
- ✅ CORS configurado
- ✅ Logging de auditoría
- ✅ Secrets en variables de entorno
- ✅ Dependency injection para autenticación
- ✅ Manejo de errores HTTP estándar

## 🔌 Consumo de MCP Servers

### MCP Local (stdio)

El API Server consume el MCP Server local directamente via stdio:

```python
# Comunicación interna - NO expuesta al frontend
from mcp.client.stdio import stdio_client

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        result = await session.call_tool("create_task", {...})
```

**Ventajas**:
- Más rápido (sin latencia de red)
- Más seguro (no expone puertos)
- Ideal para lógica de negocio crítica
- Async/await nativo con FastAPI

### MCP Remoto (HTTP/SSE)

El API Server consume MCP Servers remotos via HTTP:

```python
# Comunicación con servicios externos
from mcp.client.sse import sse_client

async with sse_client("http://mcp-service:8080") as (read, write):
    async with ClientSession(read, write) as session:
        result = await session.call_tool("get_weather", {...})
```

**Ventajas**:
- Escalable horizontalmente
- Permite microservicios
- Ideal para servicios externos
- Async/await nativo

## 🚀 Ventajas de FastAPI

### Performance
- **Más rápido que Flask**: Basado en Starlette y Pydantic
- **Async/await nativo**: Mejor manejo de I/O concurrente
- **Menor latencia**: Ideal para llamadas a MCP Servers

### Developer Experience
- **Documentación automática**: Swagger UI y ReDoc
- **Type hints**: Validación automática con Pydantic
- **Dependency injection**: Código más limpio y testeable
- **Editor support**: Autocompletado y type checking

### Producción
- **Standards-based**: OpenAPI, JSON Schema
- **Security**: OAuth2, JWT, API Keys out-of-the-box
- **Testing**: TestClient integrado
- **Deployment**: Compatible con ASGI servers (Uvicorn, Hypercorn)

## 📊 Monitoreo

```bash
# Health check
GET /api/health

# Métricas (si Prometheus está habilitado)
# Agregar prometheus-fastapi-instrumentator
pip install prometheus-fastapi-instrumentator
```

## 🚀 Deploy

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "5000"]
```

```bash
# Build
docker build -t mcp-backend .

# Run
docker run -p 5000:5000 --env-file .env mcp-backend
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=5000
    env_file:
      - .env
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-backend
  template:
    metadata:
      labels:
        app: mcp-backend
    spec:
      containers:
      - name: api
        image: mcp-backend:latest
        ports:
        - containerPort: 5000
        env:
        - name: API_HOST
          value: "0.0.0.0"
        - name: API_PORT
          value: "5000"
```

## 📚 Documentación Adicional

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Arquitectura completa
- [PLANNING.md](../PLANNING.md) - Diseño y planificación
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Documentación oficial de FastAPI
- [MCP Specification](https://spec.modelcontextprotocol.io/) - Especificación MCP
