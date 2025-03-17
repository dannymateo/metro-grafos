"""
Módulo de servicios del Metro de Medellín.
Contiene la lógica de negocio y servicios del sistema.
"""

from app.services.weather_service import weather_monitoring_system
from app.services.metro_service import metro_system

# Establecer la referencia circular después de importar ambos servicios
weather_monitoring_system.set_metro_system(metro_system)

__all__ = ['weather_monitoring_system', 'metro_system'] 