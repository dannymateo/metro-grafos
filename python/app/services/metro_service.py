"""
Servicio que maneja las operaciones del sistema de metro.
"""

from app.models.metro import MetroSystem
import logging

logger = logging.getLogger(__name__)

# Crear una instancia única del sistema de metro
try:
    metro_system = MetroSystem()
    logger.info("Sistema de metro inicializado correctamente")
except Exception as e:
    logger.error(f"Error al inicializar el sistema de metro: {e}", exc_info=True)
    raise 