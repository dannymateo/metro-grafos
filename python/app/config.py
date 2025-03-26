from typing import Dict, List, Tuple

# Constantes y configuración
WEATHER_UPDATE_INTERVAL = 15  # segundos
MAX_HISTORY_SIZE = 10
DEFAULT_COORDINATES = (6.2442, -75.5812)

# Factores de velocidad según el clima
WEATHER_SPEED_FACTORS = {
    "sunny": 1.0,      # Velocidad normal
    "cloudy": 0.7,     # 30% más lento
    "rainy": 0.5,      # 50% más lento
    "stormy": 0.3      # 70% más lento
}

# Velocidades promedio por tipo de transporte (km/h)
TRANSPORT_SPEEDS = {
    "metro": 35.0,    # Metro: 35 km/h promedio
    "cable": 18.0,    # Metrocable: 18 km/h promedio
    "tranvia": 20.0,   # Tranvía: 20 km/h promedio
    "bus": 40.0       # Bus: 40 km/h promedio
}

# Mapeo de líneas a tipos de transporte
LINE_TRANSPORT_TYPES = {
    "A": "metro", "B": "metro",
    "H": "cable", "J": "cable", "K": "cable",
    "L": "cable", "M": "cable", "P": "cable",
    "TA": "tranvia",
    "0": "bus", "1": "bus", "2": "bus"
}

# Tiempo de transbordo en minutos
TRANSFER_TIME = 3.0

# Conexiones de transbordo entre estaciones
TRANSFER_CONNECTIONS = [
    # Conexiones entre Metro y Metro
    ("Estación de metro San Antonio", "Estación de metro Cisneros"),  # Líneas A y B
    
    # Conexiones con el Metro y Tranvía
    ("Estación de metro San Antonio", "Estación de tranvia San José"),  # Líneas A/B y TA

    # Conexiones con el Tranvia y Metrocable
    ("Estación de tranvia Miraflores", "Estación de metro cable El Pinal"),  # TA y M
    ("Estación de tranvia Oriente", "Estación de metro cable Las Torres"),  # TA y H

    # Conexiones con el Metro y Metrocable
    ("Estación de metro Acevedo", "Estación de metro cable Andalucía"),  # A y K
    ("Estación de metro Acevedo", "Estación de metro cable Sena"),  # A y P 
    ("Estación de metro San Javier", "Estación de metro cable Juan XXIII"),  # B y J

    # Conexiones con el Metrocable y Metrocable
    ("Estación de metro cable Santo Domingo", "Estación de metro cable Arví"),  # K y L
    
    # Conexiones entre Metro y Bus
    ("Estación de metro Caribe", "Estación de bus Universal"),  # A y 0
    ("Estación de metro Hospital", "Estación de bus Palos Verdes 1"),  # A y 1
    ("Estación de metro Hospital", "Estación de bus Palos Verdes 2"),  # A y 2
    ("Estación de metro Hospital", "Estación de bus U. de A"),  # A y 1
    ("Estación de metro Cisneros", "Estación de bus Minorista"),  # B y 1
    ("Estación de metro Cisneros", "Estación de bus Plaza Mayor"),  # B y 1
    ("Estación de metro Floresta", "Estación de bus Calasanz"),  # B y 0
    ("Estación de metro Floresta", "Estación de bus Los Pinos"),  # B y 0
    ("Estación de metro Industriales", "Estación de bus Barrio Colombia"),  # A y 2
    ("Estación de metro Industriales", "Estación de bus Plaza Mayor"),  # A y 1
    ("Estación de metro Industriales", "Estación de bus Nutibara 1"),  # A y 1
    ("Estación de metro Industriales", "Estación de bus Nutibara 2"),  # A y 2

    # Conexiones entre Tranvia y Bus
    ("Estación de tranvia San José", "Estación de bus La Playa"),  # TA y 2
    ("Estación de tranvia San José", "Estación de bus Barrio Colón"),  # TA y 2

    # Conexiones entre Bus y Bus
    ("Estación de bus La Palma 1", "Estación de bus Villa de Aburrá"),  # 1 y 0
    ("Estación de bus La Palma 2", "Estación de bus Villa de Aburrá"),  # 2 y 0
    
]

