type WeatherReading = {
    temperature: number;
    humidity: number;
    pressure: number;
    visibility: number;
};

export type MetroLines = {
    [key: string]: {
        color: string;
        stations: string[];
    };
}

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