
import { dev } from '$app/environment';

let API_URL = 'https://wetter.fhy.re/api';

if (dev) {
    API_URL = 'http://localhost:8000';
}

export { API_URL };
