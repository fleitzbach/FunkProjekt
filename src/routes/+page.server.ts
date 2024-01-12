import fetch from 'node-fetch';

export async function load() {
	// URL of the data file
	const url = 'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt';

	try {
		// Stream and parse the data
		const parsedDataPromise = streamAndParseData(url);

		// Return the parsed data
		return {
			pointsPromise: parsedDataPromise,
		};
	} catch (error) {
		console.error('Error loading data:', error);
		return null;
	}
}

// Function to stream and parse data from URL
async function streamAndParseData(url: string): Promise<any[]> {
	const response = await fetch(url);
	const stream = response.body;

	return new Promise((resolve, reject) => {
		let buffer = '';
		const parsedLines = [];

		stream.on('data', (chunk) => {
			buffer += chunk.toString();
			let boundary = buffer.lastIndexOf('\n');
			let chunkLines = buffer.substring(0, boundary).split('\n');
			buffer = buffer.substring(boundary + 1);
            //console.log(chunkLines)
            let row: { id: string; latitude: number; longitude: number; name: string } = {};
			chunkLines.forEach((line) => {
				row.id = line.slice(0, 11);
				row.latitude = parseFloat(line.slice(12, 20));
				row.longitude = parseFloat(line.slice(21, 30));
				row.name = line.slice(41, 71);
				parsedLines.push(row);
                row = {}
			});
		});

		stream.on('end', () => {
			if (buffer.length > 0) {
				// parsedLines.push(parseLine(buffer)); // parse any remaining line
			}
			resolve(parsedLines);
		});

		stream.on('error', (err) => {
			reject(err);
		});
	});
}

// Function to parse a single line
function parseLine(line: string) {
	// Replace this with actual parsing logic based on the data format
	// Example: const [component1, component2, ...] = line.split(' ');
	// Return parsed line
}
