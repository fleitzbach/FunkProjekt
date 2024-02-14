import express from 'express';
import cors from 'cors';
import stationData from './station_data.js';

const app = express();

const origins = [
    "*",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
];

const corsOptions = {  //CORS Setup
    origin: origins,
    credentials: true,
    methods: ["GET"],
    allowedHeaders: ["*"]
};

app.use(cors(corsOptions));

app.get('/stations', (req, res) => {
    const { latitude, longitude, radius, start, end, selection } = req.query;
    stationData.getStations(latitude, longitude, radius, start, end, selection)
        .then(df => {
            res.json(df);
            res.status(200).json("successful");
        })
        .catch(error => {
            console.error("Error:", error);
            res.status(500).json({ error: "Error" });
        });
});

app.get('/reload_stations', (req, res) => {
    try {
        stationData.loadStations();
        res.send('Stations reloaded');
        res.status(200).json("successful");
    } catch (error) {
        console.error('Error:', error);
        res.status(500).send('Error');
    }
});

app.get('/stations/:name', (req, res) => {
    const { name } = req.params;
    stationData.getStationByName(name)
        .then(df => {
            res.json(df);
            res.status(200).json("successful");
        })
        .catch(error => {
            console.error("Error:", error);
            res.status(500).json({ error: "Error" });
        });
});

app.listen(8000, () => console.log('Server running on port 8000'));