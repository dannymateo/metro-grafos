from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import json
import logging
from app.services.weather_service import weather_monitoring_system
from app.services.metro_service import metro_system
from app.utils.graph_utils import generate_graph_visualization
from app.config import METRO_LINES
from datetime import datetime, timezone

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    weather_monitoring_system.connected_clients.add(websocket)
    
    try:
        # Enviar datos iniciales
        initial_data = {
            "type": "initial_data",
            "data": {
                "weather_conditions": weather_monitoring_system.update_weather(),
                "route_history": metro_system.route_history
            }
        }
        await websocket.send_json(initial_data)
        
        while True:
            try:
                data = await websocket.receive_json()
                origin = data.get("origin")
                destination = data.get("destination")
                
                if not origin or not destination:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Origen y destino son requeridos"
                    })
                    continue
                
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
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Formato de mensaje inválido"
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
    all_stations = {}
    for line_info in METRO_LINES.values():
        all_stations.update(line_info["stations"])
    return {"coordinates": all_stations}

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
    logger.info(f"Solicitud de ruta: {origin} -> {destination}")
    
    if not origin or not destination:
        return {
            "status": "error",
            "message": "Origen y destino son requeridos"
        }
    
    route = metro_system.find_route(origin, destination)
    if route:
        logger.info(f"Ruta encontrada con {len(route['path'])} estaciones")
        return {
            "status": "success",
            "route": route
        }
    
    logger.error(f"No se encontró ruta entre {origin} y {destination}")
    return {
        "status": "error",
        "message": "No se encontró una ruta disponible"
    }

@router.get("/station/{station_name}")
async def get_station_info(station_name: str):
    """Obtener información detallada de una estación específica"""
    # Buscar la estación en todas las líneas
    station_found = False
    station_coordinates = None
    station_lines = []
    
    for line_name, line_info in METRO_LINES.items():
        if station_name in line_info["stations"]:
            station_found = True
            station_coordinates = line_info["stations"][station_name]
            station_lines.append({
                "line": line_name,
                "color": line_info["color"]
            })
    
    if not station_found:
        return {
            "status": "error",
            "message": "Estación no encontrada"
        }
    
    # Obtener clima actual de la estación
    weather = weather_monitoring_system.update_weather().get(station_name, {})
    
    return {
        "status": "success",
        "station_info": {
            "name": station_name,
            "coordinates": station_coordinates,
            "lines": station_lines,
            "weather": weather,
            "connections": list(metro_system.metro_graph.neighbors(station_name))
        }
    }

@router.get("/route/weather-impact")
async def get_weather_impact(origin: str, destination: str):
    """Calcular el impacto del clima en una ruta específica"""
    logger.info(f"Solicitud de impacto del clima en ruta: {origin} -> {destination}")
    
    if not origin or not destination:
        return {
            "status": "error",
            "message": "Origen y destino son requeridos"
        }
    
    impact = metro_system.get_weather_impact_on_route(origin, destination)
    
    if "error" in impact:
        return {
            "status": "error",
            "message": impact["error"]
        }
    
    return {
        "status": "success",
        "impact": impact
    }

@router.post("/weather/force-update")
async def force_weather_update():
    """Forzar una actualización del clima y recalcular los pesos del grafo"""
    try:
        # Forzar actualización del clima
        weather_monitoring_system._last_update = None  # Resetear el tiempo de última actualización
        updated_conditions = weather_monitoring_system.update_weather()
        
        # Transmitir a los clientes conectados
        if weather_monitoring_system.connected_clients:
            await weather_monitoring_system.broadcast_weather()
        
        return {
            "status": "success",
            "message": "Clima actualizado y pesos recalculados",
            "stations_updated": len(updated_conditions),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error al forzar actualización del clima: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        } 