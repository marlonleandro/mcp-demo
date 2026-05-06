#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión con el servidor MCP
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Prueba todas las herramientas del servidor MCP"""
    
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    print("🔌 Conectando al servidor MCP...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Conexión establecida\n")
            
            # Listar herramientas disponibles
            print("📋 Herramientas disponibles:")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()
            
            # Crear una tarea
            print("➕ Creando tarea...")
            result = await session.call_tool("create_task", {
                "title": "Tarea de prueba",
                "description": "Esta es una tarea creada desde el script de prueba"
            })
            task_data = json.loads(result.content[0].text)
            task_id = task_data["id"]
            print(f"✅ Tarea creada: {task_data['title']} (ID: {task_id})\n")
            
            # Listar tareas
            print("📋 Listando tareas...")
            result = await session.call_tool("list_tasks", {})
            tasks = json.loads(result.content[0].text)
            print(f"✅ Total de tareas: {len(tasks)}")
            for task in tasks:
                status = "✓" if task["completed"] else "○"
                print(f"  {status} {task['title']}")
            print()
            
            # Actualizar tarea
            print("✏️ Actualizando tarea...")
            result = await session.call_tool("update_task", {
                "task_id": task_id,
                "completed": True
            })
            updated_task = json.loads(result.content[0].text)
            print(f"✅ Tarea actualizada: {updated_task['title']} - Completada: {updated_task['completed']}\n")
            
            # Eliminar tarea
            print("🗑️ Eliminando tarea...")
            result = await session.call_tool("delete_task", {
                "task_id": task_id
            })
            delete_result = json.loads(result.content[0].text)
            print(f"✅ {delete_result['message']}\n")
            
            print("🎉 Todas las pruebas completadas exitosamente!")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
