import { WeatherCondition, MetroLines, Route } from "@/types";

export type Props = {
    stations: string[];
    coordinates: Record<string, [number, number]>;
    selectedRoute: Route | null;
    lines: MetroLines;
    userLocation?: [number, number];
    nearestStation?: string;
    weatherConditions?: Record<string, WeatherCondition>;
}