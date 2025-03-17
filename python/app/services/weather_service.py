from typing import Dict
import asyncio
import logging
from datetime import datetime, timezone
from app.models.weather import WeatherStation
from app.config import WEATHER_UPDATE_INTERVAL, WEATHER_STATES, METRO_LINES
import random

logger = logging.getLogger(__name__)

class WeatherMonitoringSystem:
    def __init__(self):
        self.stations: Dict[str, WeatherStation] = {}
        self.initialize_stations()
        self._cache = {}
        self._last_update = None
        self.connected_clients = set()

    def get_all_stations(self) -> Dict[str, list]:
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

    async def broadcast_weather(self):
        """Envía actualizaciones del clima a todos los clientes conectados"""
        if self.connected_clients:
            message = {
                "type": "weather_update",
                "weather_conditions": self.update_weather(),
                "metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "stations_reporting": len(self.stations),
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
                await self.broadcast_weather()
                await asyncio.sleep(WEATHER_UPDATE_INTERVAL)
            except Exception as e:
                logger.error(f"Error en actualización periódica del clima: {e}")
                await asyncio.sleep(1)

weather_monitoring_system = WeatherMonitoringSystem() 