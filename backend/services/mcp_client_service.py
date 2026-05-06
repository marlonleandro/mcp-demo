"""
Servicio cliente MCP unificado
Maneja conexiones a MCP Servers locales (stdio) y remotos (HTTP/SSE)
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
# from mcp.client.sse import sse_client  # Descomentar cuando esté disponible

from config import (
    MCP_LOCAL_TASKS_ENABLED,
    MCP_LOCAL_TASKS_COMMAND,
    MCP_LOCAL_TASKS_SCRIPT,
    MCP_REMOTE_WEATHER_ENABLED,
    MCP_REMOTE_WEATHER_URL
)

logger = logging.getLogger(__name__)


class MCPClientService:
    """
    Cliente unificado para consumir MCP Servers
    Soporta conexiones locales (stdio) y remotas (HTTP/SSE)
    """
    
    def __init__(self):
        self.local_tasks_enabled = MCP_LOCAL_TASKS_ENABLED
        self.remote_weather_enabled = MCP_REMOTE_WEATHER_ENABLED
        
        # Configuración de servidores MCP
        self.local_tasks_params = StdioServerParameters(
            command=MCP_LOCAL_TASKS_COMMAND,
            args=[MCP_LOCAL_TASKS_SCRIPT]
        )
        
        self.remote_weather_url = MCP_REMOTE_WEATHER_URL
    
    async def call_local_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Llama a una herramienta del MCP Server local via stdio
        
        Args:
            tool_name: Nombre de la herramienta MCP
            arguments: Argumentos para la herramienta
            user_id: ID del usuario (para filtrado y auditoría)
        
        Returns:
            Resultado de la herramienta como diccionario
        
        Raises:
            Exception: Si hay error en la comunicación o ejecución
        """
        if not self.local_tasks_enabled:
            raise Exception("MCP Server local no está habilitado")
        
        # Agregar user_id para filtrado por usuario
        arguments['user_id'] = user_id
        
        logger.info(f"Llamando a herramienta local '{tool_name}' para usuario {user_id}")
        
        try:
            async with stdio_client(self.local_tasks_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Ejecutar herramienta
                    result = await session.call_tool(tool_name, arguments)
                    
                    # Extraer contenido
                    if result.content and len(result.content) > 0:
                        data = json.loads(result.content[0].text)
                        logger.debug(f"Resultado de '{tool_name}': {data}")
                        return data
                    
                    raise Exception("No se recibió respuesta del servidor MCP")
        
        except Exception as e:
            logger.error(f"Error al llamar a herramienta local '{tool_name}': {str(e)}")
            raise
    
    async def call_remote_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Llama a una herramienta del MCP Server remoto via HTTP
        
        Args:
            tool_name: Nombre de la herramienta MCP
            arguments: Argumentos para la herramienta
            user_id: ID del usuario (para auditoría)
        
        Returns:
            Resultado de la herramienta como diccionario
        
        Raises:
            Exception: Si hay error en la comunicación o ejecución
        """
        if not self.remote_weather_enabled:
            raise Exception("MCP Server remoto no está habilitado")
        
        logger.info(f"Llamando a herramienta remota '{tool_name}' para usuario {user_id}")
        
        try:
            import httpx
            
            # Mapear herramientas MCP a endpoints HTTP
            endpoint_map = {
                "get_weather": "/weather",
                "get_forecast": "/forecast"
            }
            
            if tool_name not in endpoint_map:
                raise Exception(f"Herramienta remota desconocida: {tool_name}")
            
            endpoint = endpoint_map[tool_name]
            url = f"{self.remote_weather_url}{endpoint}"
            
            # Hacer petición HTTP al servidor remoto
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=arguments)
                response.raise_for_status()
                
                result = response.json()
                logger.debug(f"Resultado de '{tool_name}': {result}")
                return result
        
        except httpx.HTTPError as e:
            logger.error(f"Error HTTP al llamar a herramienta remota '{tool_name}': {str(e)}")
            raise Exception(f"Error de comunicación con servidor remoto: {str(e)}")
        except Exception as e:
            logger.error(f"Error al llamar a herramienta remota '{tool_name}': {str(e)}")
            raise
    
    # Métodos de conveniencia para tareas (MCP local)
    
    async def list_tasks(self, user_id: str) -> list:
        """Lista todas las tareas del usuario"""
        result = await self.call_local_tool("list_tasks", {}, user_id)
        return result if isinstance(result, list) else []
    
    async def create_task(self, user_id: str, title: str, description: str) -> dict:
        """Crea una nueva tarea"""
        return await self.call_local_tool(
            "create_task",
            {"title": title, "description": description},
            user_id
        )
    
    async def update_task(self, user_id: str, task_id: str, completed: bool) -> dict:
        """Actualiza una tarea"""
        return await self.call_local_tool(
            "update_task",
            {"task_id": task_id, "completed": completed},
            user_id
        )
    
    async def delete_task(self, user_id: str, task_id: str) -> dict:
        """Elimina una tarea"""
        return await self.call_local_tool(
            "delete_task",
            {"task_id": task_id},
            user_id
        )
    
    # Métodos de conveniencia para clima (MCP remoto)
    
    async def get_weather(self, user_id: str, city: str, units: str = "metric") -> dict:
        """Obtiene el clima de una ciudad"""
        return await self.call_remote_tool(
            "get_weather",
            {"city": city, "units": units},
            user_id
        )


# Instancia singleton del servicio
mcp_service = MCPClientService()
