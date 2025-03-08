export const getWeatherIcon = (weather: string) => {
    switch(weather.toLowerCase()) {
        case 'lluvioso': return '🌧️';
        case 'nublado': return '☁️';
        case 'tormenta': return '⛈️';
        default: return '☀️';
    }
}; 