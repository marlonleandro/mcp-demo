#!/usr/bin/env python3
"""
API Server - Arquitectura Empresarial con FastAPI
Backend principal que consume MCP Servers locales (stdio) y remotos (HTTP/SSE)
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

# Importar configuración
from config import (
    API_HOST, API_PORT, DEBUG,
    CORS_ORIGINS, RATE_LIMIT_DEFAULT,
    RATE_LIMIT_LOGIN, RATE_LIMIT_CREATE, LOG_LEVEL, LOG_FORMAT
)

# Importar middleware
from middleware.auth import get_current_user, generate_token, User
from middleware.validation import (
    CreateTaskRequest, UpdateTaskRequest,
    LoginRequest, WeatherRequest, TaskResponse,
    LoginResponse, MessageResponse, HealthResponse,
    ChatRequest, ChatResponse
)

# Importar servicios
from services.mcp_client_service import mcp_service
from services.ai_chatbot_service import ai_chatbot

# Configuración de logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    logger.info("=" * 60)
    logger.info("🚀 MCP API Server - Arquitectura Empresarial (FastAPI)")
    logger.info("=" * 60)
    logger.info(f"📡 MCP Local (stdio): {'✅ Habilitado' if mcp_service.local_tasks_enabled else '❌ Deshabilitado'}")
    logger.info(f"🌐 MCP Remoto (HTTP): {'✅ Habilitado' if mcp_service.remote_weather_enabled else '❌ Deshabilitado'}")
    logger.info(f"🔒 Autenticación JWT: ✅ Habilitada")
    logger.info(f"⚡ Rate Limiting: ✅ Habilitado")
    logger.info(f"🌍 CORS Origins: {', '.join(CORS_ORIGINS)}")
    logger.info(f"🎯 Servidor iniciado en http://{API_HOST}:{API_PORT}")
    logger.info("=" * 60)
    yield
    logger.info("🛑 Cerrando servidor...")

# Crear aplicación FastAPI
app = FastAPI(
    title="MCP API Server",
    description="Backend empresarial con integración MCP",
    version="2.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================================================
# ENDPOINTS - AUTENTICACIÓN
# ============================================================================

@app.post("/api/auth/login", response_model=LoginResponse, tags=["Authentication"])
@limiter.limit(RATE_LIMIT_LOGIN)
async def login(request: Request, credentials: LoginRequest):
    """
    Autenticación de usuario
    
    - **username**: Nombre de usuario (mínimo 3 caracteres)
    - **password**: Contraseña (mínimo 6 caracteres)
    
    Retorna un JWT token válido por 24 horas.
    
    ⚠️ DEMO: En producción, verificar contra base de datos con hash
    """
    try:
        # Aquí aceptamos cualquier usuario/password para demostración
        if credentials.username and credentials.password:
            token = generate_token(user_id=credentials.username)
            
            logger.info(f"Login exitoso para usuario: {credentials.username}")
            
            return LoginResponse(
                token=token,
                user_id=credentials.username,
                expires_in=86400
            )
        
        logger.warning(f"Intento de login fallido desde {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


# ============================================================================
# ENDPOINTS - TAREAS (MCP Local via stdio)
# ============================================================================

@app.get("/api/tasks", response_model=List[TaskResponse], tags=["Tasks"])
@limiter.limit("50 per minute")
async def list_tasks(request: Request, current_user: User = Depends(get_current_user)):
    """
    Lista todas las tareas del usuario autenticado
    
    Requiere autenticación JWT en el header Authorization.
    """
    try:
        logger.info(f"Usuario {current_user.user_id} listando tareas")
        
        # Llamar al MCP Server local via stdio
        result = await mcp_service.list_tasks(current_user.user_id)
        
        return result
    
    except Exception as e:
        logger.error(f"Error al listar tareas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener tareas"
        )


@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
@limiter.limit(RATE_LIMIT_CREATE)
async def create_task(
    request: Request,
    task_data: CreateTaskRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva tarea
    
    - **title**: Título de la tarea (1-200 caracteres)
    - **description**: Descripción detallada (1-1000 caracteres)
    
    Requiere autenticación JWT.
    """
    try:
        logger.info(f"Usuario {current_user.user_id} creando tarea: {task_data.title}")
        
        # Llamar al MCP Server local via stdio
        result = await mcp_service.create_task(
            current_user.user_id,
            task_data.title,
            task_data.description
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error al crear tarea: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear tarea"
        )


