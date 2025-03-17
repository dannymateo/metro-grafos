import networkx as nx
from typing import Dict, List, Tuple
from datetime import datetime, timezone
import random
from math import radians, sin, cos, sqrt, atan2
from app.config import METRO_LINES
from data.coordinates import STATION_COORDINATES
from app.models.weather_monitoring import WeatherMonitoringSystem

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
        self.update_weather()

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371  # Radio de la Tierra en km
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return 2 * R * atan2(sqrt(a), sqrt(1-a))

    def calculate_travel_time(self, station1: str, station2: str, line: str) -> float:
        if station1 not in STATION_COORDINATES or station2 not in STATION_COORDINATES:
            return 1.0
            
        coords1, coords2 = STATION_COORDINATES[station1], STATION_COORDINATES[station2]
        distance = self.calculate_distance(coords1[0], coords1[1], coords2[0], coords2[1])
        base_speed = self.SPEEDS[self.LINE_TYPES.get(line, "metro")]

        weather1 = self.weather_conditions.get(station1, {'type': 'sunny'})
        weather2 = self.weather_conditions.get(station2, {'type': 'sunny'})
        
        weather_factor = min(
            self.WEATHER_SPEED_FACTORS.get(weather1.get('type', 'sunny'), 1.0),
            self.WEATHER_SPEED_FACTORS.get(weather2.get('type', 'sunny'), 1.0)
        )
        
        adjusted_speed = base_speed * weather_factor
        travel_time = (distance / adjusted_speed) * 60  # Convertir a minutos

        return max(travel_time, 0.5)

    def initialize_graph(self):
        for linea, info in METRO_LINES.items():
            stations = info["stations"]
            for i in range(len(stations) - 1):
                station1, station2 = stations[i], stations[i + 1]
                time = self.calculate_travel_time(station1, station2, linea)
                self.metro_graph.add_edge(
                    station1, station2,
                    line=linea,
                    color=info["color"],
                    weight=time
                )

    def add_to_history(self, route: Dict) -> Dict:
        """Agregar ruta al historial con ID único"""
        route_with_id = {
            **route,
            "id": len(self.route_history),
            "timestamp": datetime.now().isoformat()
        }
        self.route_history.insert(0, route_with_id)
        if len(self.route_history) > 10:
            self.route_history.pop()
        return route_with_id

    def find_route(self, origin: str, destination: str) -> Dict:
        self.update_weather()
        
        try:
            path = nx.shortest_path(self.metro_graph, origin, destination, weight='weight')
            
            total_time = 0
            total_distance = 0
            lines = []
            current_line = None
            transbordos = []
            weather_impacts = []
            
            for i in range(len(path) - 1):
                station1, station2 = path[i], path[i + 1]
                edge = self.metro_graph[station1][station2]
                
                coords1 = STATION_COORDINATES[station1]
                coords2 = STATION_COORDINATES[station2]
                segment_distance = self.calculate_distance(coords1[0], coords1[1], coords2[0], coords2[1])
                total_distance += segment_distance
                
                base_time = self.calculate_travel_time(station1, station2, edge['line'])
                
                weather1 = self.weather_conditions.get(station1, {'type': 'sunny', 'name': 'Soleado'})
                weather2 = self.weather_conditions.get(station2, {'type': 'sunny', 'name': 'Soleado'})
                
                if edge.get('line') != 'transbordo':
                    if current_line != edge['line']:
                        current_line = edge['line']
                        lines.append(current_line)
                    
                    if weather1.get('type') != 'sunny' or weather2.get('type') != 'sunny':
                        weather_impacts.append({
                            "segment": [station1, station2],
                            "line": edge['line'],
                            "conditions": {
                                "origin": {
                                    "station": station1,
                                    "weather": weather1.get('name', 'Soleado'),
                                    "impact": round((1 - self.WEATHER_SPEED_FACTORS.get(weather1.get('type', 'sunny'), 1.0)) * 100)
                                },
                                "destination": {
                                    "station": station2,
                                    "weather": weather2.get('name', 'Soleado'),
                                    "impact": round((1 - self.WEATHER_SPEED_FACTORS.get(weather2.get('type', 'sunny'), 1.0)) * 100)
                                }
                            }
                        })
                else:
                    transbordos.append(path[i])
                    base_time += 3

                total_time += base_time

            route = {
                "path": path,
                "coordinates": [STATION_COORDINATES[station] for station in path],
                "num_stations": len(path) - 1,
                "lines": lines,
                "estimated_time": round(total_time),
                "total_distance": round(total_distance, 2),
                "transbordos": transbordos,
                "weather_impacts": weather_impacts,
                "weather_conditions": self.weather_conditions
            }
            
            return self.add_to_history(route)
        except nx.NetworkXNoPath:
            return None

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

    def _update_edge_weights(self):
        """Actualiza los pesos de las aristas basándose en el clima actual"""
        for station1, station2, data in self.metro_graph.edges(data=True):
            time = self.calculate_travel_time(station1, station2, data['line'])
            self.metro_graph[station1][station2]['weight'] = time

metro_system = MetroSystem() 