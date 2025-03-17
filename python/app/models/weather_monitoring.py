from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Tuple
import random
from data.coordinates import STATION_COORDINATES

# Constantes
WEATHER_UPDATE_INTERVAL = 15  # segundos

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