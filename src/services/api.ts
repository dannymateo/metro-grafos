import { MetroLines } from '../types';

export const fetchInitialData = async () => {
    const [stationsRes, coordsRes, linesRes] = await Promise.all([
        fetch('https://191.91.240.39/metro/stations'),
        fetch('https://191.91.240.39/metro/coordinates'),
        fetch('https://191.91.240.39/metro/lines')
    ]);

    const stationsData = await stationsRes.json();
    const coordsData = await coordsRes.json();
    const linesData = await linesRes.json();

    return {
        stations: stationsData.stations || [],
        coordinates: coordsData.coordinates || {},
        lines: linesData.lines as MetroLines || {}
    };
}; 