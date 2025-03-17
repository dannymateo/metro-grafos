from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Tuple, List
import random
from app.config import METRO_LINES, WEATHER_STATES, WEATHER_UPDATE_INTERVAL
import logging

logger = logging.getLogger(__name__)

@dataclass
class WeatherStation:
    station_id: str
    location: List[float]
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
        self.connected_clients = set()
        self.metro_system = None  # Se establecerá después para evitar dependencia circular

    def set_metro_system(self, metro_system):
        """Establece la referencia al sistema de metro para actualizar pesos"""
        self.metro_system = metro_system
        logger.info("Referencia al sistema de metro establecida en WeatherMonitoringSystem")

    def get_all_stations(self) -> Dict[str, List[float]]:
        """Obtiene todas las estaciones y sus coordenadas de METRO_LINES"""
        all_stations = {}
        for line_info in METRO_LINES.values():
            all_stations.update(line_info["stations"])
        return all_stations

    def initialize_stations(self):
        stations_coords = self.get_all_stations()
        for station_name, coords in stations_coords.items():
            station_id = f"MDE-{abs(hash(station_name)) % 1000:03d}"
            self.stations[station_name] = WeatherStation(
                station_id=station_id,
                location=coords
            )

    def update_weather(self) -> Dict[str, Dict]:
        current_time = datetime.now(timezone.utc)
        force_update = False
        
        # Si han pasado más de WEATHER_UPDATE_INTERVAL segundos, forzar actualización
        if (self._last_update and 
            (current_time - self._last_update).total_seconds() >= WEATHER_UPDATE_INTERVAL):
            force_update = True
            logger.info(f"Forzando actualización del clima después de {WEATHER_UPDATE_INTERVAL} segundos")
        
        if not force_update and self._cache:
            return self._cache

        updated_conditions = {}
        weather_changes = []  # Para rastrear cambios en el clima
        
        for station_name, station in self.stations.items():
            current = station.weather_data.get("type", "sunny")
            weather_state = WEATHER_STATES[current]
            
            # Determinar siguiente estado del clima con mayor variabilidad
            transitions = weather_state["transitions"]
            
            # Aumentar la probabilidad de cambio para pruebas
            if force_update:
                # Reducir la probabilidad de quedarse en el mismo estado
                adjusted_transitions = transitions.copy()
                if current in adjusted_transitions and adjusted_transitions[current] > 0.3:
                    adjusted_transitions[current] = 0.3
                    # Redistribuir el resto de probabilidad
                    remaining = 1.0 - adjusted_transitions[current]
                    other_states = [s for s in adjusted_transitions if s != current]
                    for state in other_states:
                        adjusted_transitions[state] = remaining / len(other_states)
                transitions = adjusted_transitions
            
            next_state = random.choices(
                list(transitions.keys()),
                weights=list(transitions.values())
            )[0]
            
            # Registrar cambio si ocurrió
            if next_state != current:
                weather_changes.append({
                    "station": station_name,
                    "from": current,
                    "to": next_state
                })
            
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

        # Registrar cambios en el clima
        if weather_changes:
            logger.info(f"Cambios en el clima detectados en {len(weather_changes)} estaciones:")
            for change in weather_changes:
                logger.info(f"  {change['station']}: {change['from']} → {change['to']}")

        self._cache = updated_conditions
        self._last_update = current_time
        
        # Actualizar los pesos del grafo basados en el nuevo clima
        if self.metro_system:
            self._update_graph_weights()
        else:
            logger.warning("No se pueden actualizar los pesos: metro_system no está establecido")
        
        return updated_conditions
    
    def _update_graph_weights(self):
        """Actualiza los pesos de las aristas en el grafo del metro basados en el clima actual"""
        if not self.metro_system:
            logger.warning("No se pueden actualizar los pesos del grafo: metro_system no está establecido")
            return
            
        logger.info("Actualizando pesos del grafo basados en condiciones climáticas actuales")
        
        # Contador para cambios significativos
        significant_changes = 0
        total_edges = 0
        
        # Guardar los pesos actuales para comparación
        old_weights = {}
        for station1, station2, data in self.metro_system.metro_graph.edges(data=True):
            old_weights[(station1, station2)] = data.get('weight', 0)
        
        # Actualizar el clima en el sistema de metro
        self.metro_system.weather_conditions = {
            station: {
                "type": data.get("type", "sunny"),
                "name": data.get("name", "Soleado"),
                "icon": data.get("icon", "☀️"),
                "intensity": data.get("intensity", 1.0)
            }
            for station, data in self._cache.items()
        }
        
        # Iterar sobre todas las aristas del grafo
        for station1, station2, data in self.metro_system.metro_graph.edges(data=True):
            total_edges += 1
            
            # Calcular el nuevo tiempo de viaje basado en el clima actual
            time = self.metro_system.calculate_travel_time(station1, station2, data['line'])
            
            # Verificar si hay un cambio significativo
            old_weight = old_weights.get((station1, station2), time)
            if abs(old_weight - time) > 0.2:  # Cambio de más de 12 segundos
                significant_changes += 1
                
                # Obtener información del clima para ambas estaciones
                weather1 = self._cache.get(station1, {}).get('type', 'sunny')
                weather2 = self._cache.get(station2, {}).get('type', 'sunny')
                
                logger.info(
                    f"Peso actualizado: {station1} → {station2} | "
                    f"Línea: {data['line']} | "
                    f"Tiempo: {old_weight:.1f}min → {time:.1f}min | "
                    f"Clima: {weather1}/{weather2}"
                )
            
            # Actualizar el peso de la arista
            self.metro_system.metro_graph[station1][station2]['weight'] = time
        
        if significant_changes > 0:
            logger.info(f"Pesos actualizados: {significant_changes} de {total_edges} aristas modificadas debido a cambios en el clima")
        else:
            logger.info("Pesos del grafo actualizados (sin cambios significativos)") 