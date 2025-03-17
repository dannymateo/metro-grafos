from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Tuple, List
import random
from app.config import METRO_LINES, WEATHER_STATES

# Constantes
WEATHER_UPDATE_INTERVAL = 15  # segundos

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