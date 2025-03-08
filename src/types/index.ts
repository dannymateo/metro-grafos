export type Route = {
    path: string[];
    coordinates: [number, number][];
    num_stations: number;
    lines: string[];
    estimated_time: number;
    total_distance: number;
    transbordos: string[];
    timestamp: string;
    weather_impacts: WeatherImpact[];
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

export type WeatherImpact = {
    segment: [string, string];
    line: string;
    conditions: {
        origin: WeatherConditionImpact;
        destination: WeatherConditionImpact;
    };
};

export type WeatherConditionImpact = {
    station: string;
    weather: string;
    impact: number;
}; 