# Configuración visual para transbordos
TRANSFER_VISUAL = {
    "line": "transbordo",
    "color": "gray"
}

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
            "Estación de metro Estadio": [6.2536, -75.5900],
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
            "Estación de metro cable Vallejuelos": [6.2754, -75.6142],
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
            "Estación de metro cable El Pinal": [6.2453, -75.5444],
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
    "0" : {
        "color": "#FF5733",
        "stations": {
            "Estación de bus La Palma": [6.2312, -75.6015],
            "Estación de bus Villa de Aburrá": [6.2442, -75.5812],
            "Estación de bus Santa Gema": [6.2397, -75.6029],
            "Estación de bus Laureles": [6.2458, -75.6025],
            "Estación de bus Los Pinos": [6.2549, -75.6098],
            "Estación de bus Floresta": [6.2586, -75.5977],
            "Estación de bus Calasanz": [6.2636, -75.5979],
            "Estación de bus Los colores": [6.2699, -75.5952],
            "Estación de bus Facultad de Minas": [6.2738, -75.5921],
            "Estación de bus Ciudadela Universitaria": [6.2730, -75.5885],
            "Estación de bus Pilarica": [6.2711, -75.5862],
            "Estación de bus Córdoba": [6.2744, -75.5784],
            "Estación de bus Universal": [6.2769, -75.5731],
            "Estación de bus Caribe": [6.2775, -75.5696],
        }
    },
    "1" : {
        "color": "#33FF57",
        "stations": {
            "Estación de bus Parque Aranjuez 1": [6.2848, -75.5570],
            "Estación de bus Berlín 1": [6.2823, -75.5576],
            "Estación de bus Las Esmeraldas 1": [6.2805, -75.5553],
            "Estación de bus Manrique 1": [6.2744, -75.5566],
            "Estación de bus Gardel 1": [6.2697, -75.5569],
            "Estación de bus Palos Verdes 1": [6.2624, -75.5572],
            "Estación de bus Hospital": [6.2635, -75.5650],
            "Estación de bus U. de A": [6.2654, -75.5706],
            "Estación de bus Chagualo": [6.2607, -75.5770],
            "Estación de bus Minorista": [6.2576, -75.5733],
            "Estación de bus Cisneros ": [6.2525, -75.5845],
            "Estación de bus Plaza Mayor": [6.2399, -75.5891],
            "Estación de bus Industriales 1": [6.2339, -75.5814],
            "Estación de bus Nutibara 1": [6.2356, -75.5869],
            "Estación de bus Fátima 1": [6.2347, -75.5883],
            "Estación de bus Rosales 1": [6.2333, -75.5949],
            "Estación de bus Parque Belén 1": [6.2319, -75.6019],
            "Estación de bus La Palma 1": [6.2310, -75.6010],
            "Estación de bus Los Alpes 1": [6.2329, -75.6163],
            "Estación de bus U. de M. 1": [6.2322, -75.6133],
        }
    },
    "2" : {
        "color": "#F0E68C",
        "stations": {
            "Estación de bus Parque Aranjuez 2": [6.2848, -75.5570],
            "Estación de bus Berlín 2": [6.2823, -75.5576],
            "Estación de bus Las Esmeraldas 2": [6.2805, -75.5553],
            "Estación de bus Manrique 2": [6.2744, -75.5566],
            "Estación de bus Gardel 2": [6.2697, -75.5569],
            "Estación de bus Palos Verdes 2": [6.2624, -75.5572],
            "Estación de bus Prado": [6.2442, -75.5812],
            "Estación de bus Catedral": [6.2442, -75.5812],
            "Estación de bus La Playa": [6.2442, -75.5812],
            "Estación de bus San José": [6.2442, -75.5812],
            "Estación de bus Barrio Colón": [6.2442, -75.5812],
            "Estación de bus Perpetuo Socorro ": [6.2442, -75.5812],
            "Estación de bus Barrio Colombia": [6.2442, -75.5812],
            "Estación de bus Industriales 2": [6.2339, -75.5814],
            "Estación de bus Nutibara 2": [6.2356, -75.5869],
            "Estación de bus Fátima 2": [6.2347, -75.5883],
            "Estación de bus Rosales 2": [6.2333, -75.5949],
            "Estación de bus Parque Belén 2": [6.2319, -75.6019],
            "Estación de bus La Palma 2": [6.2310, -75.6010],
            "Estación de bus Los Alpes 2": [6.2329, -75.6163],
            "Estación de bus U. de M. 2": [6.2322, -75.6133],
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
        "transitions": {
            "sunny": 0.4,
            "cloudy": 0.3,
            "rainy": 0.2,
            "stormy": 0.1
        },
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
        "transitions": {
            "sunny": 0.2,
            "cloudy": 0.3,
            "rainy": 0.3,
            "stormy": 0.2
        },
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
        "transitions": {
            "sunny": 0.1,
            "cloudy": 0.2,
            "rainy": 0.4,
            "stormy": 0.3
        },
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
        "transitions": {
            "sunny": 0.1,
            "cloudy": 0.2,
            "rainy": 0.3,
            "stormy": 0.4
        },
        "temp_range": (12, 20),
        "humidity_range": (80, 100),
        "visibility_range": (1, 4)
    }
} 