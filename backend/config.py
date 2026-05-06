"""
Configuración centralizada del backend
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorios
BASE_DIR = Path(__file__).parent
MCP_SERVERS_DIR = BASE_DIR / "mcp_servers"

# API Server
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tasks.db")

# MCP Servers
MCP_LOCAL_TASKS_ENABLED = os.getenv("MCP_LOCAL_TASKS_ENABLED", "true").lower() == "true"
MCP_LOCAL_TASKS_COMMAND = "python"
MCP_LOCAL_TASKS_SCRIPT = str(MCP_SERVERS_DIR / "local_tasks_server.py")

MCP_REMOTE_WEATHER_ENABLED = os.getenv("MCP_REMOTE_WEATHER_ENABLED", "false").lower() == "true"
MCP_REMOTE_WEATHER_URL = os.getenv("MCP_REMOTE_WEATHER_URL", "http://localhost:8080")

# Rate Limiting
RATE_LIMIT_STORAGE = os.getenv("RATE_LIMIT_STORAGE", "memory://")  # Usar "redis://localhost:6379" en producción
RATE_LIMIT_DEFAULT = "100 per hour"
RATE_LIMIT_LOGIN = "5 per minute"
RATE_LIMIT_CREATE = "10 per minute"

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
