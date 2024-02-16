
import { browser, building, dev, version } from '$app/environment';

let API_URL = 'https://api.wetter.fhy.re';

if (dev) {
    API_URL = 'http://localhost:8000';
}

export { API_URL };
