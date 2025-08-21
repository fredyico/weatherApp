# Weather Dashboard (CLI)

A Python CLI tool for fetching and analyzing weather data from the OpenWeather API.  
Displays current conditions and a configurable 24–48h forecast in a clean terminal table,  
with summary statistics and optional CSV export.  

**Skills shown:** API integration, JSON parsing, CLI development, data summarization,  
CSV handling, environment-based configuration.

---

## Usage
```
# Metric (°C, km/h)
python app.py --city "Miramichi" --units metric

# Imperial (°F, mph)
python app.py --city "Miramichi" --units imperial
```

## Features

- Current conditions: temp, feels-like, humidity, pressure, wind, clouds, sunrise/sunset
- Forecast (3h steps): configurable hours (24/48), compact table
- Summary stats: min/max/avg temp, avg feels-like & humidity
- **CSV export**: `--csv forecast.csv`
- Safe config: reads `OPENWEATHER_API_KEY` from `.env`
- Units toggle: --units metric|imperial

---

## Quick Start

### 1) Clone & Install
```bash
git clone https://github.com/<your-username>/weatherApp.git
cd weatherApp
pip install -r requirements.txt
```

## Run

- Metric (°C, km/h)
python app.py --city "Miramichi" --units metric

- Imperial (°F, mph)
python app.py --city "Miramichi" --units imperial

## Changelog 
- 0.2: Units toggle (--units), improved printing.
- 0.1: Current weather, 24–48h forecast, summary, CSV export.

