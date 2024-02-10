import { writable } from 'svelte/store';


// Server Response Data
function createDataStore() {
  const { subscribe, set } = writable([]);

  return {
    subscribe,
    fetchData: async (url) => {
      const response = await fetch(url);
      const newData = await response.json();
      set(newData);
    },
  };
}
export const dataStore = createDataStore();


// Current Station
function createCurrentStationStore() {
  const { subscribe, set } = writable([]);

  return {
    subscribe,
    setCurrentStation: async (station) => {
      set(station);
    },
  };
}

export const currentStation = createCurrentStationStore();