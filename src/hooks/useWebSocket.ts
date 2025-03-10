import { useState, useEffect } from 'react';
import { WeatherCondition, Route } from '@/types';

export const useWebSocket = () => {
    const [ws, setWs] = useState<WebSocket | null>(null);
    const [weatherConditions, setWeatherConditions] = useState<Record<string, WeatherCondition>>({});
    const [currentRoute, setCurrentRoute] = useState<Route | null>(null);
    const [routeHistory, setRouteHistory] = useState<Route[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const socket = new WebSocket('ws://191.91.240.39/metro/ws');
        
        socket.onopen = () => {
            console.log('WebSocket Connected');
            setWs(socket);
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case "initial_data":
                    setWeatherConditions(data.data.weather_conditions);
                    setRouteHistory(data.data.route_history);
                    break;
                    
                case "weather_update":
                    setWeatherConditions(data.weather_conditions);
                    break;
                    
                case "route_update":
                    setCurrentRoute(data.data.new_route);
                    setRouteHistory(data.data.route_history);
                    setWeatherConditions(data.data.new_route.weather_conditions);
                    setLoading(false);
                    break;
                    
                default:
                    if (data.error) {
                        setError(data.error);
                        setLoading(false);
                    }
            }
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            setError('Error en la conexión WebSocket');
        };

        return () => {
            if (socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
        };
    }, []);

    return { 
        ws, 
        weatherConditions, 
        currentRoute, 
        routeHistory,
        loading, 
        error, 
        setLoading, 
        setError 
    };
}; 