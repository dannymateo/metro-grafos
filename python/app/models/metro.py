import networkx as nx
from typing import Dict, List, Tuple
from datetime import datetime, timezone
import random
from math import radians, sin, cos, sqrt, atan2
from app.config import (
    METRO_LINES, 
    WEATHER_SPEED_FACTORS, 
    TRANSPORT_SPEEDS, 
    LINE_TRANSPORT_TYPES,
    TRANSFER_CONNECTIONS,
    TRANSFER_TIME,
    TRANSFER_VISUAL
)
from app.models.weather_monitoring import WeatherMonitoringSystem
import logging

logger = logging.getLogger(__name__)

class MetroSystem:
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

    def get_station_coordinates(self, station: str, line: str = None) -> List[float]:
        """Obtiene las coordenadas de una estación"""
        if line and line in METRO_LINES:
            if station in METRO_LINES[line]["stations"]:
                return METRO_LINES[line]["stations"][station]
        
        # Si no se especifica línea o no se encuentra en la línea especificada,
        # buscar en todas las líneas
        for line_info in METRO_LINES.values():
            if station in line_info["stations"]:
                return line_info["stations"][station]
        return None

    def calculate_travel_time(self, station1: str, station2: str, line: str) -> float:
        coords1 = self.get_station_coordinates(station1)
        coords2 = self.get_station_coordinates(station2)
        
        if not coords1 or not coords2:
            return 1.0
            
        distance = self.calculate_distance(coords1[0], coords1[1], coords2[0], coords2[1])
        
        # Obtener el tipo de transporte y su velocidad base desde la configuración
        transport_type = LINE_TRANSPORT_TYPES.get(line, "metro")
        base_speed = TRANSPORT_SPEEDS.get(transport_type, 35.0)

        # Obtener condiciones climáticas de ambas estaciones
        weather1 = self.weather_conditions.get(station1, {'type': 'sunny'})
        weather2 = self.weather_conditions.get(station2, {'type': 'sunny'})
        
        # Usar el clima más severo entre las dos estaciones
        weather1_type = weather1.get('type', 'sunny')
        weather2_type = weather2.get('type', 'sunny')
        
        # Añadir un poco de variabilidad a los factores del clima
        weather_factor1 = WEATHER_SPEED_FACTORS.get(weather1_type, 1.0) * random.uniform(0.95, 1.05)
        weather_factor2 = WEATHER_SPEED_FACTORS.get(weather2_type, 1.0) * random.uniform(0.95, 1.05)
        
        # Usar el factor más bajo (peor clima)
        weather_factor = min(weather_factor1, weather_factor2)
        
        # Añadir un poco de variabilidad al tiempo de viaje
        adjusted_speed = base_speed * weather_factor
        travel_time = (distance / adjusted_speed) * 60  # Convertir a minutos
        
        # Añadir un pequeño factor aleatorio para simular variabilidad en condiciones de tráfico
        travel_time *= random.uniform(0.95, 1.05)

        return max(travel_time, 0.5)

    def initialize_graph(self):
        """Inicializa el grafo del metro con la nueva estructura de datos"""
        logger.info("Iniciando inicialización del grafo")
        
        # Limpiar el grafo existente
        self.metro_graph.clear()
        
        # Primero añadir todas las estaciones como nodos
        for line_id, line_info in METRO_LINES.items():
            logger.info(f"Añadiendo estaciones de la línea {line_id}")
            for station in line_info["stations"].keys():
                if station not in self.metro_graph:
                    self.metro_graph.add_node(station)
                    logger.debug(f"Añadido nodo: {station}")
        
        # Luego crear las conexiones dentro de cada línea
        for line_id, line_info in METRO_LINES.items():
            stations = list(line_info["stations"].keys())
            logger.info(f"Creando conexiones para línea {line_id} ({len(stations)} estaciones)")
            
            for i in range(len(stations) - 1):
                station1, station2 = stations[i], stations[i + 1]
                coords1 = self.get_station_coordinates(station1, line_id) # deberia ser get_station_coordinates(station1, line_id)?
                coords2 = self.get_station_coordinates(station2, line_id) # deberia ser get_station_coordinates(station2, line_id)?
                
                if coords1 and coords2:
                    time = self.calculate_travel_time(station1, station2, line_id)
                    self.metro_graph.add_edge(
                        station1,
                        station2,
                        line=line_id,
                        color=line_info["color"],
                        weight=time
                    )
                    logger.debug(f"Añadida conexión: {station1} -> {station2} (línea {line_id})")
                else:
                    logger.warning(f"No se pudo crear conexión entre {station1} y {station2}: coordenadas faltantes")
        
        # Añadir conexiones entre líneas (transbordos)
        self._add_transfer_stations()
        
        # Verificar la conectividad del grafo
        if not nx.is_connected(self.metro_graph):
            components = list(nx.connected_components(self.metro_graph))
            logger.warning(f"El grafo no está completamente conectado. Hay {len(components)} componentes separados")
            for i, component in enumerate(components):
                logger.warning(f"Componente {i+1}: {component}")
        else:
            logger.info("El grafo está completamente conectado")
        
        logger.info(f"Grafo inicializado con {len(self.metro_graph.nodes())} estaciones y {len(self.metro_graph.edges())} conexiones")

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
        """Encuentra la mejor ruta entre dos estaciones"""
        try:
            logger.info(f"Buscando ruta desde {origin} hasta {destination}")
            
            # Verificar que las estaciones existan
            if origin not in self.metro_graph.nodes():
                logger.error(f"Estación de origen '{origin}' no encontrada")
                return None
            if destination not in self.metro_graph.nodes():
                logger.error(f"Estación de destino '{destination}' no encontrada")
                return None
            
            # Verificar que el grafo tenga nodos y aristas
            if len(self.metro_graph.nodes()) == 0:
                logger.error("El grafo del metro está vacío")
                return None
                
            logger.info(f"Nodos en el grafo: {len(self.metro_graph.nodes())}")
            logger.info(f"Aristas en el grafo: {len(self.metro_graph.edges())}")
            
            path = nx.shortest_path(self.metro_graph, origin, destination, weight='weight')
            logger.info(f"Ruta encontrada: {path}")
            
            total_time = 0
            total_distance = 0
            lines = []
            current_line = None
            transbordos = []
            weather_impacts = []
            
            for i in range(len(path) - 1):
                station1, station2 = path[i], path[i + 1]
                edge = self.metro_graph[station1][station2]
                
                # Obtener coordenadas y calcular distancia
                coords1 = self.get_station_coordinates(station1)
                coords2 = self.get_station_coordinates(station2)
                
                if coords1 and coords2:  # Verificar que existan las coordenadas
                    segment_distance = self.calculate_distance(coords1[0], coords1[1], coords2[0], coords2[1])
                    total_distance += segment_distance
                
                # Calcular tiempo de viaje
                time = self.calculate_travel_time(station1, station2, edge['line'])
                total_time += time
                
                # Registrar línea y transbordos
                if edge['line'] != current_line:
                    if current_line is not None:  # Si hay cambio de línea
                        transbordos.append(station1)
                        total_time += 3  # Añadir tiempo de transbordo
                    current_line = edge['line']
                    if current_line not in lines:
                        lines.append(current_line)
                
                # Registrar impactos del clima
                weather1 = self.weather_conditions.get(station1, {'type': 'sunny', 'name': 'Soleado'})
                weather2 = self.weather_conditions.get(station2, {'type': 'sunny', 'name': 'Soleado'})
                
                if weather1['type'] != 'sunny' or weather2['type'] != 'sunny':
                    weather_impacts.append({
                        "segment": [station1, station2],
                        "line": edge['line'],
                        "conditions": {
                            "origin": {
                                "station": station1,
                                "weather": weather1['name'],
                                "impact": round((1 - WEATHER_SPEED_FACTORS[weather1['type']]) * 100)
                            },
                            "destination": {
                                "station": station2,
                                "weather": weather2['name'],
                                "impact": round((1 - WEATHER_SPEED_FACTORS[weather2['type']]) * 100)
                            }
                        }
                    })

            route = {
                "path": path,
                "coordinates": [self.get_station_coordinates(station) for station in path],
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
            logger.error(f"No existe ruta entre {origin} y {destination}")
            return None
        except Exception as e:
            logger.error(f"Error al calcular ruta: {e}", exc_info=True)
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

    def _add_transfer_stations(self):
        """Añade conexiones entre estaciones de diferentes líneas (transbordos)"""
        logger.info("Añadiendo conexiones de transbordo entre líneas")
        
        # Añadir conexiones de transbordo desde la configuración
        for station1, station2 in TRANSFER_CONNECTIONS:
            if station1 in self.metro_graph and station2 in self.metro_graph:
                self.metro_graph.add_edge(
                    station1,
                    station2,
                    line=TRANSFER_VISUAL["line"],
                    color=TRANSFER_VISUAL["color"],
                    weight=TRANSFER_TIME
                )
                logger.info(f"Añadida conexión de transbordo entre {station1} y {station2}")
        
        logger.info(f"Completada la adición de conexiones de transbordo. Total de aristas: {len(self.metro_graph.edges())}")

    def get_weather_impact_on_route(self, origin: str, destination: str) -> dict:
        """
        Calcula el impacto del clima en una ruta específica.
        Compara el tiempo de viaje con clima actual vs. clima soleado.
        """
        try:
            # Guardar el clima actual
            current_weather = self.weather_conditions.copy()
            
            # Calcular ruta con clima actual
            route_with_weather = self.find_route(origin, destination)
            if not route_with_weather:
                return {"error": "No se pudo encontrar una ruta"}
            
            time_with_weather = route_with_weather["estimated_time"]
            
            # Simular clima soleado para todas las estaciones
            sunny_weather = {}
            for station in self.weather_conditions:
                sunny_weather[station] = {
                    "type": "sunny",
                    "name": "Soleado",
                    "icon": "☀️",
                    "intensity": 1.0
                }
            
            # Aplicar clima soleado temporalmente
            self.weather_conditions = sunny_weather
            
            # Recalcular pesos con clima soleado
            for station1, station2, data in self.metro_graph.edges(data=True):
                time = self.calculate_travel_time(station1, station2, data['line'])
                self.metro_graph[station1][station2]['weight'] = time
            
            # Calcular ruta con clima soleado
            route_sunny = self.find_route(origin, destination)
            time_sunny = route_sunny["estimated_time"] if route_sunny else 0
            
            # Restaurar clima original
            self.weather_conditions = current_weather
            
            # Restaurar pesos originales
            for station1, station2, data in self.metro_graph.edges(data=True):
                time = self.calculate_travel_time(station1, station2, data['line'])
                self.metro_graph[station1][station2]['weight'] = time
            
            # Calcular impacto
            if time_sunny > 0:
                delay = time_with_weather - time_sunny
                delay_percent = (delay / time_sunny) * 100
                
                return {
                    "route": route_with_weather["path"],
                    "time_with_weather": time_with_weather,
                    "time_sunny": time_sunny,
                    "delay_minutes": round(delay, 1),
                    "delay_percent": round(delay_percent, 1),
                    "weather_conditions": [
                        {
                            "station": station,
                            "weather": self.weather_conditions.get(station, {}).get("name", "Desconocido"),
                            "type": self.weather_conditions.get(station, {}).get("type", "sunny")
                        }
                        for station in route_with_weather["path"]
                    ]
                }
            
            return {"error": "Error al calcular el impacto del clima"}
        
        except Exception as e:
            logger.error(f"Error al calcular impacto del clima: {e}", exc_info=True)
            return {"error": str(e)}

metro_system = MetroSystem() 