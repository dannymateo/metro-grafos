import matplotlib.pyplot as plt
from io import BytesIO
import networkx as nx
from app.config import (
    METRO_LINES, 
    WEATHER_STATES, 
    TRANSFER_VISUAL
)

def get_station_coordinates(station_name: str) -> list:
    """Obtiene las coordenadas de una estación desde METRO_LINES"""
    for line_info in METRO_LINES.values():
        if station_name in line_info["stations"]:
            return line_info["stations"][station_name]
    return None

def generate_graph_visualization(metro_system):
    """
    Genera una visualización del sistema de metro con las rutas actuales
    y el estado del clima.
    """
    plt.figure(figsize=(15, 10))
    
    # Crear un grafo nuevo para la visualización
    G = metro_system.metro_graph.copy()
    
    # Crear un diccionario de posiciones único para cada estación
    pos = {}
    for line_info in METRO_LINES.values():
        for station, coords in line_info["stations"].items():
            if station not in pos:  # Solo agregar si no existe
                pos[station] = [coords[1], coords[0]]
    
    # Dibujar las líneas del metro con diferentes colores
    for line_name, line_info in METRO_LINES.items():
        stations = list(line_info["stations"].keys())
        edge_list = [
            (station1, station2)
            for station1, station2 in zip(stations, stations[1:])
            if G.has_edge(station1, station2)
        ]
        nx.draw_networkx_edges(G, pos, edgelist=edge_list, 
                             edge_color=line_info["color"],
                             width=2)

    # Si hay una ruta actual en el historial, dibujarla en rojo
    if metro_system.route_history:
        current_route = metro_system.route_history[0]  # Última ruta calculada
        path = current_route["path"]
        
        # Crear lista de pares de estaciones consecutivas en la ruta
        route_edges = list(zip(path[:-1], path[1:]))
        
        # Dibujar la ruta en rojo y más gruesa
        nx.draw_networkx_edges(G, pos,
                             edgelist=route_edges,
                             edge_color='red',
                             width=4,
                             alpha=0.7)
        
        # Resaltar nodos de origen y destino
        nx.draw_networkx_nodes(G, pos,
                             nodelist=[path[0]],  # Origen
                             node_color='green',
                             node_size=300,
                             node_shape='o')
        nx.draw_networkx_nodes(G, pos,
                             nodelist=[path[-1]],  # Destino
                             node_color='red',
                             node_size=300,
                             node_shape='o')

    # Dibujar los nodos (estaciones)
    nx.draw_networkx_nodes(G, pos, 
                          node_color='white',
                          node_size=200,
                          edgecolors='black',
                          linewidths=1)
    
    # Añadir etiquetas de las estaciones
    labels = {node: node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, 
                          font_size=8,
                          font_weight='bold')
    
    # Añadir título y leyenda
    plt.title("Sistema Metro de Medellín", pad=20, fontsize=16)
    
    # Crear leyenda para las líneas
    legend_elements = [
        plt.Line2D([0], [0], color=info["color"], label=f'Línea {line}')
        for line, info in METRO_LINES.items()
    ]
    if metro_system.route_history:
        legend_elements.append(
            plt.Line2D([0], [0], color='red', linewidth=4, label='Ruta actual')
        )
    plt.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
    
    # Añadir indicadores de clima
    for station, weather in metro_system.weather_conditions.items():
        if station in pos:
            x, y = pos[station]
            weather_type = weather.get('type', 'sunny')
            weather_state = WEATHER_STATES.get(weather_type, WEATHER_STATES['sunny'])
            plt.plot(x, y, 
                    marker='o',
                    markersize=15,
                    color=weather_state['color'],
                    alpha=weather_state['opacity'],
                    zorder=2)
            plt.text(x, y+0.01, 
                    weather_state['icon'],
                    horizontalalignment='center',
                    fontsize=10)
    
    # Ajustar los márgenes y layout
    plt.margins(0.15)
    plt.tight_layout()
    
    # Guardar el gráfico en un buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf 