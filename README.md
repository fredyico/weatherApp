# Weather Dashboard (CLI)

A small, job-style Python CLI that fetches **current weather** and a **24–48h forecast** from OpenWeather, prints a clean terminal summary, and (optionally) exports CSV.

- **Tech:** Python 3.10+, `requests`, `python-dotenv`
- **Skills shown:** API integration, JSON parsing, CLI flags, input validation, simple data summarization, CSV export, environment-based config

---

## Usage

# Metric (°C, km/h)
python app.py --city "Miramichi" --units metric

# Imperial (°F, mph)
python app.py --city "Miramichi" --units imperial


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

