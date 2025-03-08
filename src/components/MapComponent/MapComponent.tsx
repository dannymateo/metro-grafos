'use client'

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

import { Props } from './types';

export default function MapComponent({ 
    stations, 
    coordinates, 
    selectedRoute, 
    lines, 
    weatherConditions 
}: Props) {
    const [isLoading, setIsLoading] = useState(true);
    
    const MapWithNoSSR = dynamic(() => import('@/components/Map/Map').then(mod => mod.default), {
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
            weatherConditions={weatherConditions}
        />
    );
} 