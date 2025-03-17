from typing import Dict

# Constantes y configuración
WEATHER_UPDATE_INTERVAL = 15  # segundos
MAX_HISTORY_SIZE = 10
DEFAULT_COORDINATES = (6.2442, -75.5812)

# Definir líneas del metro
METRO_LINES = {
    "A": {
        "color": "#007bff",
        "stations": ["Niquía", "Bello", "Madera", "Acevedo", "Tricentenario", "Caribe",
                    "Universidad", "Hospital", "Prado", "Parque Berrío", "San Antonio",
                    "Alpujarra", "Exposiciones", "Industriales", "Poblado", "Aguacatala",
                    "Ayurá", "Envigado", "Itagüí", "Sabaneta", "La Estrella"]
    },
    "B": {
        "color": "#fd7e14",
        "stations": ["San Antonio", "Cisneros", "Suramericana", "Estadio", 
                    "Floresta", "Santa Lucía", "San Javier"]
    },
    "H": {
        "color": "#e83e8c",
        "stations": ["Oriente", "Las Torres", "Villa Sierra"]
    },
    "J": {
        "color": "#ffc107",
        "stations": ["San Javier", "Juan XXIII", "Vallejuelos", "La Aurora"]
    },
    "K": {
        "color": "#28a745",
        "stations": ["Acevedo", "Andalucía", "Popular", "Santo Domingo"]
    },
    "L": {
        "color": "#8B4513",
        "stations": ["Santo Domingo", "Arví"]
    },
    "M": {
        "color": "#6f42c1",
        "stations": ["Miraflores", "Trece de Noviembre"]
    },
    "P": {
        "color": "#dc3545",
        "stations": ["Acevedo", "Sena", "Doce de Octubre", "El Progreso"]
    },
    "TA": {
        "color": "#28a745",
        "stations": ["San Antonio", "San José", "Pabellón del Agua EPM", "Bicentenario",
                    "Buenos Aires", "Miraflores", "Loyola", "Alejandro Echavarría", "Oriente"]
    }
}

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