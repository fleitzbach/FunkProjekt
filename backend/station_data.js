import fetch from 'node-fetch';
import fs from 'fs';

async function _getStations() {
    const url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt";
    const response = await fetch(url);
    if (response.status === 200) {
        const text = await response.text();
        const data = text.split(/\n+/).map(line => ({
            id: line.slice(0, 11).trim(),
            latitude: parseFloat(line.slice(12, 20)),
            longitude: parseFloat(line.slice(21, 30)),
            name: line.slice(41, 71).trim()
        }));
        return data;
    } else {
        throw new Error(`Error fetching stations: ${response.status}`);
    }
}

async function _getInventory() {
    const url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt";
    const response = await fetch(url);
    if (response.status === 200) {
        const text = await response.text();
        const data = text.split(/\n+/)
            .map(line => ({
                id: line.slice(0, 11).trim(),
                element: line.slice(31, 35).trim(),
                firstYear: parseInt(line.slice(36, 40)),
                lastYear: parseInt(line.slice(41, 45))
            }))
            .filter(entry => entry.element === 'TMAX' || entry.element === 'TMIN')
            .reduce((acc, cur) => {
                if (!acc.has(cur.id)) {
                    acc.set(cur.id, {
                        id: cur.id,
                        firstYear: cur.firstYear,
                        lastYear: cur.lastYear
                    });
                }
                return acc;
            }, new Map())
            .values();
        return Array.from(data);
    } else {
        throw new Error(`Error fetching inventory: ${response.status}`);
    }
}

async function loadStations() {
    try {
        const stations = await _getStations();
        const inventory = await _getInventory();
        const combined = stations.map(station => ({
            ...station,
            ...inventory.find(entry => entry.id === station.id)
        }));
        const csv = combined.map(station => `${station.id},${station.latitude},${station.longitude},${station.name},${station.first_year},${station.last_year}`).join('\n');
        fs.writeFileSync('stations.csv', csv);
    } catch (error) {
        console.error('Error loading stations:', error);
    }
}

function calculateDistance(latitude1, longitude1, latitude2, longitude2) {
    const R = 6371.0; // Radius of the Earth in kilometers
    const lat1 = radians(latitude1);
    const lon1 = radians(longitude1);
    const lat2 = radians(latitude2);
    const lon2 = radians(longitude2);
    const dlon = lon2 - lon1;
    const dlat = lat2 - lat1;
    const a = Math.pow(Math.sin(dlat / 2.0), 2) + Math.cos(lat1) * Math.cos(lat2) * Math.pow(Math.sin(dlon / 2.0), 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c;
    return distance;
}

function radians(degrees) {
    return degrees * Math.PI / 180;
}

function getStations(latitude, longitude, radius, start, end, selection) {
    const stations = fs.readFileSync('stations.csv', 'utf8').split('\n').map(line => {
        const [id, lat, lon, name, firstYear, lastYear] = line.split(',');
        return {
            id,
            latitude: parseFloat(lat),
            longitude: parseFloat(lon),
            name,
            firstYear: parseInt(firstYear),
            lastYear: parseInt(lastYear)
        };
    });
    
    const nearbyStations = stations
        .map(station => ({
            ...station,
            distance: calculateDistance(latitude, longitude, station.latitude, station.longitude)
        }))
        .sort((a, b) => a.distance - b.distance)
        .filter(station => station.distance <= radius)
        .filter(station => (start === null || station.firstYear <= start) && (end === null || station.lastYear >= end));
    
    return selection !== undefined ? nearbyStations.slice(0, selection) : nearbyStations;
}

function getStationByName(name) {
    const stations = fs.readFileSync('stations.csv', 'utf8').split('\n').map(line => {
        const [id, lat, lon, stationName, firstYear, lastYear] = line.split(',');
        return {
            id,
            latitude: parseFloat(lat),
            longitude: parseFloat(lon),
            name: stationName,
            firstYear: parseInt(firstYear),
            lastYear: parseInt(lastYear)
        };
    });
    return stations.filter(station => station.name.toLowerCase().includes(name.toLowerCase()));
}

function main() {
    const result = getStations(51.5, 7.5, 100, 2010, 2020, 10);
    console.log(result);
}

main();

const stationData = {
    loadStations,
    getStations,
    getStationByName
};

export default stationData;