@app.patch("/api/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
@limiter.limit("20 per minute")
async def update_task(
    request: Request,
    task_id: str,
    task_data: UpdateTaskRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza el estado de una tarea
    
    - **task_id**: ID de la tarea a actualizar
    - **completed**: Nuevo estado de completado (true/false)
    
    Requiere autenticación JWT.
    """
    try:
        logger.info(f"Usuario {current_user.user_id} actualizando tarea {task_id}")
        
        # Llamar al MCP Server local via stdio
        result = await mcp_service.update_task(
            current_user.user_id,
            task_id,
            task_data.completed
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar tarea: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar tarea"
        )


@app.delete("/api/tasks/{task_id}", response_model=MessageResponse, tags=["Tasks"])
@limiter.limit("20 per minute")
async def delete_task(
    request: Request,
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una tarea
    
    - **task_id**: ID de la tarea a eliminar
    
    Requiere autenticación JWT.
    """
    try:
        logger.info(f"Usuario {current_user.user_id} eliminando tarea {task_id}")
        
        # Llamar al MCP Server local via stdio
        result = await mcp_service.delete_task(
            current_user.user_id,
            task_id
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar tarea: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar tarea"
        )


# ============================================================================
# ENDPOINTS - CHATBOT CON IA
# ============================================================================

@app.post("/api/ai/chat", response_model=ChatResponse, tags=["AI Chatbot"])
@limiter.limit("30 per minute")
async def ai_chat(
    request: Request,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Chatbot inteligente con procesamiento de lenguaje natural
    
    Usa OpenAI para interpretar comandos en lenguaje natural y ejecutar
    herramientas MCP automáticamente.
    
    - **message**: Mensaje del usuario en lenguaje natural
    - **conversation_history**: Historial de conversación (opcional)
    
    Ejemplos de comandos:
    - "Crea una tarea para comprar leche"
    - "Muéstrame mis tareas"
    - "Completa la tarea 1"
    - "Elimina la tarea con ID abc123"
    
    Requiere autenticación JWT y OPENAI_API_KEY configurada.
    """
    try:
        logger.info(f"Usuario {current_user.user_id} usando chatbot: {chat_request.message[:50]}...")
        
        # Llamar al servicio de chatbot
        result = await ai_chatbot.chat(
            message=chat_request.message,
            user_id=current_user.user_id,
            conversation_history=chat_request.conversation_history
        )
        
        return ChatResponse(**result)
    
    except Exception as e:
        logger.error(f"Error en chatbot: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar mensaje"
        )


# ============================================================================
# ENDPOINTS - CLIMA (MCP Remoto via HTTP/SSE)
# ============================================================================

@app.get("/api/weather", tags=["Weather"])
@limiter.limit("30 per minute")
async def get_weather(
    request: Request,
    city: str,
    units: str = "metric",
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el clima de una ciudad
    
    - **city**: Nombre de la ciudad (requerido)
    - **units**: Sistema de unidades - metric o imperial (opcional, default: metric)
    
    Requiere autenticación JWT.
    
    Ejemplo: `/api/weather?city=Madrid&units=metric`
    """
    try:
        # Validar entrada
        weather_request = WeatherRequest(city=city, units=units)
        
        logger.info(f"Usuario {current_user.user_id} consultando clima de {weather_request.city}")
        
        # Llamar al MCP Server remoto via HTTP/SSE
        result = await mcp_service.get_weather(
            current_user.user_id,
            weather_request.city,
            weather_request.units
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error al obtener clima: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener clima"
        )


# ============================================================================
# ENDPOINTS - UTILIDADES
# ============================================================================

@app.get("/api/health", response_model=HealthResponse, tags=["Utilities"])
async def health():
    """
    Health check del servidor
    
    Retorna el estado del servidor y los servicios MCP disponibles.
    No requiere autenticación.
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat(),
        service="MCP API Server (FastAPI)",
        mcp_local=mcp_service.local_tasks_enabled,
        mcp_remote=mcp_service.remote_weather_enabled
    )


@app.get("/", tags=["Utilities"])
async def root():
    """Endpoint raíz - Redirige a la documentación"""
    return {
        "message": "MCP API Server - Arquitectura Empresarial",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/health"
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    
    # En producción, usar:
    # uvicorn api_server:app --host 0.0.0.0 --port 5000 --workers 4
    uvicorn.run(
        "api_server:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG,
        log_level=LOG_LEVEL.lower()
    )
