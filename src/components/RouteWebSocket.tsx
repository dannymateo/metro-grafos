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
    Input
} from "@nextui-org/react";
import { MapPin, Navigation, Clock, Train, AlertCircle, Loader2, ArrowRight, GitCommit, Navigation2, Download, Search, Crosshair } from 'lucide-react';
import MapComponent from './MapComponent';
import Image from 'next/image';
import AdminPanel from './AdminPanel';

type Station = {
    name: string;
    line: string;
}

type Route = {
    path: string[];
    coordinates: [number, number][];
    num_stations: number;
    lines: string[];
    estimated_time: number;
    transbordos: string[];
    timestamp: string;
}

type MetroLines = {
    [key: string]: {
        color: string;
        stations: string[];
    };
}

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
    const [weatherInfo, setWeatherInfo] = useState<Record<string, any>>({});
    const [zoneConditions, setZoneConditions] = useState<Record<string, any>>({});
    const [useCurrentLocation, setUseCurrentLocation] = useState(false);
    const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
    const [nearestStation, setNearestStation] = useState<string | null>(null);

    useEffect(() => {
        setIsMounted(true);
        const fetchStationsAndLines = async () => {
            try {
                const [stationsRes, linesRes, coordsRes] = await Promise.all([
                    fetch('http://localhost:8000/stations'),
                    fetch('http://localhost:8000/lines'),
                    fetch('http://localhost:8000/coordinates')
                ]);
                
                const stationsData = await stationsRes.json();
                const linesData = await linesRes.json();
                const coordsData = await coordsRes.json();
                
                if (Array.isArray(stationsData.stations)) {
                    setStations(stationsData.stations);
                } else {
                    console.error('Stations data is not an array:', stationsData);
                    setStations([]);
                }

                if (coordsData.coordinates) {
                    setCoordinates(coordsData.coordinates);
                }

                if (linesData.lines) {
                    setLines(linesData.lines);
                }
            } catch (error) {
                console.error('Error fetching data:', error);
                setError('Error al cargar las estaciones y líneas');
                setStations([]);
                setCoordinates({});
                setLines({});
            }
        };

        fetchStationsAndLines();

        const socket = new WebSocket('ws://localhost:8000/ws');
        
        socket.onopen = () => {
            console.log('WebSocket Connected');
            setWs(socket);
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('WebSocket message received:', data);

            if (data.type === "weather_update") {
                console.log('Weather update received:', data.zone_conditions);
                setZoneConditions(data.zone_conditions);
                if (currentRoute) {
                    handleRouteRequest();
                }
            } else if (data.error) {
                setError(data.error);
                setLoading(false);
            } else {
                setCurrentRoute(data);
                if (data.weather_info) {
                    setWeatherInfo(data.weather_info);
                }
                if (data.zone_conditions) {
                    setZoneConditions(data.zone_conditions);
                }
                setLoading(false);
            }
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            setError('Error en la conexión WebSocket');
            setLoading(false);
        };

        return () => {
            if (socket) {
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
                                    <Select
                                        label="Origen"
                                        placeholder="Selecciona estación de origen"
                                        value={origin}
                                        onChange={(e) => setOrigin(e.target.value)}
                                        startContent={<MapPin className="w-4 h-4" />}
                                    >
                                        {stations.map((station) => (
                                            <SelectItem key={station} value={station}>
                                                {station}
                                            </SelectItem>
                                        ))}
                                    </Select>
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

                                <div className="flex justify-center">
                                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                                        <ArrowRight className="text-blue-600 w-5 h-5" />
                                    </div>
                                </div>

                                <Select
                                    label="Estación de destino"
                                    placeholder="¿A dónde vas?"
                                    value={destination}
                                    onChange={(e) => setDestination(e.target.value)}
                                    startContent={
                                        <div className="flex items-center">
                                            <Navigation className="text-red-500 w-5 h-5" />
                                            <Search className="text-gray-400 w-4 h-4 ml-2" />
                                        </div>
                                    }
                                    classNames={{
                                        label: "text-blue-900 font-medium",
                                        trigger: "bg-white/50 data-[hover=true]:bg-white/80 transition-all",
                                        base: "max-w-full",
                                    }}
                                >
                                    {stations.map((station) => (
                                        <SelectItem 
                                            key={station} 
                                            value={station}
                                            className="data-[hover=true]:bg-blue-50"
                                        >
                                            {station}
                                        </SelectItem>
                                    ))}
                                </Select>
                            </div>

                            <Button
                                color="primary"
                                onClick={handleRouteRequest}
                                isLoading={loading}
                                disabled={!origin || !destination}
                                className="w-full bg-gradient-to-r from-blue-700 to-blue-500 shadow-lg hover:shadow-blue-200 transition-all"
                                size="lg"
                                startContent={!loading && <Navigation2 className="w-5 h-5" />}
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
                                        <div className="flex items-center gap-3 bg-blue-100/50 p-3 rounded-lg">
                                            <Clock className="w-6 h-6 text-blue-600" />
                                            <div>
                                                <p className="text-sm text-blue-600 font-medium">Tiempo estimado</p>
                                                <p className="text-xl font-bold text-blue-900">
                                                    {currentRoute.estimated_time} minutos
                                                </p>
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
                            />
                        </CardBody>
                    </Card>
                </div>

                <div className="mt-8">
                    <AdminPanel 
                        stations={stations}
                        onShowRoute={(route) => setSelectedHistoryRoute(route)}
                    />
                </div>
            </div>
        </div>
    );
} 