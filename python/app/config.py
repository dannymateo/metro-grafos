from typing import Dict, List, Tuple

# Constantes y configuración
WEATHER_UPDATE_INTERVAL = 15  # segundos
MAX_HISTORY_SIZE = 10
DEFAULT_COORDINATES = (6.2442, -75.5812)

# Definir líneas del metro con sus coordenadas
METRO_LINES = {
    "A": {
        "color": "#007bff",
        "stations": {
            "Estación de metro Niquía": [6.3378, -75.5441],
            "Estación de metro Bello": [6.3299, -75.5536],
            "Estación de metro Madera": [6.3159, -75.5553],
            "Estación de metro Acevedo": [6.2998, -75.5586],
            "Estación de metro Tricentenario": [6.2903, -75.5647],
            "Estación de metro Caribe": [6.2775, -75.5696],
            "Estación de metro Universidad": [6.2694, -75.5658],
            "Estación de metro Hospital": [6.2639, -75.5631],
            "Estación de metro Prado": [6.2577, -75.5657],
            "Estación de metro Parque Berrío": [6.2504, -75.5682],
            "Estación de metro San Antonio": [6.2472, -75.5697],
            "Estación de metro Alpujarra": [6.2429, -75.5714],
            "Estación de metro Exposiciones": [6.2383, -75.5731],
            "Estación de metro Industriales": [6.2299, -75.5756],
            "Estación de metro Poblado": [6.2128, -75.5779],
            "Estación de metro Aguacatala": [6.1940, -75.5817],
            "Estación de metro Ayurá": [6.1865, -75.5854],
            "Estación de metro Envigado": [6.1747, -75.5970],
            "Estación de metro Itagüí": [6.1632, -75.6057],
            "Estación de metro Sabaneta": [6.1574, -75.6167],
            "Estación de metro La Estrella": [6.1527, -75.6264]
        }
    },
    "B": {
        "color": "#fd7e14",
        "stations": {
            "Estación de metro San Antonio": [6.2472, -75.5697],
            "Estación de metro Cisneros": [6.2490, -75.5748],
            "Estación de metro Suramericana": [6.2530, -75.5829],
            "Estación de metro Estadio": [6.2530, -75.5829],
            "Estación de metro Floresta": [6.2586, -75.5977],
            "Estación de metro Santa Lucía": [6.2581, -75.6037],
            "Estación de metro San Javier": [6.2566, -75.6134]
        }
    },
    "H": {
        "color": "#e83e8c",
        "stations": {
            "Estación de metro cable Oriente": [6.2332, -75.5402],
            "Estación de metro cable Las Torres": [6.2367, -75.5363],
            "Estación de metro cable Villa Sierra": [6.2352, -75.5334]
        }
    },
    "J": {
        "color": "#ffc107",
        "stations": {
            "Estación de metro cable San Javier": [6.2566, -75.6134],
            "Estación de metro cable Juan XXIII": [6.2657, -75.6137],
            "Estación de metro cable Vallejuelos": [6.2759, -75.6134],
            "Estación de metro cable La Aurora": [6.2810, -75.6143]
        }
    },
    "K": {
        "color": "#28a745",
        "stations": {
            "Estación de metro cable Acevedo": [6.2998, -75.5586],
            "Estación de metro cable Andalucía": [6.2961, -75.5519],
            "Estación de metro cable Popular": [6.2951, -75.5481],
            "Estación de metro cable Santo Domingo": [6.2928, -75.5418]
        }
    },
    "L": {
        "color": "#8B4513",
        "stations": {
            "Estación de metro cable Santo Domingo": [6.2928, -75.5418],
            "Estación de metro cable Arví": [6.2815, -75.5028]
        }
    },
    "M": {
        "color": "#6f42c1",
        "stations": {
            "Estación de metro cable Miraflores": [6.2414, -75.5490],
            "Estación de metro cable Trece de Noviembre": [6.2454, -75.5441]
        }
    },
    "P": {
        "color": "#dc3545",
        "stations": {
            "Estación de metro cable Acevedo": [6.2998, -75.5586],
            "Estación de metro cable Sena": [6.3018, -75.5674],
            "Estación de metro cable Doce de Octubre": [6.3041, -75.5760],
            "Estación de metro cable El Progreso": [6.3059, -75.5820]
        }
    },
    "TA": {
        "color": "#28a745",
        "stations": {
            "Estación de tranvia San Antonio": [6.2472, -75.5697],
            "Estación de tranvia San José": [6.2473, -75.5653],
            "Estación de tranvia Pabellón del Agua EPM": [6.2455, -75.5620],
            "Estación de tranvia Bicentenario": [6.2439, -75.5587],
            "Estación de tranvia Buenos Aires": [6.2414, -75.5539],
            "Estación de tranvia Miraflores": [6.2414, -75.5490],
            "Estación de tranvia Loyola": [6.2390, -75.5452],
            "Estación de tranvia Alejandro Echavarría": [6.2355, -75.5417],
            "Estación de tranvia Oriente": [6.2332, -75.5402]
        }
    },
        "C1": {
        "color": "#FF5733",
        "stations": {
            "Estación de bus Exposiciones": [6.2383, -75.5731],
            "Estación de bus San Diego": [6.2345, -75.5720],
            "Estación de bus Boston": [6.2401, -75.5645],
            "Estación de bus Los Ángeles": [6.2432, -75.5589],
            "Estación de bus El Salvador": [6.2440, -75.5532]
        }
    },
    "C2": {
        "color": "#33FF57",
        "stations": {
            "Estación de bus Industriales": [6.2299, -75.5756],
            "Estación de bus Barrio Colombia": [6.2264, -75.5740],
            "Estación de bus La Asomadera": [6.2305, -75.5678],
            "Estación de bus Las Palmas": [6.2312, -75.5623],
            "Estación de bus El Poblado": [6.2128, -75.5779]
        }
    },
    "C3": {
        "color": "#3357FF",
        "stations": {
            "Estación de bus Floresta": [6.2586, -75.5977],
            "Estación de bus Calasanz": [6.2603, -75.6031],
            "Estación de bus La América": [6.2617, -75.6089],
            "Estación de bus Santa Lucía": [6.2581, -75.6037],
            "Estación de bus San Javier": [6.2566, -75.6134]
        }
    },
    "C4": {
        "color": "#F0E68C",
        "stations": {
            "Estación de bus Aguacatala": [6.1940, -75.5817],
            "Estación de bus EAFIT": [6.1985, -75.5782],
            "Estación de bus Santa María de Los Ángeles": [6.2023, -75.5756],
            "Estación de bus La Frontera": [6.2048, -75.5709],
            "Estación de bus Envigado": [6.1747, -75.5970]
        }
    },
    "C5": {
        "color": "#FF1493",
        "stations": {
            "Estación de bus Niquía": [6.3378, -75.5441],
            "Estación de bus Barrio París": [6.3302, -75.5509],
            "Estación de bus Bello Centro": [6.3299, -75.5536],
            "Estación de bus Fabricato": [6.3250, -75.5560],
            "Estación de bus Madera": [6.3159, -75.5553]
        }
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