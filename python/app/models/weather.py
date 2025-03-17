from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Tuple
import random

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