import { MetroLines } from '../types';

export const fetchInitialData = async () => {
    const [stationsRes, coordsRes, linesRes] = await Promise.all([
        fetch('https://dasscoin.zapto.org/metro/stations'),
        fetch('https://dasscoin.zapto.org/metro/coordinates'),
        fetch('https://dasscoin.zapto.org/metro/lines')
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