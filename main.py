from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data.coordinates import STATION_COORDINATES
from fastapi.responses import FileResponse, StreamingResponse
from math import radians, sin, cos, sqrt, atan2
import networkx as nx
import logging
import json
from datetime import datetime, timezone
import random
from asyncio import create_task, sleep
import asyncio
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definir líneas del metro antes de la clase
lineas = {
    "A": {
        "color": "#007bff",
        "stations": ["Niquía", "Bello", "Madera", "Acevedo", "Tricentenario", "Caribe",
                    "Universidad", "Hospital", "Prado", "Parque Berrío", "San Antonio",
                    "Alpujarra", "Exposiciones", "Industriales", "Poblado", "Aguacatala",
                    "Ayurá", "Envigado", "Itagüí", "Sabaneta", "La Estrella"]
    },
    "B": {
        "color": "#fd7e14",
        "stations": ["San Antonio", "Cisneros", "Suramericana", "Estadio", 
                    "Floresta", "Santa Lucía", "San Javier"]
    },
    "H": {
        "color": "#e83e8c",
        "stations": ["Oriente", "Las Torres", "Villa Sierra"]
    },
    "J": {
        "color": "#ffc107",
        "stations": ["San Javier", "Juan XXIII", "Vallejuelos", "La Aurora"]
    },
    "K": {
        "color": "#28a745",
        "stations": ["Acevedo", "Andalucía", "Popular", "Santo Domingo"]
    },
    "L": {
        "color": "#8B4513",
        "stations": ["Santo Domingo", "Arví"]
    },
    "M": {
        "color": "#6f42c1",
        "stations": ["Miraflores", "Trece de Noviembre"]
    },
    "P": {
        "color": "#dc3545",
        "stations": ["Acevedo", "Sena", "Doce de Octubre", "El Progreso"]
    },
    "TA": {
        "color": "#28a745",
        "stations": ["San Antonio", "San José", "Pabellón del Agua EPM", "Bicentenario",
                    "Buenos Aires", "Miraflores", "Loyola", "Alejandro Echavarría", "Oriente"]
    }
}

# Constantes y configuración
WEATHER_UPDATE_INTERVAL = 15  # segundos
MAX_HISTORY_SIZE = 10
DEFAULT_COORDINATES = (6.2442, -75.5812)

# Mejorar la estructura de datos del clima
WEATHER_STATES = {
    "sunny": {
        "id": "sunny",
        "name": "Soleado",
        "icon": "☀️",
        "color": "#FFD700",
        "opacity": 0.4,
        "radius": 600,
        "transitions": {"sunny": 0.7, "cloudy": 0.2, "rainy": 0.1, "stormy": 0},
        "temp_range": (22, 30),
        "humidity_range": (30, 60),
        "visibility_range": (8, 10)
    },
    "cloudy": {
        "id": "cloudy",
        "name": "Nublado",
        "icon": "☁️",
        "color": "#A9A9A9",
        "opacity": 0.5,
        "radius": 800,
        "transitions": {"sunny": 0.2, "cloudy": 0.5, "rainy": 0.2, "stormy": 0.1},
        "temp_range": (18, 25),
        "humidity_range": (50, 80),
        "visibility_range": (5, 8)
    },
    "rainy": {
        "id": "rainy",
        "name": "Lluvioso",
        "icon": "🌧️",
        "color": "#4682B4",
        "opacity": 0.6,
        "radius": 700,
        "transitions": {"sunny": 0.1, "cloudy": 0.2, "rainy": 0.5, "stormy": 0.2},
        "temp_range": (15, 22),
        "humidity_range": (70, 95),
        "visibility_range": (3, 6)
    },
    "stormy": {
        "id": "stormy",
        "name": "Tormenta",
        "icon": "⛈️",
        "color": "#483D8B",
        "opacity": 0.7,
        "radius": 900,
        "transitions": {"sunny": 0, "cloudy": 0.2, "rainy": 0.3, "stormy": 0.5},
        "temp_range": (12, 20),
        "humidity_range": (80, 100),
        "visibility_range": (1, 4)
    }
}

@dataclass
class WeatherStation:
    station_id: str
    location: Tuple[float, float]
    sensor_type: str = "METRO-AWS-2000"
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    weather_data: Dict = field(default_factory=dict)
    status: str = "operational"

    def generate_readings(self, weather_state: dict) -> Dict:
        return {
            "temperature": round(random.uniform(*weather_state["temp_range"]), 1),
            "humidity": round(random.uniform(*weather_state["humidity_range"]), 1),
            "visibility": round(random.uniform(*weather_state["visibility_range"]), 1),
            "pressure": round(random.uniform(1008, 1020), 1)
        }

