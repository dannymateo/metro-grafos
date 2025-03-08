import { WeatherCondition } from "@/types";

export type Props = {
    stations: string[];
    coordinates: Record<string, [number, number]>;
    selectedRoute?: {
        path: string[];
        coordinates: [number, number][];
        status?: {
            congestion: 'normal' | 'alta' | 'muy_alta';
            alerts?: string[];
        };
    } | null;
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
    weatherConditions?: Record<string, WeatherCondition>;
}