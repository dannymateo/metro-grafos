'use client';

import { useEffect, useState } from 'react';
import {
    Button,
    Card,
    CardBody,
    CardHeader,
    Divider,
    Chip,
    Spinner,
    Autocomplete,
    AutocompleteItem,
} from "@nextui-org/react";
import { MapPin, Navigation, Clock, Train, AlertCircle, ArrowRight, GitCommit, Download } from 'lucide-react';

import MapComponent from '@/components/MapComponent/MapComponent';
import Image from 'next/image';
import AdminPanel from '@/components/AdminPanel/AdminPanel';
import { useWebSocket } from '@/hooks/useWebSocket';
import { fetchInitialData } from '@/services/api';
import { WeatherImpactInfo } from '@/components/WeatherDetailsContent';
import { MetroLines } from './types';
import { Route } from '@/types';

export default function RouteWebSocket() {
    const { ws, weatherConditions, currentRoute, loading, error, setLoading, setError } = useWebSocket();
    const [stations, setStations] = useState<string[]>([]);
    const [coordinates, setCoordinates] = useState<Record<string, [number, number]>>({});
    const [lines, setLines] = useState<MetroLines>({});
    const [origin, setOrigin] = useState("");
    const [destination, setDestination] = useState("");
    const [selectedHistoryRoute, setSelectedHistoryRoute] = useState<Route | null>(null);

    useEffect(() => {
        const loadInitialData = async () => {
            try {
                const data = await fetchInitialData();
                setStations(data.stations);
                setCoordinates(data.coordinates);
                setLines(data.lines);
            } catch (error) {
                console.error('Error fetching initial data:', error);
            }
        };

        loadInitialData();
    }, []);

    const handleRouteRequest = () => {
        if (!ws || !origin || !destination) return;

        setLoading(true);
        setError(null);
        
        ws.send(JSON.stringify({
            origin,
            destination,
            real_time_factors: {
                traffic: {}
            }
        }));
    };

    const getLineColor = (lineName: string) => {
        return lines[lineName]?.color || '#000000';
    };

    if (!stations.length) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="flex flex-col items-center justify-center gap-4 h-[400px]">
                    <Image 
                        src="/Logo.svg" 
                        alt="Metro de Medellín Logo" 
                        width={58} 
                        height={83}
                        className="mb-4"
                    />
                    <Spinner 
                        size="lg" 
                        label="Cargando estaciones..." 
                    />
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
            <div className="container mx-auto mobile-spacing">
                <Card className="mb-4 md:mb-8 glass-effect responsive-card">
                    <CardBody>
                        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                            <div className="flex items-center gap-4">
                                <Image 
                                    src="/Logo.svg" 
                                    alt="Metro de Medellín Logo" 
                                    width={58} 
                                    height={83}
                                    className="transition-transform hover:scale-105 w-12 md:w-[58px]"
                                />
                                <div>
                                    <h1 className="text-2xl md:text-4xl font-bold bg-gradient-to-r from-blue-900 to-blue-600 bg-clip-text text-transparent">
                                        Metro de Medellín
                                    </h1>
                                    <p className="text-sm md:text-base text-gray-600 mt-1">
                                        Sistema Inteligente de Rutas
                                    </p>
                                </div>
                            </div>
                            <Button
                                color="primary"
                                variant="ghost"
                                onPress={() => {
                                    window.open(`http://191.91.240.39/metro/graph?t=${Date.now()}`, '_blank')
                                }}
                                startContent={<Download className="w-4 h-4" />}
                                className="w-full md:w-auto touch-target"
                            >
                                Ver Mapa del Sistema
                            </Button>
                        </div>
                    </CardBody>
                </Card>
                
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-8">
                    <Card className="lg:col-span-1 glass-effect responsive-card order-2 lg:order-1">
                        <CardHeader className="flex gap-3">
                            <div className="flex flex-col">
                                <p className="text-lg md:text-xl font-semibold bg-gradient-to-r from-blue-900 to-blue-600 bg-clip-text text-transparent">
                                    Planifica tu viaje
                                </p>
                                <p className="text-xs md:text-sm text-gray-500">
                                    Encuentra la mejor ruta para tu destino
                                </p>
                            </div>
                        </CardHeader>
                        <Divider/>
                        <CardBody className="space-y-4 md:space-y-6">
                            <div className="space-y-4">
                                <Autocomplete
                                    label="Estación de origen"
                                    placeholder="¿Desde dónde?"
                                    selectedKey={origin}
                                    onSelectionChange={(key) => setOrigin(key as string)}
                                    className="flex-1"
                                    startContent={<MapPin className="w-4 h-4" />}
                                >
                                    {stations.map((station) => (
                                        <AutocompleteItem key={station} value={station}>
                                            {station}
                                        </AutocompleteItem>
                                    ))}
                                </Autocomplete>

                                <Autocomplete
                                    label="Estación de destino"
                                    placeholder="¿A dónde vas?"
                                    selectedKey={destination}
                                    onSelectionChange={(key) => setDestination(key as string)}
                                    startContent={
                                        <div className="flex items-center">
                                            <Navigation className="text-red-500 w-4 h-4 md:w-5 md:h-5" />
                                        </div>
                                    }
                                >
                                    {stations.map((station) => (
                                        <AutocompleteItem key={station} value={station}>
                                            {station}
                                        </AutocompleteItem>
                                    ))}
                                </Autocomplete>
                            </div>

                            <Button
                                color="primary"
                                onPress={handleRouteRequest}
                                isLoading={loading}
                                disabled={!origin || !destination}
                                className="w-full bg-gradient-to-r from-blue-700 to-blue-500 shadow-lg hover:shadow-blue-200 transition-all touch-target"
                                size="lg"
                                endContent={!loading && <Navigation className="w-4 h-4 md:w-5 md:h-5" />}
                            >
                                {loading ? 'Calculando ruta...' : 'Buscar mejor ruta'}
                            </Button>

                            {error && (
                                <div className="flex items-center gap-2 p-3 md:p-4 rounded-lg bg-red-50 text-red-600 border border-red-100 animate-fadeIn">
                                    <AlertCircle className="w-4 h-4 md:w-5 md:h-5 flex-shrink-0" />
                                    <span className="text-xs md:text-sm">{error}</span>
                                </div>
                            )}

                            {currentRoute && (
                                <Card className="bg-gradient-to-br from-blue-50 to-white border-none shadow-sm">
                                    <CardBody className="space-y-4">
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                            <div className="flex items-center gap-3 bg-blue-100/50 p-3 rounded-lg">
                                                <Clock className="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
                                                <div>
                                                    <p className="text-xs md:text-sm text-blue-600 font-medium">Tiempo estimado</p>
                                                    <p className="text-lg md:text-xl font-bold text-blue-900">
                                                        {currentRoute.estimated_time} minutos
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-3 bg-green-100/50 p-3 rounded-lg">
                                                <MapPin className="w-5 h-5 md:w-6 md:h-6 text-green-600" />
                                                <div>
                                                    <p className="text-xs md:text-sm text-green-600 font-medium">Distancia total</p>
                                                    <p className="text-lg md:text-xl font-bold text-green-900">
                                                        {currentRoute.total_distance} km
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="space-y-3">
                                            <div className="flex items-center gap-2">
                                                <Train className="w-4 h-4 md:w-5 md:h-5 text-blue-600" />
                                                <span className="text-sm md:text-base font-medium text-blue-900">Líneas del recorrido</span>
                                            </div>
                                            <div className="flex flex-wrap gap-2">
                                                {currentRoute.lines.map((line) => (
                                                    <Chip
                                                        key={line}
                                                        style={{ 
                                                            backgroundColor: getLineColor(line),
                                                            boxShadow: `0 2px 4px ${getLineColor(line)}40`
                                                        }}
                                                        className="text-white font-medium transition-transform hover:scale-105"
                                                        size="sm"
                                                        startContent={<GitCommit className="w-3 h-3 md:w-4 md:h-4" />}
                                                    >
                                                        Línea {line}
                                                    </Chip>
                                                ))}
                                            </div>
                                        </div>

                                        {currentRoute.transbordos.length > 0 && (
                                            <div className="space-y-3">
                                                <div className="flex items-center gap-2">
                                                    <ArrowRight className="w-4 h-4 md:w-5 md:h-5 text-orange-500" />
                                                    <span className="text-sm md:text-base font-medium text-blue-900">Transbordos</span>
                                                </div>
                                                <div className="flex flex-wrap gap-2">
                                                    {currentRoute.transbordos.map((transbordo, index) => (
                                                        <Chip 
                                                            key={index} 
                                                            variant="flat" 
                                                            color="warning"
                                                            size="sm"
                                                            className="transition-transform hover:scale-105"
                                                            startContent={<GitCommit className="w-3 h-3 md:w-4 md:h-4" />}
                                                        >
                                                            {transbordo}
                                                        </Chip>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {currentRoute.weather_impacts && (
                                            <WeatherImpactInfo weatherImpacts={currentRoute.weather_impacts} />
                                        )}
                                    </CardBody>
                                </Card>
                            )}
                        </CardBody>
                    </Card>
                    <Card className="lg:col-span-2 glass-effect responsive-card order-1 lg:order-2">
                        <CardBody className="p-0">
                            <MapComponent 
                                stations={stations}
                                coordinates={coordinates}
                                selectedRoute={selectedHistoryRoute || currentRoute}
                                lines={lines}
                                weatherConditions={weatherConditions}
                            />
                        </CardBody>
                    </Card>
                </div>

                <div className="mt-4 md:mt-8">
                    <AdminPanel 
                        stations={stations}
                        onShowRoute={(route) => setSelectedHistoryRoute(route as Route)}
                    />
                </div>
            </div>
        </div>
    );
} 