class WeatherMonitoringSystem:
    def __init__(self):
        self.stations: Dict[str, WeatherStation] = {}
        self.initialize_stations()
        self._cache = {}
        self._last_update = None

    def initialize_stations(self):
        for station_name, coords in STATION_COORDINATES.items():
            station_id = f"MDE-{abs(hash(station_name)) % 1000:03d}"
            self.stations[station_name] = WeatherStation(
                station_id=station_id,
                location=coords
            )

    def update_weather(self) -> Dict[str, Dict]:
        current_time = datetime.now(timezone.utc)
        if (self._last_update and 
            (current_time - self._last_update).total_seconds() < WEATHER_UPDATE_INTERVAL):
            return self._cache

        updated_conditions = {}
        for station_name, station in self.stations.items():
            current = station.weather_data.get("type", "sunny")
            weather_state = WEATHER_STATES[current]
            
            # Determinar siguiente estado del clima
            transitions = weather_state["transitions"]
            next_state = random.choices(
                list(transitions.keys()),
                weights=list(transitions.values())
            )[0]
            
            new_state = WEATHER_STATES[next_state]
            readings = station.generate_readings(new_state)
            
            station.weather_data = {
                "type": next_state,
                "intensity": random.uniform(0.8, 1.0),
                "readings": readings
            }
            station.last_updated = current_time
            
            updated_conditions[station_name] = {
                "station_id": station.station_id,
                "type": next_state,
                "name": new_state["name"],
                "icon": new_state["icon"],
                "intensity": station.weather_data["intensity"],
                "location": station.location,
                "readings": readings,
                "last_updated": current_time.isoformat(),
                "status": station.status
            }

        self._cache = updated_conditions
        self._last_update = current_time
        return updated_conditions

