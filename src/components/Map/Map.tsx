'use client';

import { useEffect, useState, useRef, memo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { WeatherCondition } from '@/types';
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
        if (!isMapReady || !map || !weatherConditions) return;

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

const Map = ({ stations, coordinates, selectedRoute, lines, weatherConditions }: Props) => {
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

    const createIcon = (isSelected: boolean) => {
        const size = isSelected ? 24 : 16;
        const color = isSelected ? '#FF3B30' : '#FFFFFF';
        const borderColor = isSelected ? '#FFFFFF' : '#FFA000';
        const borderWidth = isSelected ? 3 : 2;
        const shadowOpacity = isSelected ? 0.8 : 0.5;

        return L.divIcon({
            className: 'custom-station-icon',
            html: `
                <div style="
                    width: ${size}px;
                    height: ${size}px;
                    background-color: ${color};
                    border: ${borderWidth}px solid ${borderColor};
                    border-radius: 50%;
                    box-shadow: 0 0 ${size/2}px rgba(0,0,0,${shadowOpacity}), 0 0 ${size/4}px rgba(255,255,255,0.5);
                    transition: all 0.3s ease;
                "></div>`,
            iconSize: [size, size],
            iconAnchor: [size/2, size/2],
        });
    };

    const getLineStyle = (status?: { congestion: 'normal' | 'alta' | 'muy_alta' }) => {
        const baseStyle = {
            weight: 6,
            opacity: 1,
            lineCap: 'round' as L.LineCapShape,
            lineJoin: 'round' as L.LineJoinShape
        };

        if (!status) return baseStyle;

        switch (status.congestion) {
            case 'muy_alta':
                return {
                    ...baseStyle,
                    weight: 8,
                    opacity: 0.9,
                    dashArray: '10, 10'
                };
            case 'alta':
                return {
                    ...baseStyle,
                    weight: 7,
                    opacity: 0.9,
                    dashArray: '5, 5'
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
            <>
                {/* Capa de sombra para la ruta */}
                <Polyline
                    positions={selectedRoute.coordinates}
                    pathOptions={{
                        color: '#000000',
                        weight: 8,
                        opacity: 0.4,
                        lineCap: 'round',
                        lineJoin: 'round',
                        dashArray: selectedRoute.status?.congestion === 'muy_alta' ? '10,10' : undefined
                    }}
                />
                {/* Ruta principal */}
                <Polyline
                    positions={selectedRoute.coordinates}
                    pathOptions={{
                        color: '#FF3B30',
                        weight: 4,
                        opacity: 1,
                        lineCap: 'round',
                        lineJoin: 'round',
                        dashArray: selectedRoute.status?.congestion === 'muy_alta' ? '10,10' : undefined
                    }}
                />
                {/* Borde brillante */}
                <Polyline
                    positions={selectedRoute.coordinates}
                    pathOptions={{
                        color: '#FFFFFF',
                        weight: 1,
                        opacity: 0.8,
                        lineCap: 'round',
                        lineJoin: 'round',
                        dashArray: selectedRoute.status?.congestion === 'muy_alta' ? '10,10' : undefined
                    }}
                />
            </>
        );
    };

    if (!isClient) {
        return <div className="h-[600px] w-full relative rounded-xl overflow-hidden shadow-xl bg-gray-100" />;
    }

    return (
        <div className="h-[600px] w-full relative rounded-xl overflow-hidden shadow-xl">
            <MapContainer 
                center={defaultCenter}
                zoom={13} 
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={true}
                className="z-0"
            >
                <TileLayer
                    url="https://api.mapbox.com/styles/v1/dannymateoh1/clvbhsqsh011d01peahrq3t8b/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiZGFubnltYXRlb2gxIiwiYSI6ImNsdmJocHlmYjA5M3oycXFtM2llaWJsY2sifQ.a8cfb91OkmPekSpKNc90iw"
                    attribution='&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a>'
                    maxZoom={20}
                />
                {renderMetroLines()}
                {renderSelectedRoute()}
                {stations.map((station) => {
                    const coords = coordinates[station];
                    if (coords) {
                        const isSelected = selectedRoute?.path.includes(station);
                        
                        return (
                            <Marker 
                                key={station} 
                                position={coords}
                                icon={createIcon(!!isSelected)}
                            >
                                <Popup className="station-popup">
                                    <div className="font-semibold text-gray-900">{station}</div>
                                </Popup>
                            </Marker>
                        );
                    }
                    return null;
                })}
                {weatherConditions && (
                    <WeatherOverlay weatherConditions={weatherConditions} />
                )}
            </MapContainer>
        </div>
    );
}

export default Map; 