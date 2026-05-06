#!/usr/bin/env python3
"""
MCP Server Remoto - Servicio de Clima
Servidor HTTP independiente que simula un MCP Server remoto
Se comunica via HTTP REST (no requiere librería MCP)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
from datetime import datetime

# Crear aplicación FastAPI
app = FastAPI(
    title="Weather MCP Server",
    description="Servidor MCP remoto para servicios de clima",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MODELOS DE DATOS
# ============================================================================

class WeatherRequest(BaseModel):
    """Petición de clima actual"""
    city: str = Field(..., description="Nombre de la ciudad")
    units: Optional[str] = Field("metric", description="Sistema de unidades (metric o imperial)")


class ForecastRequest(BaseModel):
    """Petición de pronóstico"""
    city: str = Field(..., description="Nombre de la ciudad")
    days: Optional[int] = Field(3, ge=1, le=7, description="Número de días (1-7)")


class WeatherResponse(BaseModel):
    """Respuesta de clima actual"""
    city: str
    temperature: float
    units: str
    condition: str
    humidity: int
    wind_speed: float
    timestamp: str


class ForecastDay(BaseModel):
    """Día del pronóstico"""
    day: int
    temp_max: float
    temp_min: float
    condition: str


class ForecastResponse(BaseModel):
    """Respuesta de pronóstico"""
    city: str
    forecast: List[ForecastDay]


class ToolsResponse(BaseModel):
    """Lista de herramientas disponibles"""
    tools: List[dict]


# ============================================================================
# DATOS SIMULADOS
# ============================================================================

# Datos de clima por ciudad (simulados)
WEATHER_DATA = {
    "madrid": {"temp_c": 22, "temp_f": 72, "condition": "Soleado", "humidity": 65, "wind": 15},
    "barcelona": {"temp_c": 24, "temp_f": 75, "condition": "Parcialmente nublado", "humidity": 70, "wind": 12},
    "valencia": {"temp_c": 26, "temp_f": 79, "condition": "Soleado", "humidity": 60, "wind": 10},
    "sevilla": {"temp_c": 28, "temp_f": 82, "condition": "Muy soleado", "humidity": 55, "wind": 8},
    "default": {"temp_c": 20, "temp_f": 68, "condition": "Nublado", "humidity": 75, "wind": 18}
}


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Información del servidor"""
    return {
        "name": "Weather MCP Server",
        "version": "1.0.0",
        "description": "Servidor MCP remoto para servicios de clima",
        "endpoints": {
            "tools": "/tools",
            "weather": "/weather",
            "forecast": "/forecast",
            "health": "/health"
        }
    }


@app.get("/tools", response_model=ToolsResponse, tags=["MCP"])
async def list_tools():
    """
    Lista las herramientas disponibles en este servidor MCP
    Equivalente a list_tools() en MCP stdio
    """
    return {
        "tools": [
            {
                "name": "get_weather",
                "description": "Obtiene el clima actual de una ciudad",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "Nombre de la ciudad"
                        },
                        "units": {
                            "type": "string",
                            "enum": ["metric", "imperial"],
                            "description": "Sistema de unidades",
                            "default": "metric"
                        }
                    },
                    "required": ["city"]
                }
            },
            {
                "name": "get_forecast",
                "description": "Obtiene el pronóstico del clima para los próximos días",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "Nombre de la ciudad"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Número de días (1-7)",
                            "minimum": 1,
                            "maximum": 7,
                            "default": 3
                        }
                    },
                    "required": ["city"]
                }
            }
        ]
    }


@app.post("/weather", response_model=WeatherResponse, tags=["Weather"])
async def get_weather(request: WeatherRequest):
    """
    Obtiene el clima actual de una ciudad
    Equivalente a call_tool("get_weather", ...) en MCP stdio
    """
    city_lower = request.city.lower()
    
    # Buscar datos de la ciudad
    weather = WEATHER_DATA.get(city_lower, WEATHER_DATA["default"])
    
    # Seleccionar temperatura según unidades
    temp = weather["temp_c"] if request.units == "metric" else weather["temp_f"]
    units = "°C" if request.units == "metric" else "°F"
    
    return WeatherResponse(
        city=request.city,
        temperature=temp,
        units=units,
        condition=weather["condition"],
        humidity=weather["humidity"],
        wind_speed=weather["wind"],
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.post("/forecast", response_model=ForecastResponse, tags=["Weather"])
async def get_forecast(request: ForecastRequest):
    """
    Obtiene el pronóstico del clima para los próximos días
    Equivalente a call_tool("get_forecast", ...) en MCP stdio
    """
    city_lower = request.city.lower()
    
    # Buscar datos base de la ciudad
    weather = WEATHER_DATA.get(city_lower, WEATHER_DATA["default"])
    base_temp = weather["temp_c"]
    
    # Generar pronóstico simulado
    forecast_days = []
    conditions = ["Soleado", "Parcialmente nublado", "Nublado", "Lluvioso", "Soleado", "Despejado", "Nublado"]
    
    for day in range(1, request.days + 1):
        temp_variation = (day % 3) - 1  # -1, 0, 1
        forecast_days.append(
            ForecastDay(
                day=day,
                temp_max=base_temp + 3 + temp_variation,
                temp_min=base_temp - 2 + temp_variation,
                condition=conditions[day % len(conditions)]
            )
        )
    
    return ForecastResponse(
        city=request.city,
        forecast=forecast_days
    )


@app.get("/health", tags=["Info"])
async def health():
    """Health check del servidor"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "Weather MCP Server"
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🌤️  Weather MCP Server (HTTP)")
    print("=" * 60)
    print("📡 Protocolo: HTTP REST")
    print("🎯 Puerto: 8080")
    print("📚 Docs: http://localhost:8080/docs")
    print("🔧 Tools: http://localhost:8080/tools")
    print("=" * 60)
    
    uvicorn.run(
        "remote_weather_server:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
