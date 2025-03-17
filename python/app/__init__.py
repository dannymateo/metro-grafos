"""
Módulo principal de la aplicación del Metro de Medellín.
Contiene la configuración y servicios principales del sistema.
"""

from app.config import METRO_LINES, WEATHER_STATES
from app.services.metro_service import metro_system
from app.services.weather_service import weather_monitoring_system

__version__ = "1.0.0" 