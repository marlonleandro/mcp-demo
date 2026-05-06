"""
Servicio de Chatbot con IA
Integra OpenAI con MCP Servers para procesamiento de lenguaje natural
"""

import json
import logging
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL
from services.mcp_client_service import mcp_service

logger = logging.getLogger(__name__)


class AIChatbotService:
    """
    Chatbot inteligente que usa OpenAI para interpretar comandos
    y ejecutar herramientas MCP
    """
    
    def __init__(self):
        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY no configurada - Chatbot no disponible")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        self.model = OPENAI_MODEL
        
        # Definir herramientas MCP disponibles para OpenAI
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Lista todas las tareas del usuario. Úsala cuando el usuario quiera ver sus tareas, listar tareas, o preguntar qué tareas tiene.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Crea una nueva tarea. Úsala cuando el usuario quiera crear, agregar o añadir una tarea. Si falta información (título o descripción), pídela al usuario.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Título corto de la tarea (requerido)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Descripción detallada de la tarea (requerido)"
                            }
                        },
                        "required": ["title", "description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Actualiza el estado de una tarea (completar o reabrir). El task_id es un número de 6 dígitos (ejemplo: 000001). Si el usuario menciona el nombre, primero usa list_tasks para obtener el ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "ID de la tarea (6 dígitos con ceros a la izquierda). Ejemplos: '000001', '000002', '1' (se normaliza a 000001)."
                            },
                            "completed": {
                                "type": "boolean",
                                "description": "true para marcar como completada, false para reabrir"
                            }
                        },
                        "required": ["task_id", "completed"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Elimina una tarea permanentemente. El task_id es un número de 6 dígitos (ejemplo: 000001). Si el usuario menciona el nombre, primero usa list_tasks para obtener el ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "ID de la tarea (6 dígitos con ceros a la izquierda). Ejemplos: '000001', '000002', '1' (se normaliza a 000001)."
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Obtiene el clima ACTUAL de una ciudad. USA ESTA HERRAMIENTA cuando el usuario pregunte por: clima, temperatura, tiempo, condiciones meteorológicas, 'qué clima hace', 'cómo está el tiempo', 'hace calor', 'hace frío', etc. SIEMPRE disponible para cualquier ciudad.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "Nombre de la ciudad (requerido). Ejemplos: Madrid, Barcelona, Valencia, Sevilla, o cualquier otra ciudad del mundo."
                            },
                            "units": {
                                "type": "string",
                                "enum": ["metric", "imperial"],
                                "description": "Sistema de unidades: 'metric' para Celsius (default), 'imperial' para Fahrenheit."
                            }
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_forecast",
                    "description": "Obtiene el pronóstico del clima para los próximos días. USA ESTA HERRAMIENTA cuando el usuario pregunte por: pronóstico, 'cómo estará el tiempo', 'va a llover', clima futuro, 'qué tiempo hará', etc. SIEMPRE disponible para cualquier ciudad.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "Nombre de la ciudad (requerido). Ejemplos: Madrid, Barcelona, Valencia, Sevilla, o cualquier otra ciudad."
                            },
                            "days": {
                                "type": "integer",
                                "description": "Número de días del pronóstico (1-7). Default: 3",
                                "minimum": 1,
                                "maximum": 7
                            }
                        },
                        "required": ["city"]
                    }
                }
            }
        ]
        
        # System prompt
        self.system_prompt = """Eres un asistente inteligente para gestión de tareas y consultas de clima. Tienes acceso a herramientas para ayudar al usuario.

HERRAMIENTAS DISPONIBLES:
1. list_tasks - Lista todas las tareas del usuario
2. create_task - Crea una nueva tarea
3. update_task - Actualiza el estado de una tarea
4. delete_task - Elimina una tarea
5. get_weather - Obtiene el clima ACTUAL de una ciudad (ÚSALA SIEMPRE que pregunten por clima, temperatura, tiempo)
6. get_forecast - Obtiene el pronóstico del clima para los próximos días

REGLAS IMPORTANTES:

CLIMA:
- SIEMPRE usa get_weather cuando el usuario pregunte por: clima, temperatura, tiempo, condiciones meteorológicas, "qué clima hace", "cómo está el tiempo", etc.
- SIEMPRE usa get_forecast cuando el usuario pregunte por: pronóstico, "cómo estará el tiempo", "va a llover", clima futuro, etc.
- Ciudades disponibles: Madrid, Barcelona, Valencia, Sevilla, y cualquier otra ciudad.
- NO digas que no tienes acceso a información de clima - TIENES las herramientas get_weather y get_forecast.

TAREAS:
- Si el usuario quiere crear una tarea pero no proporciona título o descripción, pregúntale amablemente.
- Para eliminar/completar/actualizar una tarea, usa el campo "id" que es un número de 6 dígitos (ejemplo: 000001, 000002, 000003).
- Si el usuario menciona el NOMBRE de una tarea, primero usa list_tasks para encontrar el "id" correcto, luego usa ese "id" en delete_task/update_task.

EJEMPLOS DE INTERACCIÓN:

CLIMA (MUY IMPORTANTE):
- Usuario: "¿Qué clima hace en Madrid?"
  Tú: [USA get_weather con city="Madrid"] → "En Madrid hace 22°C, está soleado..."

- Usuario: "¿Cómo está el tiempo en Barcelona?"
  Tú: [USA get_weather con city="Barcelona"] → "En Barcelona hace 24°C..."

- Usuario: "Dime la temperatura de Valencia"
  Tú: [USA get_weather con city="Valencia"] → "En Valencia hace 26°C..."

- Usuario: "¿Cómo estará el tiempo en Barcelona los próximos 5 días?"
  Tú: [USA get_forecast con city="Barcelona" y days=5] → "Pronóstico para Barcelona..."

- Usuario: "¿Va a llover en Sevilla?"
  Tú: [USA get_forecast con city="Sevilla"] → "Según el pronóstico..."

TAREAS:
- Usuario: "Crea una tarea"
  Tú: "¡Claro! ¿Qué título y descripción quieres para la tarea?"

- Usuario: "Elimina la tarea de comprar leche"
  Tú: [1. Usa list_tasks, 2. Encuentra la tarea, 3. Usa delete_task con el id]

- Usuario: "Muéstrame mis tareas"
  Tú: [Usa list_tasks y presenta los resultados]

IMPORTANTE: 
- NUNCA digas "no tengo acceso a información de clima" - TIENES las herramientas get_weather y get_forecast.
- SIEMPRE usa las herramientas cuando el usuario pregunte por clima o tareas.
- El campo "id" de tareas es un número de 6 dígitos con ceros a la izquierda (000001, 000002, etc.)."""
    
    async def chat(
        self,
        message: str,
        user_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Procesa un mensaje del usuario y ejecuta acciones si es necesario
        
        Args:
            message: Mensaje del usuario
            user_id: ID del usuario autenticado
            conversation_history: Historial de conversación (opcional)
        
        Returns:
            {
                "response": "Respuesta del chatbot",
                "tool_used": "Nombre de la herramienta usada (si aplica)",
                "tool_result": "Resultado de la herramienta (si aplica)"
            }
        """
        if not self.client:
            return {
                "response": "Lo siento, el chatbot no está disponible. Por favor configura OPENAI_API_KEY.",
                "error": "OPENAI_API_KEY no configurada"
            }
        
        try:
            # Construir mensajes
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Agregar historial si existe
            if conversation_history:
                messages.extend(conversation_history)
            
            # Agregar mensaje actual
            messages.append({"role": "user", "content": message})
            
            logger.info(f"Usuario {user_id}: {message}")
            
            # Variables para rastrear herramientas usadas
            tools_used = []
            tools_results = []
            
            # Loop para permitir múltiples llamadas de herramientas
            max_iterations = 5  # Prevenir loops infinitos
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                # Llamada a OpenAI
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto"
                )
                
                response_message = response.choices[0].message
                
                # Si OpenAI quiere usar una herramienta
                if response_message.tool_calls:
                    # Convertir response_message a dict para agregarlo a messages
                    assistant_message = {
                        "role": "assistant",
                        "content": response_message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in response_message.tool_calls
                        ]
                    }
                    messages.append(assistant_message)
                    
                    # Ejecutar todas las herramientas solicitadas
                    for tool_call in response_message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        logger.info(f"Ejecutando herramienta: {function_name} con args: {function_args}")
                        
                        # Ejecutar la herramienta MCP correspondiente
                        tool_result = await self._execute_mcp_tool(
                            function_name,
                            function_args,
                            user_id
                        )
                        
                        # Guardar para el resultado final
                        tools_used.append(function_name)
                        tools_results.append(tool_result)
                        
                        # Agregar resultado de la herramienta a los mensajes
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": json.dumps(tool_result, ensure_ascii=False)
                        })
                    
                    # Continuar el loop para que OpenAI pueda usar más herramientas o responder
                    continue
                
                else:
                    # No hay más herramientas que ejecutar, retornar respuesta final
                    return {
                        "response": response_message.content,
                        "tool_used": tools_used[-1] if tools_used else None,
                        "tool_result": tools_results[-1] if tools_results else None,
                        "all_tools_used": tools_used if len(tools_used) > 1 else None
                    }
            
            # Si llegamos aquí, excedimos el límite de iteraciones
            logger.warning(f"Excedido límite de iteraciones para usuario {user_id}")
            return {
                "response": "He procesado tu solicitud pero necesité demasiados pasos. Por favor, intenta ser más específico.",
                "tool_used": tools_used[-1] if tools_used else None,
                "tool_result": tools_results[-1] if tools_results else None
            }
        
        except Exception as e:
            logger.error(f"Error en chatbot: {str(e)}")
            return {
                "response": f"Lo siento, ocurrió un error: {str(e)}",
                "error": str(e)
            }
    
    async def _execute_mcp_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Ejecuta una herramienta MCP
        
        Args:
            tool_name: Nombre de la herramienta
            arguments: Argumentos de la herramienta
            user_id: ID del usuario
        
        Returns:
            Resultado de la herramienta
        """
        try:
            if tool_name == "list_tasks":
                tasks = await mcp_service.list_tasks(user_id)
                # Formatear tareas para que OpenAI pueda encontrar IDs fácilmente
                formatted_tasks = []
                for idx, task in enumerate(tasks, 1):
                    formatted_tasks.append({
                        "index": idx,
                        "id": task["id"],  # ID de 6 dígitos (000001, 000002, etc.)
                        "title": task["title"],
                        "description": task["description"],
                        "completed": task["completed"]
                    })
                return {
                    "success": True,
                    "tasks": formatted_tasks,
                    "count": len(tasks),
                    "message": f"Se encontraron {len(tasks)} tareas. Usa el campo 'id' (6 dígitos) para eliminar/actualizar."
                }
            
            elif tool_name == "create_task":
                task = await mcp_service.create_task(
                    user_id,
                    arguments["title"],
                    arguments["description"]
                )
                return {
                    "success": True,
                    "task": task,
                    "message": "Tarea creada exitosamente"
                }
            
            elif tool_name == "update_task":
                task = await mcp_service.update_task(
                    user_id,
                    arguments["task_id"],
                    arguments["completed"]
                )
                if "error" in task:
                    return {
                        "success": False,
                        "error": task["error"]
                    }
                return {
                    "success": True,
                    "task": task,
                    "message": "Tarea actualizada exitosamente"
                }
            
            elif tool_name == "delete_task":
                task_id = arguments["task_id"]
                logger.info(f"Intentando eliminar tarea con ID: '{task_id}' (tipo: {type(task_id).__name__}, longitud: {len(task_id)})")
                
                result = await mcp_service.delete_task(
                    user_id,
                    task_id
                )
                
                logger.info(f"Resultado de delete_task: {result}")
                return result
            
            elif tool_name == "get_weather":
                city = arguments["city"]
                units = arguments.get("units", "metric")
                logger.info(f"Consultando clima de {city} en unidades {units}")
                
                result = await mcp_service.get_weather(
                    user_id,
                    city,
                    units
                )
                
                return {
                    "success": True,
                    "weather": result,
                    "message": f"Clima obtenido para {city}"
                }
            
            elif tool_name == "get_forecast":
                city = arguments["city"]
                days = arguments.get("days", 3)
                logger.info(f"Consultando pronóstico de {city} para {days} días")
                
                # Llamar al servidor remoto
                import httpx
                url = f"http://localhost:8080/forecast"
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(url, json={"city": city, "days": days})
                    response.raise_for_status()
                    result = response.json()
                
                return {
                    "success": True,
                    "forecast": result,
                    "message": f"Pronóstico obtenido para {city}"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Herramienta desconocida: {tool_name}"
                }
        
        except Exception as e:
            logger.error(f"Error ejecutando herramienta {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Instancia singleton
ai_chatbot = AIChatbotService()
