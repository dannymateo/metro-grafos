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
except KeyError as ke:
    logger.error(f"Error de configuración en el sistema de metro: falta el campo '{ke}'", exc_info=True)
    raise
except Exception as e:
    logger.error(f"Error al inicializar el sistema de metro: {e}", exc_info=True)
    raise

# La referencia circular se establecerá en el archivo __init__.py del paquete services 