class MetroSystem:
    # Definir constantes de clase
    WEATHER_SPEED_FACTORS = {
        "sunny": 1.0,      # Velocidad normal
        "cloudy": 0.9,     # 10% más lento
        "rainy": 0.75,     # 25% más lento
        "stormy": 0.6      # 40% más lento
    }

    SPEEDS = {
        "metro": 35.0,    # Metro: 35 km/h promedio
        "cable": 18.0,    # Metrocable: 18 km/h promedio
        "tranvia": 20.0   # Tranvía: 20 km/h promedio
    }

    LINE_TYPES = {
        "A": "metro", "B": "metro",
        "H": "cable", "J": "cable", "K": "cable",
        "L": "cable", "M": "cable", "P": "cable",
        "TA": "tranvia"
    }

    def __init__(self):
        self.metro_graph = nx.Graph()
        self.current_route = None
        self.route_history = []
        self.weather_conditions = {}
        self.connected_clients = set()
        self.weather_monitoring = WeatherMonitoringSystem()
        self.initialize_graph()
        # Inicializar el clima al crear la instancia
        self.update_weather()

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371  # Radio de la Tierra en km
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return 2 * R * atan2(sqrt(a), sqrt(1-a))

    def calculate_travel_time(self, station1, station2, line):
        if station1 not in STATION_COORDINATES or station2 not in STATION_COORDINATES:
            return 1.0
            
        coords1, coords2 = STATION_COORDINATES[station1], STATION_COORDINATES[station2]
        distance = self.calculate_distance(coords1[0], coords1[1], coords2[0], coords2[1])
        base_speed = self.SPEEDS[self.LINE_TYPES.get(line, "metro")]

        # Obtener condiciones climáticas de ambas estaciones
        weather1 = self.weather_conditions.get(station1, {})
        weather2 = self.weather_conditions.get(station2, {})
        
        # Usar el clima más severo entre las dos estaciones
        weather_factor = min(
            self.WEATHER_SPEED_FACTORS[weather1.get('type', 'sunny')],
            self.WEATHER_SPEED_FACTORS[weather2.get('type', 'sunny')]
        )
        
        adjusted_speed = base_speed * weather_factor
        travel_time = (distance / adjusted_speed) * 60  # Convertir a minutos

        return max(travel_time, 0.5)

    def initialize_graph(self):
        # Asegurarse de que todas las estaciones tengan coordenadas
        for linea, info in lineas.items():
            stations = info["stations"]
            for station in stations:
                if station not in STATION_COORDINATES:
                    # Asignar coordenadas aproximadas basadas en estaciones vecinas
                    neighbors = [s for s in stations if s in STATION_COORDINATES]
                    if neighbors:
                        neighbor = neighbors[0]
                        # Añadir un pequeño offset a las coordenadas del vecino
                        lat, lon = STATION_COORDINATES[neighbor]
                        STATION_COORDINATES[station] = [
                            lat + random.uniform(-0.001, 0.001),
                            lon + random.uniform(-0.001, 0.001)
                        ]
                    else:
                        # Si no hay vecinos con coordenadas, usar coordenadas por defecto
                        STATION_COORDINATES[station] = [6.2442, -75.5812]

            # Continuar con la inicialización normal del grafo
            for i in range(len(stations) - 1):
                station1, station2 = stations[i], stations[i + 1]
                time = self.calculate_travel_time(station1, station2, linea)
                self.metro_graph.add_edge(
                    station1, station2,
                    line=linea,
                    color=info["color"],
                    weight=time
                )

    def add_to_history(self, route):
        """Agregar ruta al historial con ID único"""
        route_with_id = {
            **route,
            "id": len(self.route_history),
            "timestamp": datetime.now().isoformat()
        }
        self.route_history.insert(0, route_with_id)  # Agregar al inicio
        if len(self.route_history) > 10:  # Mantener solo las últimas 10 rutas
            self.route_history.pop()
        return route_with_id

    async def broadcast_weather(self):
        """Envía actualizaciones del clima a todos los clientes conectados"""
        if self.connected_clients:
            message = {
                "type": "weather_update",
                "weather_conditions": self.weather_conditions,
                "metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "stations_reporting": len(self.weather_conditions),
                    "system_status": "operational"
                }
            }
            
            disconnected_clients = set()
            for client in self.connected_clients:
                try:
                    await client.send_json(message)
                except Exception as e:
                    logger.error(f"Error al enviar actualización del clima: {e}")
                    disconnected_clients.add(client)
            
            self.connected_clients -= disconnected_clients

    async def update_weather_periodically(self):
        """Actualiza y transmite el clima periódicamente"""
        while True:
            try:
                self.update_weather()
                await self.broadcast_weather()
                await asyncio.sleep(15)  # Cambiar a 15 segundos
            except Exception as e:
                logger.error(f"Error en actualización periódica del clima: {e}")
                await asyncio.sleep(1)

    def update_weather(self):
        """Actualiza las condiciones climáticas basadas en lecturas de sensores"""
        updated_conditions = {}
        
        for station_name, weather_station in self.weather_monitoring.stations.items():
            weather_data = self.weather_monitoring.update_weather()[station_name]
            weather_station.weather_data = weather_data
            weather_station.last_updated = datetime.now(timezone.utc)
            
            # Preparar datos para el cliente
            updated_conditions[station_name] = {
                "type": weather_data["type"],
                "intensity": weather_data["intensity"],
                "name": weather_data["name"],
                "icon": weather_data["icon"],
                "location": weather_data["location"],
                "readings": weather_data["readings"],
                "station_id": weather_data["station_id"],
                "last_updated": weather_data["last_updated"],
                "status": weather_data["status"]
            }
        
        self.weather_conditions = updated_conditions

    def find_route(self, origin, destination):
        try:
            path = nx.shortest_path(self.metro_graph, origin, destination, weight='weight')
            
            total_time = 0
            total_distance = 0  # Añadir variable para distancia total
            lines = []
            current_line = None
            transbordos = []
            weather_impacts = []
            
            for i in range(len(path) - 1):
                station1, station2 = path[i], path[i + 1]
                edge = self.metro_graph[station1][station2]
                
                # Calcular distancia del segmento
                coords1 = STATION_COORDINATES[station1]
                coords2 = STATION_COORDINATES[station2]
                segment_distance = self.calculate_distance(coords1[0], coords1[1], coords2[0], coords2[1])
                total_distance += segment_distance
                
                base_time = self.calculate_travel_time(station1, station2, edge['line'])
                
                # Calcular impacto del clima
                weather1 = self.weather_conditions.get(station1, {})
                weather2 = self.weather_conditions.get(station2, {})
                
                if edge.get('line') != 'transbordo':
                    if current_line != edge['line']:
                        current_line = edge['line']
                        lines.append(current_line)
                    
                    # Añadir información sobre el impacto del clima
                    if weather1.get('type') != 'sunny' or weather2.get('type') != 'sunny':
                        weather_impacts.append({
                            "segment": [station1, station2],
                            "line": edge['line'],
                            "conditions": {
                                "origin": {
                                    "station": station1,
                                    "weather": weather1.get('name', 'Soleado'),
                                    "impact": round((1 - self.WEATHER_SPEED_FACTORS[weather1.get('type', 'sunny')]) * 100)
                                },
                                "destination": {
                                    "station": station2,
                                    "weather": weather2.get('name', 'Soleado'),
                                    "impact": round((1 - self.WEATHER_SPEED_FACTORS[weather2.get('type', 'sunny')]) * 100)
                                }
                            }
                        })
                else:
                    transbordos.append(path[i])
                    base_time += 3  # Tiempo adicional por transbordo

                total_time += base_time

            route = {
                "path": path,
                "coordinates": [STATION_COORDINATES[station] for station in path],
                "num_stations": len(path) - 1,
                "lines": lines,
                "estimated_time": round(total_time),
                "total_distance": round(total_distance, 2),  # Distancia en kilómetros
                "transbordos": transbordos,
                "weather_impacts": weather_impacts,
                "weather_conditions": self.weather_conditions
            }
            
            return self.add_to_history(route)
        except nx.NetworkXNoPath:
            return None

