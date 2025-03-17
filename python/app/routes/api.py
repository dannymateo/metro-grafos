from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import json
import logging
from app.services.weather_service import weather_monitoring_system
from app.services.metro_service import metro_system
from app.utils.graph_utils import generate_graph_visualization
from app.config import METRO_LINES
from data.coordinates import STATION_COORDINATES

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    weather_monitoring_system.connected_clients.add(websocket)
    
    try:
        # Enviar datos iniciales: clima y historial de rutas
        initial_data = {
            "type": "initial_data",
            "data": {
                "weather_conditions": weather_monitoring_system.update_weather(),
                "route_history": metro_system.route_history
            }
        }
        await websocket.send_json(initial_data)
        
        while True:
            data = json.loads(await websocket.receive_text())
            origin = data.get("origin")
            destination = data.get("destination")
            
            if origin and destination:
                route = metro_system.find_route(origin, destination)
                if route:
                    # Enviar la nueva ruta a todos los clientes conectados
                    route_update = {
                        "type": "route_update",
                        "data": {
                            "new_route": route,
                            "route_history": metro_system.route_history
                        }
                    }
                    await broadcast_to_clients(route_update)
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No se encontró una ruta disponible"
                    })
                    
    except WebSocketDisconnect:
        weather_monitoring_system.connected_clients.remove(websocket)
    except Exception as e:
        logger.error(f"Error en websocket: {e}")
        weather_monitoring_system.connected_clients.remove(websocket)

async def broadcast_to_clients(message):
    """Envía un mensaje a todos los clientes conectados"""
    disconnected_clients = set()
    for client in weather_monitoring_system.connected_clients:
        try:
            await client.send_json(message)
        except Exception as e:
            logger.error(f"Error al enviar mensaje: {e}")
            disconnected_clients.add(client)
    
    weather_monitoring_system.connected_clients -= disconnected_clients

@router.get("/stations")
async def get_stations():
    """Obtener lista de todas las estaciones"""
    return {"stations": list(metro_system.metro_graph.nodes())}

@router.get("/coordinates")
async def get_coordinates():
    """Obtener coordenadas de todas las estaciones"""
    return {"coordinates": STATION_COORDINATES}

@router.get("/lines")
async def get_lines():
    """Obtener información de todas las líneas del metro"""
    return {"lines": METRO_LINES}

@router.get("/routes/history")
async def get_route_history():
    """Obtener historial de rutas ordenado por más reciente"""
    return {
        "routes": metro_system.route_history,
        "metadata": {
            "total_routes": len(metro_system.route_history),
            "last_updated": metro_system.route_history[0]["timestamp"] if metro_system.route_history else None
        }
    }

@router.get("/weather/current")
async def get_current_weather():
    """Obtener condiciones climáticas actuales de todas las estaciones"""
    return {
        "weather_conditions": weather_monitoring_system.update_weather(),
        "metadata": {
            "stations_reporting": len(weather_monitoring_system.stations),
            "last_updated": weather_monitoring_system._last_update.isoformat() if weather_monitoring_system._last_update else None
        }
    }

@router.get("/graph")
async def get_graph():
    """Genera y devuelve una visualización del grafo del sistema"""
    buf = generate_graph_visualization(metro_system)
    return StreamingResponse(buf, media_type="image/png")

@router.get("/route")
async def get_route(origin: str, destination: str):
    """Calcular ruta entre dos estaciones"""
    route = metro_system.find_route(origin, destination)
    if route:
        return {
            "status": "success",
            "route": route
        }
    return {
        "status": "error",
        "message": "No se encontró una ruta disponible"
    }

@router.get("/station/{station_name}")
async def get_station_info(station_name: str):
    """Obtener información detallada de una estación específica"""
    if station_name not in STATION_COORDINATES:
        return {
            "status": "error",
            "message": "Estación no encontrada"
        }
    
    # Obtener líneas que pasan por la estación
    station_lines = []
    for line_name, line_info in METRO_LINES.items():
        if station_name in line_info["stations"]:
            station_lines.append({
                "line": line_name,
                "color": line_info["color"]
            })
    
    # Obtener clima actual de la estación
    weather = weather_monitoring_system.update_weather().get(station_name, {})
    
    return {
        "status": "success",
        "station_info": {
            "name": station_name,
            "coordinates": STATION_COORDINATES[station_name],
            "lines": station_lines,
            "weather": weather,
            "connections": list(metro_system.metro_graph.neighbors(station_name))
        }
    } 