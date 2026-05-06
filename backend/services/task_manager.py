"""
Gestor de tareas para el servidor MCP
Implementa la lógica de negocio para CRUD de tareas con soporte multi-usuario
Usa persistencia en archivo JSON para mantener el estado entre reinicios
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import os
from pathlib import Path


class TaskManager:
    """
    Gestor de tareas con persistencia en archivo JSON
    Soporta multi-usuario y mantiene el estado entre reinicios del servidor MCP
    Usa IDs correlativos numéricos con formato de 6 dígitos (000001, 000002, etc.)
    """
    
    def __init__(self, storage_file: str = "tasks_db.json"):
        """
        Inicializa el gestor de tareas
        
        Args:
            storage_file: Ruta al archivo JSON para persistencia
        """
        # Estructura: {user_id: {"tasks": {task_id: task_data}, "next_id": int}}
        self.data_by_user: Dict[str, dict] = {}
        
        # Configurar archivo de almacenamiento
        self.storage_file = Path(__file__).parent.parent / storage_file
        
        # Cargar tareas existentes
        self._load_tasks()
    
    def _load_tasks(self):
        """Carga las tareas desde el archivo JSON"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.data_by_user = json.load(f)
            except Exception as e:
                print(f"Error al cargar tareas: {e}")
                self.data_by_user = {}
        else:
            self.data_by_user = {}
    
    def _save_tasks(self):
        """Guarda las tareas en el archivo JSON"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.data_by_user, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar tareas: {e}")
    
    def _get_user_data(self, user_id: str) -> dict:
        """Obtiene los datos de un usuario (tareas y contador)"""
        if user_id not in self.data_by_user:
            self.data_by_user[user_id] = {
                "tasks": {},
                "next_id": 1
            }
        return self.data_by_user[user_id]
    
    def _format_task_id(self, numeric_id: int) -> str:
        """Formatea un ID numérico a 6 dígitos con ceros a la izquierda"""
        return f"{numeric_id:06d}"
    
    def _get_next_id(self, user_id: str) -> str:
        """Obtiene el siguiente ID disponible para un usuario"""
        user_data = self._get_user_data(user_id)
        numeric_id = user_data["next_id"]
        user_data["next_id"] = numeric_id + 1
        return self._format_task_id(numeric_id)
    
    def list_tasks(self, user_id: str) -> List[dict]:
        """Retorna todas las tareas de un usuario"""
        user_data = self._get_user_data(user_id)
        return list(user_data["tasks"].values())
    
    def create_task(self, user_id: str, title: str, description: str) -> dict:
        """Crea una nueva tarea para un usuario"""
        user_data = self._get_user_data(user_id)
        
        task_id = self._get_next_id(user_id)
        task = {
            "id": task_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        user_data["tasks"][task_id] = task
        
        # Guardar cambios
        self._save_tasks()
        
        return task
    
    def update_task(self, user_id: str, task_id: str, completed: bool) -> Optional[dict]:
        """Actualiza el estado de una tarea de un usuario"""
        user_data = self._get_user_data(user_id)
        
        # Normalizar task_id a formato de 6 dígitos si es necesario
        if task_id.isdigit():
            task_id = self._format_task_id(int(task_id))
        
        if task_id in user_data["tasks"]:
            user_data["tasks"][task_id]["completed"] = completed
            user_data["tasks"][task_id]["updated_at"] = datetime.now().isoformat()
            
            # Guardar cambios
            self._save_tasks()
            
            return user_data["tasks"][task_id]
        return None
    
    def delete_task(self, user_id: str, task_id: str) -> bool:
        """Elimina una tarea de un usuario"""
        user_data = self._get_user_data(user_id)
        
        # Normalizar task_id a formato de 6 dígitos si es necesario
        if task_id.isdigit():
            task_id = self._format_task_id(int(task_id))
        
        if task_id in user_data["tasks"]:
            del user_data["tasks"][task_id]
            
            # Guardar cambios
            self._save_tasks()
            
            return True
        return False
    
    def get_task(self, user_id: str, task_id: str) -> Optional[dict]:
        """Obtiene una tarea específica de un usuario"""
        user_data = self._get_user_data(user_id)
        
        # Normalizar task_id a formato de 6 dígitos si es necesario
        if task_id.isdigit():
            task_id = self._format_task_id(int(task_id))
        
        return user_data["tasks"].get(task_id)
