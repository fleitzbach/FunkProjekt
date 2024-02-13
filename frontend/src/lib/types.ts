export type DataSettings = {
	start?: string;
	end?: string;
	interval: 'day' | 'month' | 'year' | 'season';
};

export type Station = {
	id: string;
	name: string;
	latitude: number;
	longitude: number;
	first_year: number;
	last_year: number;
	distance: number;
};