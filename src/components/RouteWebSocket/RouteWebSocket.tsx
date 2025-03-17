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
import { MapPin, Navigation, Clock, Train, AlertCircle, ArrowRight, GitCommit, Download, Info } from 'lucide-react';

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
                <div className="flex flex-col items-center justify-center gap-4 h-[300px]">
                    <Image 
                        src="/Logo.svg" 
                        alt="Metro de Medellín Logo" 
                        width={50} 
                        height={70}
                        className="mb-2"
                    />
                    <Spinner 
                        size="md" 
                        color="primary"
                        label="Cargando estaciones..." 
                        classNames={{
                            label: "text-[#2B3990]"
                        }}
                    />
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-white rounded-xl overflow-hidden">
            <div className="container mx-auto md:px-4 py-4 md:py-6">
                <Card className="mb-4 shadow-sm">
                    <CardBody className="py-3 md:py-4">
                        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 md:gap-4">
                            <div className="flex items-center gap-3 md:gap-4">
                                <Image 
                                    src="/Logo.svg" 
                                    alt="Metro de Medellín Logo" 
                                    width={58} 
                                    height={83}
                                    className="w-10 md:w-[58px]"
                                />
                                <div className="flex flex-col">
                                    <h1 className="text-lg md:text-2xl font-semibold text-[#2B3990]">
                                        Metro de Medellín
                                    </h1>
                                    <p className="text-xs md:text-sm text-gray-600">
                                        Sistema Inteligente de Rutas
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center w-full md:w-auto mt-2 md:mt-0">
                                <Button
                                    color="primary"
                                    variant="flat"
                                    onPress={() => {
                                        window.open(`http://191.91.240.39/metro/graph?t=${Date.now()}`, '_blank')
                                    }}
                                    startContent={<Download className="w-3 h-3 md:w-4 md:h-4" />}
                                    className="bg-[#2B3990] text-white hover:bg-[#232d73] transition-colors w-full md:w-auto"
                                    size="sm"
                                >
                                    <span className="text-xs md:text-sm">Ver Mapa del Sistema</span>
                                </Button>
                            </div>
                        </div>
                    </CardBody>
                </Card>
                
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 md:gap-6">
                    <Card className="lg:col-span-1 shadow-sm order-2 lg:order-1">
                        <CardHeader className="flex gap-2 py-3">
                            <div className="flex flex-col">
                                <p className="text-base md:text-lg font-semibold text-[#2B3990]">
                                    Planifica tu viaje
                                </p>
                                <p className="text-xs md:text-sm text-gray-600">
                                    Encuentra la mejor ruta para tu destino
                                </p>
                            </div>
                        </CardHeader>
                        <Divider/>
                        <CardBody className="space-y-3 md:space-y-4 py-3 md:py-4">
                            <div className="space-y-3">
                                <Autocomplete
                                    label="Estación de origen"
                                    placeholder="¿Desde dónde?"
                                    selectedKey={origin}
                                    onSelectionChange={(key) => setOrigin(key as string)}
                                    className="flex-1"
                                    startContent={<MapPin className="w-3 h-3 md:w-4 md:h-4 text-[#2B3990]" />}
                                    size="sm"
                                >
                                    {stations.map((station) => (
                                        <AutocompleteItem key={station} value={station} className="text-xs md:text-sm">
                                            {station}
                                        </AutocompleteItem>
                                    ))}
                                </Autocomplete>

                                <Autocomplete
                                    label="Estación de destino"
                                    placeholder="¿A dónde vas?"
                                    selectedKey={destination}
                                    onSelectionChange={(key) => setDestination(key as string)}
                                    startContent={<Navigation className="w-3 h-3 md:w-4 md:h-4 text-[#2B3990]" />}
                                    size="sm"
                                >
                                    {stations.map((station) => (
                                        <AutocompleteItem key={station} value={station} className="text-xs md:text-sm">
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
                                className="w-full bg-[#2B3990] text-white hover:bg-[#232d73] transition-colors"
                                size="md"
                                endContent={!loading && <Navigation className="w-3 h-3 md:w-4 md:h-4" />}
                            >
                                <span className="text-xs md:text-sm">
                                    {loading ? 'Calculando ruta...' : 'Buscar mejor ruta'}
                                </span>
                            </Button>

                            {error && (
                                <div className="flex items-center gap-2 p-2 md:p-3 rounded-lg bg-red-50 text-red-600 border border-red-100">
                                    <AlertCircle className="w-3 h-3 md:w-4 md:h-4 flex-shrink-0" />
                                    <span className="text-xs md:text-sm">{error}</span>
                                </div>
                            )}

                            {currentRoute && (
                                <Card className="border border-gray-100 shadow-sm">
                                    <CardBody className="space-y-3 md:space-y-4 py-3 md:py-4">
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 md:gap-3">
                                            <div className="flex items-center gap-2 md:gap-3 bg-gray-50 p-2 md:p-3 rounded-lg">
                                                <Clock className="w-4 h-4 md:w-5 md:h-5 text-[#2B3990]" />
                                                <div>
                                                    <p className="text-xs md:text-sm text-[#2B3990] font-medium">Tiempo estimado</p>
                                                    <p className="text-base md:text-lg font-bold text-[#2B3990]">
                                                        {currentRoute.estimated_time} min
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-2 md:gap-3 bg-gray-50 p-2 md:p-3 rounded-lg">
                                                <MapPin className="w-4 h-4 md:w-5 md:h-5 text-[#2B3990]" />
                                                <div>
                                                    <p className="text-xs md:text-sm text-[#2B3990] font-medium">Distancia total</p>
                                                    <p className="text-base md:text-lg font-bold text-[#2B3990]">
                                                        {currentRoute.total_distance} km
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="space-y-2">
                                            <div className="flex items-center gap-1 md:gap-2">
                                                <Train className="w-3 h-3 md:w-4 md:h-4 text-[#2B3990]" />
                                                <span className="text-xs md:text-sm font-medium text-[#2B3990]">Líneas del recorrido</span>
                                            </div>
                                            <div className="flex flex-wrap gap-1 md:gap-2">
                                                {currentRoute.lines.map((line) => (
                                                    <Chip
                                                        key={line}
                                                        style={{ 
                                                            backgroundColor: getLineColor(line),
                                                        }}
                                                        className="text-white font-medium text-xs"
                                                        size="sm"
                                                        startContent={<GitCommit className="w-2 h-2 md:w-3 md:h-3" />}
                                                    >
                                                        {line}
                                                    </Chip>
                                                ))}
                                            </div>
                                        </div>

                                        {currentRoute.transbordos.length > 0 && (
                                            <div className="space-y-2">
                                                <div className="flex items-center gap-1 md:gap-2">
                                                    <ArrowRight className="w-3 h-3 md:w-4 md:h-4 text-[#2B3990]" />
                                                    <span className="text-xs md:text-sm font-medium text-[#2B3990]">Transbordos</span>
                                                </div>
                                                <div className="flex flex-wrap gap-1 md:gap-2">
                                                    {currentRoute.transbordos.map((transbordo, index) => (
                                                        <Chip 
                                                            key={index} 
                                                            variant="flat" 
                                                            className="bg-gray-100 text-[#2B3990] text-xs"
                                                            size="sm"
                                                            startContent={<GitCommit className="w-2 h-2 md:w-3 md:h-3" />}
                                                        >
                                                            {transbordo}
                                                        </Chip>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {currentRoute.weather_impacts && (
                                            <div className="space-y-2">
                                                <div className="flex items-center gap-1 md:gap-2">
                                                    <Info className="w-3 h-3 md:w-4 md:h-4 text-[#2B3990]" />
                                                    <span className="text-xs md:text-sm font-medium text-[#2B3990]">Condiciones climáticas</span>
                                                </div>
                                                <WeatherImpactInfo weatherImpacts={currentRoute.weather_impacts} />
                                            </div>
                                        )}
                                    </CardBody>
                                </Card>
                            )}
                        </CardBody>
                    </Card>
                    <Card className="lg:col-span-2 shadow-sm order-1 lg:order-2 h-[300px] md:h-[400px] lg:h-auto">
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

                <div className="mt-3 md:mt-6">
                    <AdminPanel 
                        stations={stations}
                        onShowRoute={(route) => setSelectedHistoryRoute(route as Route)}
                    />
                </div>
            </div>
        </div>
    );
} 