from typing import Dict, List, Tuple

# Constantes y configuración
WEATHER_UPDATE_INTERVAL = 15  # segundos
MAX_HISTORY_SIZE = 10
DEFAULT_COORDINATES = (6.2442, -75.5812)

# Factores de velocidad según el clima
WEATHER_SPEED_FACTORS = {
    "sunny": 1.0,      # Velocidad normal
    "cloudy": 0.9,     # 10% más lento
    "rainy": 0.75,     # 25% más lento
    "stormy": 0.6      # 40% más lento
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
    ("Estación de metro Caribe", "Estación de bus Caribe"),  # A y 0
    ("Estación de metro Hospital", "Estación de bus Hospital"),  # A y 1
    ("Estación de metro Cisneros", "Estación de bus Cisneros"),  # B y 1
    ("Estación de metro Floresta", "Estación de bus Floresta"),  # B y 0
    ("Estación de metro Industriales", "Estación de bus Industriales 1"),  # A y 1
    ("Estación de metro Industriales", "Estación de bus Industriales 2"),  # A y 2

    # Conexiones entre Tranvia y Bus
    ("Estación de tranvia San José", "Estación de bus San José"),  # TA y 2

    # Conexiones entre Bus y Bus
    ("Estación de bus La Palma 1", "Estación de bus Villa de Aburrá"),  # 1 y 0
    ("Estación de bus La Palma 2", "Estación de bus Villa de Aburrá"),  # 2 y 0
    ("Estación de bus Villa de Aburrá", "Estación de bus La Palma 1"),  # 0 y 1
    ("Estación de bus Villa de Aburrá", "Estación de bus La Palma 2"),  # 0 y 2
    ("Estación de bus La Palma 1", "Estación de bus La Palma 2"),  # 1 y 2
    ("Estación de bus La Palma 2", "Estación de bus La Palma 1"),  # 2 y 1
    ("Estación Palo Verde 1", "Estación de bus Palos Verdes 2"),  # 1 y 2
    ("Estación Industriales 1", "Estación de bus Industriales 2"),  # 1 y 2
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
            "Estación de bus La Palma 1": [6.231143735603874, -75.60120211686286],
            "Estación de bus La Palma 2": [6.231109241102167, -75.60116348399163],
            "Estación de bus Villa de Aburrá": [6.235386926336392, -75.60220859986252],
            "Estación de bus Santa Gema": [6.2400331754631075, -75.60291337486278],
            "Estación de bus Laureles": [6.246021775520001, -75.6025198656445],
            "Estación de bus Los Pinos": [6.254718266943481, -75.59884999251533],
            "Estación de bus Floresta": [6.25885925792891, -75.59779347166828],
            "Estación de bus Calasanz": [6.264576473135161, -75.59643105209695],
            "Estación de bus Los colores": [6.270090354396566, -75.59532096904653],
            "Estación de bus Facultad de Minas": [6.2721793615114825, -75.59373651427525],
            "Estación de bus Ciudadela Universitaria": [6.273055615089159, -75.58756237741459],
            "Estación de bus Pilarica": [6.273655344318279, -75.58259836345937],
            "Estación de bus Córdoba": [6.273806369232593, -75.5783535625409],
            "Estación de bus Universal": [6.275341170092774, -75.57402642081355],
            "Estación de bus Caribe": [6.277514663177121, -75.57038484275131],
        }
    },
    "1" : {
        "color": "#33FF57",
        "stations": {
            "Estación de bus Parque Aranjuez 1": [6.285196916883157, -75.55682397680636],
            "Estación de bus Berlín 1": [6.283010316613288, -75.55308391430287],
            "Estación de bus Las Esmeraldas 1": [6.278617662748495, -75.55316511441866],
            "Estación de bus Manrique 1": [6.273092130323664, -75.55415542251787],
            "Estación de bus Gardel 1": [6.268046559131081, -75.55501893956009],
            "Estación de bus Palos Verdes 1": [6.262204408371649, -75.5559450174177],
            "Estación de bus Hospital": [6.264035542951745, -75.56373169070037],
            "Estación de bus U. de A": [6.264001888963568, -75.56761494224716],
            "Estación de bus Chagualo": [6.260855754072381, -75.56910622702229],
            "Estación de bus Minorista": [6.256120908271058, -75.57321998804991],
            "Estación de bus Cisneros ": [6.250744864627717, -75.5750870509758],
            "Estación de bus Plaza Mayor": [6.243643518963407, -75.57535344307288],
            "Estación de bus Industriales 1": [6.230689025094534, -75.57665925741367],
            "Estación de bus Nutibara 1": [6.231903797465869, -75.5820857522456],
            "Estación de bus Fátima 1": [6.2318125648764315, -75.58660831173623],
            "Estación de bus Rosales 1": [6.2316615162938405, -75.5909253327536],
            "Estación de bus Parque Belén 1": [6.23143840520439, -75.59675297650546],
            "Estación de bus La Palma 1": [6.231194854255559, -75.60093542030809],
            "Estación de bus Los Alpes 1": [6.231134955275897, -75.60509067899916],
            "Estación de bus U. de M. 1": [6.23108649282742, -75.60924200009467],
        }
    },
    "2" : {
        "color": "#F0E68C",
        "stations": {
            "Estación de bus Parque Aranjuez 2": [6.28521911058957, -75.55645078166778],
            "Estación de bus Berlín 2": [6.282974446014115, -75.55282679186952],
            "Estación de bus Las Esmeraldas 2": [6.2785891276210135, -75.5530391211881],
            "Estación de bus Manrique 2": [6.273088131100277, -75.55410043723315],
            "Estación de bus Gardel 2": [6.268031986281959, -75.55486444055407],
            "Estación de bus Palos Verdes 2": [6.262034016202694, -75.55575330332263],
            "Estación de bus Prado": [6.256986061526312, -75.5666672126181],
            "Estación de bus Catedral": [6.2528287368789925, -75.56261442500056],
            "Estación de bus La Playa": [6.249353624493189, -75.56459508648217],
            "Estación de bus San José": [6.247240088697676, -75.56605097115695],
            "Estación de bus Barrio Colón": [6.240530718884951, -75.56986261057031],
            "Estación de bus Perpetuo Socorro ": [6.23400512224475, -75.57010377807885],
            "Estación de bus Barrio Colombia": [6.22867315036066, -75.57095699731644],
            "Estación de bus Industriales 2": [6.230124611652166, -75.57667201622114],
            "Estación de bus Nutibara 2": [6.231733395432691, -75.58208349678578],
            "Estación de bus Fátima 2": [6.231587434226688, -75.58658917352503],
            "Estación de bus Rosales 2": [6.23150008271555, -75.59095465373126],
            "Estación de bus Parque Belén 2": [6.231313482345413, -75.5967798535402],
            "Estación de bus La Palma 2": [6.231109241102167, -75.60116348399163],
            "Estación de bus Los Alpes 2": [6.231023969584785, -75.6051267663563],
            "Estación de bus U. de M. 2": [6.230696406090166, -75.60934457804314],
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