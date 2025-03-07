'use client';

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

type MapProps = {
    stations: string[];
    coordinates: Record<string, [number, number]>;
    selectedRoute?: {
        path: string[];
        coordinates: [number, number][];
        status?: {
            congestion: 'normal' | 'alta' | 'muy_alta';
            alerts?: string[];
        };
    };
    lines?: Record<string, {
        color: string;
        stations: string[];
        status?: {
            congestion: 'normal' | 'alta' | 'muy_alta';
            alerts?: string[];
        };
    }>;
    userLocation?: [number, number];
    nearestStation?: string;
}

export default function Map({ stations, coordinates, selectedRoute, lines, userLocation, nearestStation }: MapProps) {
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

    const createIcon = (isSelected: boolean, isOrigin?: boolean, isDestination?: boolean) => {
        const L = require('leaflet');
        let color = '#1a73e8';
        let size = 12;
        let borderWidth = 2;
        let shadowSize = 4;

        if (isOrigin) {
            color = '#22c55e';
            size = 28;
            borderWidth = 4;
            shadowSize = 8;
        } else if (isDestination) {
            color = '#ef4444';
            size = 28;
            borderWidth = 4;
            shadowSize = 8;
        } else if (isSelected) {
            color = '#6366f1';
            size = 16;
            borderWidth = 3;
            shadowSize = 6;
        }

        return L.divIcon({
            className: 'custom-station-icon',
            html: `
                <div style="
                    width: ${size}px;
                    height: ${size}px;
                    background-color: ${color};
                    border: ${borderWidth}px solid white;
                    border-radius: 50%;
                    box-shadow: 0 0 ${shadowSize}px rgba(0,0,0,0.3);
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
                    ...getLineStyle(selectedRoute.status),
                    lineCap: 'round',
                    lineJoin: 'round'
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
                                icon={createIcon(!!isSelected, !!isOrigin, !!isDestination)}
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