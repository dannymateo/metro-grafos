'use client';

import { useEffect, useState } from 'react';
import {
    Select,
    SelectItem,
    Button,
    Card,
    CardBody,
    CardHeader,
    Divider,
    Chip,
    Spinner,
    Modal,
    ModalContent,
    ModalHeader,
    ModalBody,
    ModalFooter,
    Autocomplete,
    AutocompleteItem
} from "@nextui-org/react";
import { MapPin, Navigation, Clock, Train, AlertCircle, Loader2, ArrowRight, GitCommit, Download, Crosshair } from 'lucide-react';
import MapComponent from './MapComponent';
import Image from 'next/image';
import AdminPanel from './AdminPanel';

export type Route = {
    path: string[];
    coordinates: [number, number][];
    num_stations: number;
    lines: string[];
    estimated_time: number;
    total_distance: number;
    transbordos: string[];
    timestamp: string;
    weather_impacts: any[];
}

export type MetroLines = {
    [key: string]: {
        color: string;
        stations: string[];
    };
}

export type WeatherReading = {
    temperature: number;
    humidity: number;
    pressure: number;
    visibility: number;
};

export type WeatherCondition = {
    type: 'sunny' | 'cloudy' | 'rainy' | 'stormy';
    intensity: number;
    name: string;
    icon: string;
    location: [number, number];
    readings: WeatherReading;
    station_id: string;
    last_updated: string;
};

type Station = {
    name: string;
    line: string;
}

// Mover la función fuera de los componentes
const getWeatherIcon = (weather: string) => {
    switch(weather.toLowerCase()) {
        case 'lluvioso': return '🌧️';
        case 'nublado': return '☁️';
        case 'tormenta': return '⛈️';
        default: return '☀️';
    }
};

const WeatherImpactInfo = ({ weatherImpacts }: { weatherImpacts: any[] }) => {
    if (!weatherImpacts?.length) return null;
    const [showDetails, setShowDetails] = useState(false);

    const maxImpact = Math.max(...weatherImpacts.map(impact => 
        Math.max(impact.conditions.origin.impact, impact.conditions.destination.impact)
    ));

    const getImpactColor = (impact: number) => {
        if (impact > 30) return 'text-red-600';
        if (impact > 20) return 'text-orange-500';
        return 'text-green-600';
    };

    return (
        <div className="mt-4">
            <div className="bg-gradient-to-r from-blue-50 to-yellow-50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <AlertCircle className="w-5 h-5 text-yellow-500" />
                        <div>
                            <div className="text-sm font-medium text-gray-700">Clima en ruta</div>
                            <div className="text-xs text-gray-500">{weatherImpacts.length} segmentos afectados</div>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <Chip
                            size="sm"
                            variant="flat"
                            color={maxImpact > 30 ? "danger" : maxImpact > 20 ? "warning" : "success"}
                            className="text-xs"
                            startContent={<Clock className="w-3 h-3" />}
                        >
                            +{maxImpact}% tiempo
                        </Chip>
                        <Button
                            size="sm"
                            variant="light"
                            onPress={() => setShowDetails(true)}
                        >
                            Ver detalles
                        </Button>
                    </div>
                </div>
            </div>

            <Modal 
                isOpen={showDetails} 
                onClose={() => setShowDetails(false)}
                size="md"
            >
                <ModalContent>
                    <ModalHeader>Detalles del clima en la ruta</ModalHeader>
                    <ModalBody>
                        <WeatherDetailsContent weatherImpacts={weatherImpacts} />
                    </ModalBody>
                    <ModalFooter>
                        <Button color="primary" onPress={() => setShowDetails(false)}>
                            Cerrar
                        </Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </div>
    );
};