metro_system = MetroSystem()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    metro_system.connected_clients.add(websocket)
    
    try:
        # Enviar datos iniciales del clima
        initial_data = {
            "type": "weather_update",
            "weather_conditions": metro_system.weather_monitoring.update_weather()
        }
        await websocket.send_json(initial_data)
        
        while True:
            data = json.loads(await websocket.receive_text())
            origin = data.get("origin")
            destination = data.get("destination")
            
            route = metro_system.find_route(origin, destination)
            if route:
                await websocket.send_json(route)
            else:
                await websocket.send_json({"error": "No se encontró una ruta disponible"})
    except WebSocketDisconnect:
        metro_system.connected_clients.remove(websocket)
    except Exception as e:
        logger.error(f"Error en websocket: {e}")
        metro_system.connected_clients.remove(websocket)

@app.get("/stations")
async def get_stations():
    return {"stations": list(metro_system.metro_graph.nodes())}

@app.get("/coordinates")
async def get_coordinates():
    return {"coordinates": STATION_COORDINATES}

@app.get("/lines")
async def get_lines():
    return {"lines": lineas}

@app.get("/routes/history")
async def get_route_history():
    """Obtener historial de rutas ordenado por más reciente"""
    return {
        "routes": metro_system.route_history
    }

@app.get("/graph")
async def get_graph():
    """Genera y devuelve una visualización del grafo del sistema"""
    plt.figure(figsize=(15, 10))
    
    # Crear un grafo nuevo para la visualización
    G = metro_system.metro_graph.copy()
    
    # Obtener posiciones para el layout usando las coordenadas reales
    pos = {station: [STATION_COORDINATES[station][1], STATION_COORDINATES[station][0]] 
           for station in G.nodes()}
    
    # Dibujar las líneas del metro con diferentes colores
    for line_name, line_info in lineas.items():
        edge_list = [
            (station1, station2)
            for station1, station2 in zip(line_info["stations"], line_info["stations"][1:])
            if G.has_edge(station1, station2)
        ]
        nx.draw_networkx_edges(G, pos, edgelist=edge_list, 
                             edge_color=line_info["color"],
                             width=2)

    # Si hay una ruta actual en el historial, dibujarla en rojo
    if metro_system.route_history:
        current_route = metro_system.route_history[0]  # Última ruta calculada
        path = current_route["path"]
        
        # Crear lista de pares de estaciones consecutivas en la ruta
        route_edges = list(zip(path[:-1], path[1:]))
        
        # Dibujar la ruta en rojo y más gruesa
        nx.draw_networkx_edges(G, pos,
                             edgelist=route_edges,
                             edge_color='red',
                             width=4,
                             alpha=0.7)
        
        # Resaltar nodos de origen y destino
        nx.draw_networkx_nodes(G, pos,
                             nodelist=[path[0]],  # Origen
                             node_color='green',
                             node_size=300,
                             node_shape='o')
        nx.draw_networkx_nodes(G, pos,
                             nodelist=[path[-1]],  # Destino
                             node_color='red',
                             node_size=300,
                             node_shape='o')

    # Dibujar los nodos (estaciones)
    nx.draw_networkx_nodes(G, pos, 
                          node_color='white',
                          node_size=200,
                          edgecolors='black',
                          linewidths=1)
    
    # Añadir etiquetas de las estaciones
    labels = {node: node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, 
                          font_size=8,
                          font_weight='bold')
    
    # Añadir título y leyenda
    plt.title("Sistema Metro de Medellín", pad=20, fontsize=16)
    
    # Crear leyenda para las líneas
    legend_elements = [
        plt.Line2D([0], [0], color=info["color"], label=f'Línea {line}')
        for line, info in lineas.items()
    ]
    if metro_system.route_history:
        legend_elements.append(
            plt.Line2D([0], [0], color='red', linewidth=4, label='Ruta actual')
        )
    plt.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
    
    # Ajustar los márgenes
    plt.margins(0.15)
    plt.tight_layout()
    
    # Guardar el gráfico en un buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return StreamingResponse(buf, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Iniciar la tarea de actualización del clima cuando la aplicación arranca
        weather_task = asyncio.create_task(metro_system.update_weather_periodically())
        yield
        # Cancelar la tarea cuando la aplicación se detiene
        weather_task.cancel()
        try:
            await weather_task
        except asyncio.CancelledError:
            logger.info("Tarea de clima cancelada")

    app.router.lifespan_context = lifespan
    uvicorn.run(app, host="0.0.0.0", port=8000)
