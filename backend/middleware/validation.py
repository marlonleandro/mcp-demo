"""
Validación de datos con Pydantic para FastAPI
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict


# ============================================================================
# REQUEST MODELS
# ============================================================================

class CreateTaskRequest(BaseModel):
    """Modelo para validar la creación de tareas"""
    title: str = Field(..., min_length=1, max_length=200, description="Título de la tarea")
    description: str = Field(..., min_length=1, max_length=1000, description="Descripción detallada")
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('La descripción no puede estar vacía')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Comprar leche",
                "description": "Ir al supermercado y comprar leche desnatada"
            }
        }


class UpdateTaskRequest(BaseModel):
    """Modelo para validar la actualización de tareas"""
    completed: bool = Field(..., description="Estado de completado de la tarea")
    
    class Config:
        json_schema_extra = {
            "example": {
                "completed": True
            }
        }


class LoginRequest(BaseModel):
    """Modelo para validar el login"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    password: str = Field(..., min_length=6, description="Contraseña")
    
    @validator('username')
    def username_must_be_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('El username solo puede contener letras, números, guiones y guiones bajos')
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "usuario_demo",
                "password": "password123"
            }
        }


class ChatRequest(BaseModel):
    """Modelo para peticiones de chat"""
    message: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Historial de conversación (opcional)"
    )
    
    @validator('message')
    def message_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('El mensaje no puede estar vacío')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Crea una tarea para comprar leche",
                "conversation_history": [
                    {"role": "user", "content": "Hola"},
                    {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte?"}
                ]
            }
        }


class ChatResponse(BaseModel):
    """Modelo de respuesta para chat"""
    response: str = Field(..., description="Respuesta del chatbot")
    tool_used: Optional[str] = Field(None, description="Herramienta MCP usada (si aplica)")
    tool_result: Optional[dict] = Field(None, description="Resultado de la herramienta (si aplica)")
    error: Optional[str] = Field(None, description="Error si ocurrió alguno")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "He creado la tarea 'Comprar leche' exitosamente.",
                "tool_used": "create_task",
                "tool_result": {
                    "success": True,
                    "task": {
                        "id": "uuid",
                        "title": "Comprar leche",
                        "completed": False
                    }
                }
            }
        }


class WeatherRequest(BaseModel):
    """Modelo para validar peticiones de clima"""
    city: str = Field(..., min_length=2, max_length=100, description="Nombre de la ciudad")
    units: Optional[str] = Field(default="metric", pattern="^(metric|imperial)$", description="Sistema de unidades")
    
    @validator('city')
    def city_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('La ciudad no puede estar vacía')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "city": "Madrid",
                "units": "metric"
            }
        }


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class TaskResponse(BaseModel):
    """Modelo de respuesta para tareas"""
    id: str = Field(..., description="ID único de la tarea")
    user_id: str = Field(..., description="ID del usuario propietario")
    title: str = Field(..., description="Título de la tarea")
    description: str = Field(..., description="Descripción de la tarea")
    completed: bool = Field(..., description="Estado de completado")
    created_at: str = Field(..., description="Fecha de creación (ISO 8601)")
    updated_at: Optional[str] = Field(None, description="Fecha de última actualización (ISO 8601)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "usuario_demo",
                "title": "Comprar leche",
                "description": "Ir al supermercado",
                "completed": False,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": None
            }
        }


class LoginResponse(BaseModel):
    """Modelo de respuesta para login"""
    token: str = Field(..., description="JWT token de autenticación")
    user_id: str = Field(..., description="ID del usuario")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user_id": "usuario_demo",
                "expires_in": 86400
            }
        }


class MessageResponse(BaseModel):
    """Modelo de respuesta genérico con mensaje"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operación completada exitosamente"
            }
        }


class HealthResponse(BaseModel):
    """Modelo de respuesta para health check"""
    status: str = Field(..., description="Estado del servidor")
    timestamp: str = Field(..., description="Timestamp actual (ISO 8601)")
    service: str = Field(..., description="Nombre del servicio")
    mcp_local: bool = Field(..., description="Estado del MCP Server local")
    mcp_remote: bool = Field(..., description="Estado del MCP Server remoto")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "timestamp": "2024-01-15T10:30:00",
                "service": "MCP API Server (FastAPI)",
                "mcp_local": True,
                "mcp_remote": False
            }
        }
