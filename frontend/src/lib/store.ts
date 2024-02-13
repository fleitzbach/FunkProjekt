import { writable } from 'svelte/store';


// Temperature Data
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

// Station List Data
function createStationListStore() {
  const { subscribe, set } = writable([]);

  return {
    subscribe,
    fetchStationList: async (url) => {
      const response = await fetch(url);
      const newStationList = await response.json();
      set(newStationList);
    },
  };
}
export const stationList = createStationListStore();

// Current Station
function createCurrentStationStore() {
  const { subscribe, set } = writable([]);

  return {
    subscribe,
    setCurrentStation: async (station) => {
      set(station);
    },
    clearCurrentStation: () => {
      set([]);
    }
  };
}

export const currentStation = createCurrentStationStore();