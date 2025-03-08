import { MetroLines } from '../types';

export const fetchInitialData = async () => {
    const [stationsRes, coordsRes, linesRes] = await Promise.all([
        fetch('http://localhost:8000/stations'),
        fetch('http://localhost:8000/coordinates'),
        fetch('http://localhost:8000/lines')
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