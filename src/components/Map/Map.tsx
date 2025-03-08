'use client';

import { useEffect, useState, useRef, memo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { WeatherCondition, WeatherReading } from '@/components/RouteWebSocket';
import { Props } from './types';

const WeatherOverlay = memo(({ weatherConditions }: { weatherConditions: Record<string, WeatherCondition> }) => {
    const map = useMap();
    const markersRef = useRef<Record<string, L.Marker>>({});
    const [isMapReady, setIsMapReady] = useState(false);

    useEffect(() => {
        if (!map) return;

        const checkMap = () => {
            if (map && map.getZoom() !== undefined) {
                setIsMapReady(true);
            }
        };

        map.whenReady(checkMap);
        return () => {
            map.off('ready', checkMap);
        };
    }, [map]);

    useEffect(() => {
        if (!isMapReady || !map) return;

        // Limpiar marcadores existentes
        Object.values(markersRef.current).forEach(marker => marker.remove());
        markersRef.current = {};

        // Añadir nuevos marcadores
        Object.entries(weatherConditions).forEach(([station, condition]) => {
            const coords = condition.location;
            if (!coords) return;

            if (!markersRef.current[station]) {
                const marker = createWeatherMarker(station, condition);
                markersRef.current[station] = marker;
                marker.addTo(map);
            } else {
                updateWeatherMarker(markersRef.current[station], condition);
            }
        });

        return () => {
            Object.values(markersRef.current).forEach(marker => marker.remove());
        };
    }, [map, isMapReady, weatherConditions]);

    const createWeatherMarker = (station: string, condition: WeatherCondition) => {
        const marker = L.marker(condition.location, {
            icon: createWeatherIcon(condition),
            zIndexOffset: 1000
        });

        marker.bindPopup(createPopupContent(station, condition));
        return marker;
    };

    const createWeatherIcon = (condition: WeatherCondition) => {
        return L.divIcon({
            className: `weather-icon weather-${condition.type}`,
            html: `
                <div class="weather-container">
                    <div class="weather-symbol">${condition.icon}</div>
                </div>
            `,
            iconSize: [16, 16],
            iconAnchor: [8, -8]
        });
    };

    const createPopupContent = (station: string, condition: WeatherCondition) => {
        const lastUpdate = new Date(condition.last_updated).toLocaleTimeString();
        return `
            <div class="weather-popup">
                <div class="text-sm">${condition.name} (${station})</div>
                <div class="text-xs">🌡️ ${condition.readings.temperature}°C</div>
            </div>
        `;
    };

    const updateWeatherMarker = (marker: L.Marker, condition: WeatherCondition) => {
        marker.setIcon(createWeatherIcon(condition));
        marker.setPopupContent(createPopupContent(marker.getPopup()?.getContent() as string, condition));
    };

    return null;
});

WeatherOverlay.displayName = 'WeatherOverlay';

export default function Map({ stations, coordinates, selectedRoute, lines, userLocation, nearestStation, weatherConditions }: Props) {
    const [isClient, setIsClient] = useState(false);
    const defaultCenter = [6.2442, -75.5812] as L.LatLngExpression;

    useEffect(() => {
        setIsClient(true);
    }, []);

    useEffect(() => {
        const L = require('leaflet');
        delete L.Icon.Default.prototype._getIconUrl;
        L.Icon.Default.mergeOptions({
            iconUrl: require('leaflet/dist/images/marker-icon.png'),
            iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
            shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
        });
    }, []);

    useEffect(() => {
        console.log('Weather conditions updated:', weatherConditions);
    }, [weatherConditions]);

    const createIcon = (isSelected: boolean, isOrigin?: boolean, isDestination?: boolean) => {
        const size = isOrigin || isDestination ? 28 : isSelected ? 16 : 12;
        const color = isOrigin ? '#22c55e' : 
                     isDestination ? '#ef4444' : 
                     isSelected ? '#6366f1' : '#1a73e8';

        return L.divIcon({
            className: 'custom-station-icon',
            html: `
                <div style="
                    width: ${size}px;
                    height: ${size}px;
                    background-color: ${color};
                    border: ${isOrigin || isDestination ? 4 : 2}px solid white;
                    border-radius: 50%;
                    box-shadow: 0 0 ${isOrigin || isDestination ? 8 : 4}px rgba(0,0,0,0.3);
                    transition: all 0.3s ease;
                "></div>`,
            iconSize: [size, size],
            iconAnchor: [size/2, size/2],
        });
    };

    const getLineStyle = (status?: { congestion: 'normal' | 'alta' | 'muy_alta' }) => {
        const baseStyle = {
            weight: 4,
            opacity: 0.8
        };

        if (!status) return baseStyle;

        switch (status.congestion) {
            case 'muy_alta':
                return {
                    ...baseStyle,
                    weight: 6,
                    opacity: 1,
                    dashArray: '4, 8'
                };
            case 'alta':
                return {
                    ...baseStyle,
                    weight: 5,
                    opacity: 0.9,
                    dashArray: '1, 5'
                };
            default:
                return baseStyle;
        }
    };

    const renderMetroLines = () => {
        if (!lines) return null;
        
        return Object.entries(lines).map(([lineName, lineInfo]) => {
            const lineCoordinates = lineInfo.stations
                .map(station => coordinates[station])
                .filter(coord => coord !== undefined);

            return (
                <Polyline
                    key={lineName}
                    positions={lineCoordinates}
                    pathOptions={{
                        color: lineInfo.color,
                        ...getLineStyle(lineInfo.status)
                    }}
                />
            );
        });
    };

    const renderSelectedRoute = () => {
        if (!selectedRoute) return null;

        return (
            <Polyline
                positions={selectedRoute.coordinates}
                pathOptions={{
                    color: '#dc2626',
                    weight: 5,
                    opacity: 0.8,
                    lineCap: 'round',
                    lineJoin: 'round',
                    dashArray: selectedRoute.status?.congestion === 'muy_alta' ? '10,10' : undefined
                }}
            />
        );
    };

    const renderUserLocation = () => {
        if (!userLocation) return null;

        return (
            <Marker
                position={userLocation}
                icon={L.divIcon({
                    className: 'user-location-icon',
                    html: `
                        <div class="relative">
                            <div class="absolute inset-0 bg-blue-500/30 animate-ping rounded-full"
                                style="width: 32px; height: 32px;">
                            </div>
                            <div class="relative bg-blue-500 border-2 border-white rounded-full shadow-lg"
                                style="width: 16px; height: 16px;">
                            </div>
                        </div>
                    `,
                    iconSize: [32, 32],
                    iconAnchor: [16, 16]
                })}
            >
                <Popup>
                    <div className="font-semibold">Tu ubicación actual</div>
                    {nearestStation && (
                        <div className="text-sm text-gray-600">
                            Estación más cercana: {nearestStation}
                        </div>
                    )}
                </Popup>
            </Marker>
        );
    };

    if (!isClient) {
        return <div className="h-[600px] w-full relative rounded-xl overflow-hidden shadow-xl bg-gray-100" />;
    }

    return (
        <div className="h-[600px] w-full relative rounded-xl overflow-hidden shadow-xl">
            <style jsx global>{`
                @keyframes pulse {
                    0% {
                        transform: translate(-50%, -50%) scale(0.95);
                        opacity: 0.6;
                    }
                    50% {
                        transform: translate(-50%, -50%) scale(1.05);
                        opacity: 0.8;
                    }
                    100% {
                        transform: translate(-50%, -50%) scale(0.95);
                        opacity: 0.6;
                    }
                }
                .weather-effect {
                    pointer-events: none;
                }
                .weather-circle {
                    transition: all 0.5s ease;
                }
                
                .weather-sunny {
                    animation: pulse-sunny 4s infinite;
                }
                
                .weather-cloudy {
                    animation: pulse-cloudy 6s infinite;
                }
                
                .weather-rainy {
                    animation: pulse-rainy 3s infinite;
                }
                
                .weather-stormy {
                    animation: pulse-stormy 2s infinite;
                }
                
                @keyframes pulse-sunny {
                    0% { opacity: 0.7; }
                    50% { opacity: 1; }
                    100% { opacity: 0.7; }
                }
                
                @keyframes pulse-cloudy {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
                
                @keyframes pulse-rainy {
                    0% { opacity: 0.6; }
                    50% { opacity: 0.9; }
                    100% { opacity: 0.6; }
                }
                
                @keyframes pulse-stormy {
                    0% { opacity: 0.7; transform: scale(1); }
                    50% { opacity: 1; transform: scale(1.1); }
                    100% { opacity: 0.7; transform: scale(1); }
                }
                
                .weather-container {
                    position: relative;
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background-color: rgba(255, 255, 255, 0.9);
                    border-radius: 50%;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                }

                .weather-symbol {
                    position: relative;
                    font-size: 12px;
                    line-height: 1;
                    filter: drop-shadow(0 1px 1px rgba(0,0,0,0.1));
                }

                .weather-icon:hover .weather-symbol {
                    transform: scale(1.2);
                }

                .weather-popup {
                    text-align: center;
                    padding: 2px 4px;
                    font-size: 11px;
                }
            `}</style>
            <MapContainer 
                center={defaultCenter}
                zoom={12} 
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={true}
                className="z-0"
            >
                <TileLayer
                    url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                {renderMetroLines()}
                {renderSelectedRoute()}
                {weatherConditions && (
                    <WeatherOverlay weatherConditions={weatherConditions} />
                )}
                {stations.map((station) => {
                    const coords = coordinates[station];
                    if (coords) {
                        const isSelected = selectedRoute?.path.includes(station);
                        const isOrigin = selectedRoute?.path[0] === station;
                        const isDestination = selectedRoute?.path[selectedRoute.path.length - 1] === station;
                        
                        return (
                            <Marker 
                                key={station} 
                                position={coords}
                                icon={createIcon(!!isSelected, isOrigin, isDestination)}
                            >
                                <Popup className="station-popup">
                                    <div className="font-semibold text-gray-900">{station}</div>
                                </Popup>
                            </Marker>
                        );
                    }
                    return null;
                })}
                {renderUserLocation()}
            </MapContainer>
        </div>
    );
} 