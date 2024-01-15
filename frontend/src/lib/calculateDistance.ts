export function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the Earth in kilometers
    const radLat1 = degreesToRadians(lat1);
    const radLat2 = degreesToRadians(lat2);
    const deltaLat = degreesToRadians(lat2 - lat1);
    const deltaLon = degreesToRadians(lon2 - lon1);

    const a = Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
              Math.cos(radLat1) * Math.cos(radLat2) *
              Math.sin(deltaLon / 2) * Math.sin(deltaLon / 2);

    const c = 2 * Math.asin(Math.sqrt(a));
    return R * c; // Distance in kilometers
}

export function degreesToRadians(degrees) {
    return degrees * Math.PI / 180;
}