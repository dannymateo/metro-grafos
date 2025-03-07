from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi import Request
from pydantic import BaseModel
import networkx as nx
from typing import List, Dict, Optional, Set
import json
from datetime import datetime
import logging
from fastapi.middleware.cors import CORSMiddleware
from data.coordinates import STATION_COORDINATES
from fastapi.responses import FileResponse
from math import radians, sin, cos, sqrt, atan2

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Metro Medellín API",
    description="API para calcular rutas óptimas en el Metro de Medellín",
    version="1.0.0"
)

# Crear el grafo del metro
metro_graph = nx.Graph()

# Definir las estaciones de todas las líneas
lineas = {
    "A": {
        "color": "#007bff",  # Azul
        "stations": [
            "Niquía", "Bello", "Madera", "Acevedo", "Tricentenario", "Caribe",
            "Universidad", "Hospital", "Prado", "Parque Berrío", "San Antonio",
            "Alpujarra", "Exposiciones", "Industriales", "Poblado", "Aguacatala",
            "Ayurá", "Envigado", "Itagüí", "Sabaneta", "La Estrella"
        ]
    },
    "B": {
        "color": "#fd7e14",  # Naranja
        "stations": [
            "San Antonio", "Cisneros", "Suramericana", "Estadio", 
            "Floresta", "Santa Lucía", "San Javier"
        ]
    },
    "H": {
        "color": "#e83e8c",  # Rosa
        "stations": [
            "Oriente", "Las Torres", "Villa Sierra"
        ]
    },
    "J":{
        "color": "#ffc107",  # Amarillo
        "stations": ["Juan XXIII", "Vallejuelos", "La Aurora"]
    },
    "K":{
        "color": "#28a745",  # Verde claro
        "stations": ["Acevedo", "Andalucía", "Popular", "Santo Domingo"]
    },
    "L":{
        "color": "#8B4513",  # Café
        "stations": ["Santo Domingo", "Arví"]
    },
    "M":{
        "color": "#6f42c1",  # Morado
        "stations": ["Miraflores", "Trece de Noviembre"]
    },
    "P": {
        "color": "#dc3545",  # Rojo
        "stations": ["Acevedo", "Sena", "Doce de Octubre", "El progreso"]
    },
    "TA": {
        "color": "#28a745",  # Verde oscuro
        "stations": ["San Antonio", "San José", "Pabellón del Agua EPM", "Bicentenario", "Buenos Aires", "Miraflores", "Loyola", "Alejandro Echavarría", "Oriente"]
    }
}

# Agregar nodos y conexiones para todas las líneas
logger.info("Iniciando la construcción del grafo del metro...")
for linea, info in lineas.items():
    stations = info["stations"]
    logger.debug(f"Agregando estaciones de la línea {linea}: {stations}")
    for i in range(len(stations) - 1):
        metro_graph.add_edge(
            stations[i], 
            stations[i + 1], 
            line=linea,
            color=info["color"],
            weight=1
        )

# Agregar conexiones entre líneas (transbordos)
transbordos = [
    ("San Antonio", ["A", "B", "TA"]),
    ("Acevedo", ["A", "K", "P"]),
    ("Santo Domingo", ["K", "L"]),
    ("Miraflores", ["TA", "M"]),
    ("Oriente", ["TA", "H"]),
    ("San Javier", ["B", "J"])
]

logger.info("Agregando conexiones de transbordo...")
for estacion, lineas_conectadas in transbordos:
    logger.debug(f"Procesando transbordo en estación {estacion}")
    for i in range(len(lineas_conectadas)):
        for j in range(i + 1, len(lineas_conectadas)):
            linea1, linea2 = lineas_conectadas[i], lineas_conectadas[j]
            if estacion in lineas[linea1]["stations"] and estacion in lineas[linea2]["stations"]:
                metro_graph.add_edge(
                    estacion,
                    estacion,
                    line="transbordo",
                    weight=0.5
                )

# Agregar el middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nueva conexión WebSocket. Total conexiones: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Conexión WebSocket cerrada. Total conexiones: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

class RouteRequest(BaseModel):
    origin: str
    destination: str

class RouteResponse(BaseModel):
    path: List[str]
    num_stations: int
    lines: List[str]
    estimated_time: int
    transbordos: List[str]

class RealTimeFactors(BaseModel):
    traffic: Dict[str, int]  # Estaciones y su nivel de tráfico
    weather: Dict[str, str]   # Estaciones y su condición climática

class RouteHistory:
    def __init__(self):
        self.routes: List[Dict] = []
        
    def add_route(self, route: Dict):
        route['id'] = len(self.routes)
        route['timestamp'] = datetime.now().isoformat()
        self.routes.append(route)
        if len(self.routes) > 100:
            self.routes.pop(0)
            
    def get_routes(self):
        return self.routes

class AdminActions:
    def __init__(self):
        self.closed_stations: Set[str] = set()
        self.manual_congestion: Dict[str, float] = {}

