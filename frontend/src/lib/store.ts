import { get, writable } from 'svelte/store';
import { API_URL } from '../config';
import type { DataSettings, Station } from './types';
import { toast } from 'svelte-sonner';

// Temperature Data
function createDataStore() {
	const { subscribe, set, update } = writable({
		data: [],
		loading: false,
		error: null
	});

	return {
		subscribe,
		fetchTemperatureData: async (id: string) => {
			update((state) => ({ ...state, loading: true, error: null }));
			try {
				const $dataSettings = get(dataSettings);
				let dataUrl = `${API_URL}/data/${id}/${$dataSettings.interval}`;

				if ($dataSettings.start && $dataSettings.end) {
					dataUrl += `?start=${$dataSettings.start}&end=${$dataSettings.end}`;
				}

				const response = await fetch(dataUrl);

				if (!response.ok) {
					throw new Error('Failed to fetch data');
				}

				const data = await response.json();
				set({ data: data, loading: false, error: null });
			} catch (error) {
				set({ data: [], loading: false, error: error });
				toast.error("Error while fetching temperature data:", { description: error.message });
			}
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
	const { subscribe, set, update } = writable({
		data: <Station[]>[],
		loading: false,
		error: null
	});

	async function fetchAndUpdate(url) {
		try {
			//console.log('Fetching station data')
			update(({ data }) => ({ data, loading: true, error: null }));
			const response = await fetch(url);

			if (!response.ok) {
				throw new Error('Failed to fetch data');
			}

			const data = await response.json();

			if (data.length === 0) {
				toast.warning('No stations found');
			} else {
				toast('Found ' + data.length + ' stations');
			}
			set({ data: data, loading: false, error: null });
		} catch (error) {
			set({ data: [], loading: false, error: error });
			toast.error("Error while fetching station data:", { description: error.message });
		}
	}

	return {
		subscribe,
		fetchStationsByCoords: async (lat, lng, radius, start?, end?, maxStations?) => {
			let url = `${API_URL}/stations`;
			url += `?latitude=${lat}&longitude=${lng}&radius=${radius}`;
			if (start) url += `&start=${start}`;
			if (end) url += `&end=${end}`;
			if (maxStations) url += `&selection=${maxStations}`;

			await fetchAndUpdate(url);
		},
		fetchStationsByName: async (name: string) => {
			let url = `${API_URL}/stations/${name}`;

			await fetchAndUpdate(url);
		}
	};
}
export const stationList = createStationListStore();

// Current Station
function createCurrentStationStore() {
	const { subscribe, set } = writable<Station>({
		id: '',
		name: '',
		latitude: 0,
		longitude: 0,
		first_year: 0,
		last_year: 0
	});

	return {
		subscribe,
		setCurrentStation: async (station) => {
			set(station);
		},
		clearCurrentStation: () => {
			set({
				id: '',
				name: '',
				latitude: 0,
				longitude: 0,
				first_year: 0,
				last_year: 0
			});
		}
	};
}

export const currentStation = createCurrentStationStore();
