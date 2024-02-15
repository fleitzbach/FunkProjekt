import { get, writable } from 'svelte/store';
import { API_URL } from '../config';
import type { DataSettings, Station } from './types';
import { toast } from 'svelte-sonner';

// Temperature Data
function createDataStore() {
	const { subscribe, set } = writable([]);

	return {
		subscribe,
		fetchTemperatureData: async (id: string) => {
			const $dataSettings = get(dataSettings);
      
			let dataUrl = `${API_URL}/data/${id}/${$dataSettings.interval}`;
			if ($dataSettings.start && $dataSettings.end) {
				dataUrl += `?start=${$dataSettings.start}&end=${$dataSettings.end}`;
			}
			const response = await fetch(dataUrl);
			const data = await response.json();
			set(data);
		}
	};
}
export const dataStore = createDataStore();


function createDataSettingsStore() {
	const { subscribe, set } = writable<DataSettings>({ interval: 'year' });

	return {
		subscribe,
		setSettings: (settings: DataSettings) => {
			set(settings);
		},
		clearSettings: () => {
			set({ interval: 'year' });
		}
	};
}

export const dataSettings = createDataSettingsStore();


// Station List Data
function createStationListStore() {
	const { subscribe, set } = writable<Station[]>([]);
      
	return {
		subscribe,
		fetchStationsByCoords: async (lat, lng, radius, start?, end?) => {
			let url = `${API_URL}/stations`;
      url += `?latitude=${lat}&longitude=${lng}&radius=${radius}`;
			if (start) url += `&start=${start}`;
			if (end) url += `&end=${end}`;
      
      const response = await fetch(url);
			const newStationList = await response.json();
			set(newStationList);
		},
    fetchStationsByName: async (name: string) => {
      const response = await fetch(`${API_URL}/stations/${name}`);
      const newStationList = await response.json();
      set(newStationList);
    }
	};
}
export const stationList = createStationListStore();

// Current Station
function createCurrentStationStore() {
	const { subscribe, set } = writable<Station>(
		{
			id: '',
			name: '',
			latitude: 0,
			longitude: 0,
			first_year: 0,
			last_year: 0,
		}
	);

	return {
		subscribe,
		setCurrentStation: async (station) => {
			toast(`Loading data for ${station.name}`);
			set(station);
		},
		clearCurrentStation: () => {
			set({
				id: '',
				name: '',
				latitude: 0,
				longitude: 0,
				first_year: 0,
				last_year: 0,
			});
		}
	};
}

export const currentStation = createCurrentStationStore();