class MetroSystem:
    def __init__(self):
        self.metro_graph = nx.Graph()
        self.station_status = {}  # Para almacenar el estado de las estaciones
        self.congestion_levels = {}  # Para almacenar niveles de congestión
        self.current_route = None
        self.route_history = RouteHistory()
        self.admin = AdminActions()
        self.BASE_TRAVEL_TIME = 2  # 2 minutos entre estaciones en condiciones normales
        self.TRANSFER_TIME = 3     # 3 minutos para transbordos
        self.INFINITE_WEIGHT = 1000000  # Peso para estaciones cerradas
        self.WALKING_SPEED = 5  # km/h para cálculos de tiempo caminando
        
        self.initialize_graph()

    def initialize_graph(self):
        # Inicializar estado de estaciones
        for line_info in lineas.values():
            for station in line_info["stations"]:
                self.station_status[station] = {
                    "status": "open",
                    "maintenance": None
                }
                self.congestion_levels[station] = 1.0  # Congestión normal

        # Construir grafo con pesos iniciales
        for linea, info in lineas.items():
            stations = info["stations"]
            for i in range(len(stations) - 1):
                self.metro_graph.add_edge(
                    stations[i],
                    stations[i + 1],
                    line=linea,
                    color=info["color"],
                    base_weight=1,
                    weight=1
                )

    def _update_edge_weights(self, station, multiplier):
        """Actualizar pesos de las conexiones de una estación"""
        for neighbor in self.metro_graph.neighbors(station):
            edge_data = self.metro_graph[station][neighbor]
            base_weight = edge_data.get('base_weight', 1)
            # Limitar el multiplicador máximo para congestión
            if multiplier < self.INFINITE_WEIGHT:  # Si no es cierre de estación
                multiplier = min(multiplier, 2.0)  # Máximo duplicar el tiempo por congestión
            self.metro_graph[station][neighbor]['weight'] = base_weight * multiplier

    def close_station(self, station: str, reason: str):
        """Cerrar una estación"""
        self.station_status[station]["status"] = "closed"
        self.station_status[station]["maintenance"] = reason
        self._update_edge_weights(station, self.INFINITE_WEIGHT)

    def open_station(self, station: str):
        """Abrir una estación"""
        self.station_status[station]["status"] = "open"
        self.station_status[station]["maintenance"] = None
        self._update_edge_weights(station, 1.0)

    def set_congestion(self, station: str, level: float):
        """Establecer nivel de congestión para una estación"""
        self.congestion_levels[station] = level
        self._update_edge_weights(station, level)

    def find_nearest_station(self, user_lat: float, user_lon: float) -> dict:
        """Encontrar la estación más cercana a las coordenadas del usuario"""
        nearest_station = None
        min_distance = float('inf')
        walking_time = 0

        for station, coords in STATION_COORDINATES.items():
            station_lat, station_lon = coords
            distance = self.calculate_distance(
                user_lat, user_lon,
                station_lat, station_lon
            )

            if distance < min_distance:
                min_distance = distance
                nearest_station = station
                # Convertir distancia a tiempo caminando (km / km/h * 60 = minutos)
                walking_time = (distance / self.WALKING_SPEED) * 60

        return {
            "station": nearest_station,
            "distance": round(min_distance, 2),
            "walking_time": round(walking_time),
            "coordinates": STATION_COORDINATES[nearest_station]
        }

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcular distancia entre dos puntos usando la fórmula de Haversine"""
        R = 6371  # Radio de la Tierra en km

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

    def update_station_status(self):
        """Actualizar el estado de las estaciones"""
        for station in self.metro_graph.nodes():
            if station not in self.station_status:
                self.station_status[station] = {
                    "status": "open",
                    "maintenance": None
                }

    def get_graph_image(self):
        """Generar imagen del grafo del metro"""
        import matplotlib.pyplot as plt
        import networkx as nx
        
        plt.figure(figsize=(15, 10))
        pos = nx.spring_layout(self.metro_graph)
        
        # Dibujar todas las aristas en gris claro
        nx.draw_networkx_edges(self.metro_graph, pos, 
                              edge_color='lightgray',
                              width=1)
        
        # Dibujar nodos normales
        nx.draw_networkx_nodes(self.metro_graph, pos, 
                              node_color='lightblue',
                              node_size=500)
        
        # Si hay una ruta actual, dibujarla en rojo
        if self.current_route:
            path_edges = list(zip(self.current_route[:-1], self.current_route[1:]))
            nx.draw_networkx_edges(self.metro_graph, pos,
                                 edgelist=path_edges,
                                 edge_color='red',
                                 width=2)
            
            # Resaltar nodos de origen y destino
            nx.draw_networkx_nodes(self.metro_graph, pos,
                                 nodelist=[self.current_route[0]],
                                 node_color='green',
                                 node_size=700)
            nx.draw_networkx_nodes(self.metro_graph, pos,
                                 nodelist=[self.current_route[-1]],
                                 node_color='red',
                                 node_size=700)
        
        # Agregar etiquetas
        nx.draw_networkx_labels(self.metro_graph, pos)
        
        # Guardar imagen
        plt.savefig('metro_graph.png', bbox_inches='tight')
        plt.close()
        
        return 'metro_graph.png'

metro_system = MetroSystem()

@app.get("/coordinates")
async def get_coordinates():
    """Obtener las coordenadas de todas las estaciones"""
    return {
        "coordinates": STATION_COORDINATES
    }

@app.get("/stations")
async def get_stations():
    """Obtener lista de estaciones y su estado"""
    stations_list = list(metro_system.metro_graph.nodes())
    return {
        "stations": stations_list,
        "status": metro_system.station_status
    }

@app.get("/lines")
async def get_lines():
    """Obtener información sobre las líneas del metro"""
    return {
        "lines": lineas
    }

@app.get("/graph")
async def get_graph():
    """Get current graph visualization"""
    metro_system.update_station_status()
    graph_path = metro_system.get_graph_image()
    return FileResponse(graph_path)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                route_request = json.loads(data)
                origin = route_request.get("origin")
                destination = route_request.get("destination")
                user_location = route_request.get("user_location")

                # Si se proporcionan coordenadas del usuario, encontrar la estación más cercana
                if user_location:
                    nearest = metro_system.find_nearest_station(
                        user_location["latitude"],
                        user_location["longitude"]
                    )
                    origin = nearest["station"]

                if (metro_system.station_status[origin]["status"] == "closed" or 
                    metro_system.station_status[destination]["status"] == "closed"):
                    await websocket.send_json({
                        "error": "Una o ambas estaciones están cerradas por mantenimiento"
                    })
                    continue

                try:
                    path = nx.shortest_path(
                        metro_system.metro_graph, 
                        origin, 
                        destination, 
                        weight='weight'
                    )
                    
                    metro_system.current_route = path
                    
                    total_time = 0
                    alerts = []
                    lines = []
                    current_line = None
                    transbordos = []
                    
                    for i in range(len(path) - 1):
                        edge_data = metro_system.metro_graph[path[i]][path[i + 1]]
                        total_time += edge_data['weight'] * metro_system.BASE_TRAVEL_TIME
                        
                        line = edge_data.get('line')
                        if line != 'transbordo':
                            if not current_line or current_line != line:
                                current_line = line
                                lines.append(line)
                        else:
                            transbordos.append(path[i])
                            total_time += metro_system.TRANSFER_TIME
                        
                        # Alertas de congestión
                        if metro_system.congestion_levels[path[i]] > 1.3:
                            alerts.append(f"Alta congestión en {path[i]}")

                    response = {
                        "path": path,
                        "coordinates": [STATION_COORDINATES[station] for station in path],
                        "num_stations": len(path) - 1,
                        "lines": lines,
                        "estimated_time": round(total_time),
                        "transbordos": transbordos,
                        "alerts": alerts,
                        "congestion_levels": {
                            station: metro_system.congestion_levels[station] 
                            for station in path
                        },
                        "nearest_station": nearest if user_location else None,
                        "walking_info": {
                            "distance": nearest["distance"] if user_location else 0,
                            "time": nearest["walking_time"] if user_location else 0
                        } if user_location else None
                    }
                    
                    metro_system.route_history.add_route(response)
                    await websocket.send_json(response)
                    
                except nx.NetworkXNoPath:
                    await websocket.send_json({
                        "error": "No hay ruta disponible debido a cierres o mantenimiento"
                    })
                    
            except Exception as e:
                logger.error(f"Error: {str(e)}", exc_info=True)
                await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        metro_system.current_route = None
        manager.disconnect(websocket)

@app.post("/admin/station/{station_id}/close")
async def close_station(station_id: str, reason: str):
    if station_id in metro_system.metro_graph.nodes():
        metro_system.close_station(station_id, reason)
        return {"message": f"Estación {station_id} cerrada"}
    raise HTTPException(status_code=404, detail="Estación no encontrada")

@app.post("/admin/station/{station_id}/open")
async def open_station(station_id: str):
    if station_id in metro_system.metro_graph.nodes():
        metro_system.open_station(station_id)
        return {"message": f"Estación {station_id} abierta"}
    raise HTTPException(status_code=404, detail="Estación no encontrada")

@app.get("/admin/status")
async def get_admin_status():
    return {
        "closed_stations": list(metro_system.admin.closed_stations),
        "congestion_levels": metro_system.admin.manual_congestion
    }

@app.get("/routes/history")
async def get_route_history():
    return {"routes": metro_system.route_history.routes}

@app.post("/nearest-station")
async def find_nearest_station(coordinates: dict):
    """Encontrar la estación más cercana a las coordenadas dadas"""
    try:
        user_lat = float(coordinates["latitude"])
        user_lon = float(coordinates["longitude"])
        
        nearest = metro_system.find_nearest_station(user_lat, user_lon)
        
        return {
            "nearest_station": nearest["station"],
            "distance_km": nearest["distance"],
            "walking_time_minutes": nearest["walking_time"],
            "station_coordinates": nearest["coordinates"]
        }
    except Exception as e:
        logger.error(f"Error finding nearest station: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Error al calcular la estación más cercana"
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
