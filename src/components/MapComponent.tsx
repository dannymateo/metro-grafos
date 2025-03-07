'use client'

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

type MapComponentProps = {
    stations: string[];
    coordinates: Record<string, [number, number]>;
    selectedRoute?: {
        path: string[];
        coordinates: [number, number][];
    };
    lines?: Record<string, {
        color: string;
        stations: string[];
    }>;
    userLocation?: [number, number];
    nearestStation?: string;
}

export default function MapComponent({ stations, coordinates, selectedRoute, lines, userLocation, nearestStation }: MapComponentProps) {
    const [isLoading, setIsLoading] = useState(true);
    
    const MapWithNoSSR = dynamic(() => import('./Map'), {
        ssr: false,
        loading: () => (
            <div className="h-[600px] w-full relative rounded-xl overflow-hidden shadow-xl bg-gray-100 flex items-center justify-center">
                <div className="text-gray-500">Cargando mapa...</div>
            </div>
        )
    });

    useEffect(() => {
        setIsLoading(false);
    }, []);

    if (isLoading) {
        return (
            <div className="h-[600px] w-full relative rounded-xl overflow-hidden shadow-xl bg-gray-100 flex items-center justify-center">
                <div className="text-gray-500">Cargando mapa...</div>
            </div>
        );
    }

    return (
        <MapWithNoSSR 
            stations={stations} 
            coordinates={coordinates} 
            selectedRoute={selectedRoute} 
            lines={lines}
            userLocation={userLocation}
            nearestStation={nearestStation}
        />
    );
} 