// Componente separado para los detalles
const WeatherDetailsContent = ({ weatherImpacts }: { weatherImpacts: any[] }) => {
    return (
        <div className="space-y-2">
            {weatherImpacts.map((impact, idx) => (
                <div 
                    key={idx} 
                    className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 transition-all duration-200"
                >
                    <div className="flex items-center gap-1.5">
                        <span className="text-sm font-medium">
                            {impact.segment[0]} → {impact.segment[1]}
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1.5 bg-gray-50 px-2 py-1 rounded-full">
                            <span className="text-xs">{impact.conditions.origin.weather}</span>
                            <span className="text-base">{getWeatherIcon(impact.conditions.origin.weather)}</span>
                        </div>
                        <Chip 
                            size="sm" 
                            variant="flat" 
                            color={impact.conditions.origin.impact > 20 ? "warning" : "success"}
                        >
                            +{impact.conditions.origin.impact}%
                        </Chip>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default function RouteWebSocket() {
    const [ws, setWs] = useState<WebSocket | null>(null);
    const [stations, setStations] = useState<string[]>([]);
    const [coordinates, setCoordinates] = useState<Record<string, [number, number]>>({});
    const [lines, setLines] = useState<MetroLines>({});
    const [origin, setOrigin] = useState("");
    const [destination, setDestination] = useState("");
    const [currentRoute, setCurrentRoute] = useState<Route | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedHistoryRoute, setSelectedHistoryRoute] = useState<Route | null>(null);
    const [isMounted, setIsMounted] = useState(false);
    const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
    const [nearestStation, setNearestStation] = useState<string | null>(null);
    const [weatherConditions, setWeatherConditions] = useState<Record<string, WeatherCondition>>({});

    useEffect(() => {
        let mounted = true;
        setIsMounted(true);

        // Cargar datos iniciales
        const fetchInitialData = async () => {
            try {
                const [stationsRes, coordsRes, linesRes] = await Promise.all([
                    fetch('http://localhost:8000/stations'),
                    fetch('http://localhost:8000/coordinates'),
                    fetch('http://localhost:8000/lines')
                ]);

                if (!mounted) return;

                const stationsData = await stationsRes.json();
                const coordsData = await coordsRes.json();
                const linesData = await linesRes.json();

                setStations(stationsData.stations || []);
                setCoordinates(coordsData.coordinates || {});
                setLines(linesData.lines || {});
            } catch (error) {
                console.error('Error fetching initial data:', error);
            }
        };

        // Inicializar WebSocket
        const initializeWebSocket = () => {
            const socket = new WebSocket('ws://localhost:8000/ws');
            
            socket.onopen = () => {
                console.log('WebSocket Connected');
                if (mounted) setWs(socket);
            };

            socket.onmessage = (event) => {
                if (!mounted) return;
                const data = JSON.parse(event.data);
                
                if (data.type === "weather_update") {
                    setWeatherConditions(data.weather_conditions);
                } else if (data.weather_conditions) {
                    setCurrentRoute(data);
                    setWeatherConditions(data.weather_conditions);
                }
                setLoading(false);
            };

            socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                if (mounted) setError('Error en la conexión WebSocket');
            };

            return socket;
        };

        fetchInitialData();
        const socket = initializeWebSocket();

        return () => {
            mounted = false;
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
        };
    }, []);

    const handleRouteRequest = () => {
        if (!ws || !origin || !destination) return;

        setLoading(true);
        setError(null);
        
        ws.send(JSON.stringify({
            origin,
            destination,
            user_location: userLocation ? {
                latitude: userLocation[0],
                longitude: userLocation[1]
            } : null,
            real_time_factors: {
                traffic: {}
            }
        }));
    };

    const getLineColor = (lineName: string) => {
        return lines[lineName]?.color || '#000000';
    };

    const handleLocationRequest = () => {
        if ("geolocation" in navigator) {
            setLoading(true);
            const options = {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            };

            navigator.geolocation.getCurrentPosition(
                // Success callback
                (position) => {
                    const userCoords: [number, number] = [
                        position.coords.latitude,
                        position.coords.longitude
                    ];
                    setUserLocation(userCoords);
                    findNearestStation(userCoords);
                    setLoading(false);
                },
                // Error callback
                (error) => {
                    setLoading(false);
                    let errorMessage = "No se pudo obtener tu ubicación";
                    
                    switch (error.code) {
                        case GeolocationPositionError.PERMISSION_DENIED:
                            errorMessage = "Necesitamos permiso para acceder a tu ubicación";
                            break;
                        case GeolocationPositionError.POSITION_UNAVAILABLE:
                            errorMessage = "La información de ubicación no está disponible";
                            break;
                        case GeolocationPositionError.TIMEOUT:
                            errorMessage = "Se agotó el tiempo para obtener la ubicación";
                            break;
                    }
                    
                    setError(errorMessage);
                    console.warn("Error de geolocalización:", error.message);
                },
                // Options
                options
            );
        } else {
            setError("Tu navegador no soporta geolocalización");
        }
    };

    const findNearestStation = (userCoords: [number, number]) => {
        let nearestDist = Infinity;
        let nearest = null;

        for (const [station, coords] of Object.entries(coordinates)) {
            const dist = calculateDistance(userCoords, coords);
            if (dist < nearestDist) {
                nearestDist = dist;
                nearest = station;
            }
        }

        if (nearest) {
            setNearestStation(nearest);
            setOrigin(nearest);
        }
    };

    const calculateDistance = (coord1: [number, number], coord2: [number, number]) => {
        const [lat1, lon1] = coord1;
        const [lat2, lon2] = coord2;
        const R = 6371; // Radio de la Tierra en km

        const dLat = toRad(lat2 - lat1);
        const dLon = toRad(lon2 - lon1);
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    };

    const toRad = (value: number) => {
        return value * Math.PI / 180;
    };

    if (!isMounted) {
        return null;
    }

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
            <div className="container mx-auto px-4 py-8">
                <Card className="mb-8 bg-white/70 backdrop-blur-md shadow-lg border-none">
                    <CardBody>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <Image 
                                    src="/Logo.svg" 
                                    alt="Metro de Medellín Logo" 
                                    width={58} 
                                    height={83}
                                    className="transition-transform hover:scale-105"
                                />
                                <div>
                                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-900 to-blue-600 bg-clip-text text-transparent">
                                        Metro de Medellín
                                    </h1>
                                    <p className="text-gray-600 mt-1">
                                        Sistema Inteligente de Rutas
                                    </p>
                                </div>
                            </div>
                            <Button
                                color="primary"
                                variant="ghost"
                                onClick={() => {
                                    window.open(`http://localhost:8000/graph?t=${Date.now()}`, '_blank')
                                }}
                                startContent={<Download className="w-4 h-4" />}
                            >
                                Ver Mapa del Sistema
                            </Button>
                        </div>
                    </CardBody>
                </Card>
                
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <Card className="lg:col-span-1 bg-white/70 backdrop-blur-md shadow-lg border-none">
                        <CardHeader className="flex gap-3">
                            <div className="flex flex-col">
                                <p className="text-xl font-semibold bg-gradient-to-r from-blue-900 to-blue-600 bg-clip-text text-transparent">
                                    Planifica tu viaje
                                </p>
                                <p className="text-small text-gray-500">
                                    Encuentra la mejor ruta para tu destino
                                </p>
                            </div>
                        </CardHeader>
                        <Divider/>
                        <CardBody className="space-y-6">
                            <div className="space-y-6">
                                <div className="flex gap-2">
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
                                    <Button
                                        isIconOnly
                                        color="primary"
                                        variant="flat"
                                        onClick={handleLocationRequest}
                                        title="Usar mi ubicación actual"
                                    >
                                        <Crosshair className="w-4 h-4" />
                                    </Button>
                                </div>

                                <Autocomplete
                                    label="Estación de destino"
                                    placeholder="¿A dónde vas?"
                                    selectedKey={destination}
                                    onSelectionChange={(key) => setDestination(key as string)}
                                    startContent={
                                        <div className="flex items-center">
                                            <Navigation className="text-red-500 w-5 h-5" />
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
                                onClick={handleRouteRequest}
                                isLoading={loading}
                                disabled={!origin || !destination}
                                className="w-full bg-gradient-to-r from-blue-700 to-blue-500 shadow-lg hover:shadow-blue-200 transition-all"
                                size="lg"
                                endContent={!loading && <Navigation className="w-5 h-5" />}
                            >
                                {loading ? 'Calculando ruta...' : 'Buscar mejor ruta'}
                            </Button>

                            {error && (
                                <div className="flex items-center gap-2 p-4 rounded-lg bg-red-50 text-red-600 border border-red-100 animate-fadeIn">
                                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                                    <span className="text-sm">{error}</span>
                                </div>
                            )}

                            {currentRoute && (
                                <Card className="bg-gradient-to-br from-blue-50 to-white border-none shadow-sm">
                                    <CardBody className="space-y-4">
                                        <div className="grid grid-cols-2 gap-3">
                                            <div className="flex items-center gap-3 bg-blue-100/50 p-3 rounded-lg">
                                                <Clock className="w-6 h-6 text-blue-600" />
                                                <div>
                                                    <p className="text-sm text-blue-600 font-medium">Tiempo estimado</p>
                                                    <p className="text-xl font-bold text-blue-900">
                                                        {currentRoute.estimated_time} minutos
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-3 bg-green-100/50 p-3 rounded-lg">
                                                <MapPin className="w-6 h-6 text-green-600" />
                                                <div>
                                                    <p className="text-sm text-green-600 font-medium">Distancia total</p>
                                                    <p className="text-xl font-bold text-green-900">
                                                        {currentRoute.total_distance} km
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="space-y-3">
                                            <div className="flex items-center gap-2">
                                                <Train className="w-5 h-5 text-blue-600" />
                                                <span className="font-medium text-blue-900">Líneas del recorrido</span>
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
                                                        startContent={<GitCommit className="w-4 h-4" />}
                                                    >
                                                        Línea {line}
                                                    </Chip>
                                                ))}
                                            </div>
                                        </div>

                                        {currentRoute.transbordos.length > 0 && (
                                            <div className="space-y-3">
                                                <div className="flex items-center gap-2">
                                                    <ArrowRight className="w-5 h-5 text-orange-500" />
                                                    <span className="font-medium text-blue-900">Transbordos</span>
                                                </div>
                                                <div className="flex flex-wrap gap-2">
                                                    {currentRoute.transbordos.map((transbordo, index) => (
                                                        <Chip 
                                                            key={index} 
                                                            variant="flat" 
                                                            color="warning"
                                                            className="transition-transform hover:scale-105"
                                                            startContent={<GitCommit className="w-4 h-4" />}
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
                    <Card className="lg:col-span-2 bg-white/70 backdrop-blur-md shadow-lg border-none overflow-hidden">
                        <CardBody className="p-0">
                            <MapComponent 
                                stations={stations}
                                coordinates={coordinates}
                                selectedRoute={selectedHistoryRoute || currentRoute}
                                lines={lines}
                                userLocation={userLocation || undefined}
                                nearestStation={nearestStation || undefined}
                                weatherConditions={weatherConditions}
                            />
                        </CardBody>
                    </Card>
                </div>

                <div className="mt-8">
                    <AdminPanel 
                        stations={stations}
                        onShowRoute={(route) => setSelectedHistoryRoute(route as Route)}
                    />
                </div>
            </div>
        </div>
    );
} 