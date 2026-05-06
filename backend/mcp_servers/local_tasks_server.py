#!/usr/bin/env python3
"""
Servidor MCP para gestión de tareas
Implementa el Model Context Protocol con herramientas CRUD
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

from services.task_manager import TaskManager

# Inicializar servidor MCP y gestor de tareas
app = Server("task-manager")
task_manager = TaskManager()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Define las herramientas disponibles en el servidor MCP"""
    return [
        Tool(
            name="list_tasks",
            description="Lista todas las tareas existentes",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="create_task",
            description="Crea una nueva tarea",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Título de la tarea"
                    },
                    "description": {
                        "type": "string",
                        "description": "Descripción detallada de la tarea"
                    }
                },
                "required": ["title", "description"]
            }
        ),
        Tool(
            name="update_task",
            description="Actualiza el estado de una tarea",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID de la tarea a actualizar"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "Estado de completado"
                    }
                },
                "required": ["task_id", "completed"]
            }
        ),
        Tool(
            name="delete_task",
            description="Elimina una tarea por su ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID de la tarea a eliminar"
                    }
                },
                "required": ["task_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Ejecuta la herramienta solicitada con los argumentos proporcionados
    Todas las operaciones están filtradas por user_id para seguridad multi-usuario
    """
    
    # Extraer user_id de los argumentos (agregado por el API Server)
    user_id = arguments.get("user_id", "anonymous")
    
    if name == "list_tasks":
        tasks = task_manager.list_tasks(user_id)
        return [TextContent(
            type="text",
            text=json.dumps(tasks, indent=2)
        )]
    
    elif name == "create_task":
        task = task_manager.create_task(
            user_id=user_id,
            title=arguments["title"],
            description=arguments["description"]
        )
        return [TextContent(
            type="text",
            text=json.dumps(task, indent=2)
        )]
    
    elif name == "update_task":
        task = task_manager.update_task(
            user_id=user_id,
            task_id=arguments["task_id"],
            completed=arguments["completed"]
        )
        if task:
            return [TextContent(
                type="text",
                text=json.dumps(task, indent=2)
            )]
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Tarea no encontrada"})
        )]
    
    elif name == "delete_task":
        success = task_manager.delete_task(
            user_id=user_id,
            task_id=arguments["task_id"]
        )
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": success,
                "message": "Tarea eliminada" if success else "Tarea no encontrada"
            })
        )]
    
    return [TextContent(
        type="text",
        text=json.dumps({"error": f"Herramienta desconocida: {name}"})
    )]


async def main():
    """Inicia el servidor MCP"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
