from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, List
import requests
import csv

KELVIN_OFFSET = 273.15

def _to_local_time(utc_ts: int, tz_offset_sec: int) -> str:
    # Hint: your app did utcfromtimestamp(sunrise + timezone)
    return datetime.utcfromtimestamp(utc_ts + tz_offset_sec).strftime("%H:%M:%S")


def get_current_weather(city: str, api_key: str, units: str = "metric") -> Dict[str, Any]:
    """
    Returns a normalized dict:
      {
        "city": str,
        "temp_c": int,
        "feels_c": int,
        "humidity": int,
        "pressure": int,
        "wind_kmh": float,
        "sunrise_local": str,  # "HH:MM:SS"
        "sunset_local": str,   # "HH:MM:SS"
        "cloud_pct": int,
        "description": str
      }
    Raises:
      ValueError on bad city or API error.
    """
    # 1) Build URL (reuse what you had)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}"
    # 2) Call API and parse JSON
    resp = requests.get(url, timeout=10)
    data = resp.json()
    # 3) Handle errors (OpenWeatherMap uses "cod")
    #    Note: sometimes it's an int 200, sometimes a string — be robust.
    cod = int(data.get("cod", 0))
    if cod != 200:
        msg = data.get("message", "Unknown error")
        raise ValueError(f"OpenWeather error ({cod}): {msg}")
    tz = data["timezone"]                         # seconds
    temp = int(data["main"]["temp"])
    feels = int(data["main"]["feels_like"])
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    wind_speed = round(float(data["wind"]["speed"]), 1)  # m/s -> km/h
    sunrise_local = _to_local_time(data["sys"]["sunrise"], tz)
    sunset_local  = _to_local_time(data["sys"]["sunset"], tz)
    cloud_pct = data["clouds"]["all"]
    description = data["weather"][0]["description"]
    # 5) Return normalized dict
    return {
        "city": city,
        "temp": temp,
        "feels": feels,
        "humidity": humidity,
        "pressure": pressure,
        "wind_speed": wind_speed,
        "sunrise_local": sunrise_local,
        "sunset_local": sunset_local,
        "cloud_pct": cloud_pct,
        "description": description,
    }

def get_forecast(city: str, api_key: str, hours: int = 24, units: str = "metric") -> List[Dict[str, Any]]:
    """
    Returns a list of time-bucketed forecast entries (~3h steps) for the next `hours`.
    Each item:
      {
        "time_local": "YYYY-MM-DD HH:MM",
        "temp": int,
        "feels": int,
        "humidity": int
      }
    """
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units={units}"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    
    cod = int(data.get("cod", 0)) if isinstance(data.get("cod"), (int, str)) else 0
    if cod != 200:
        msg = data.get("message", "Unknown error")
        raise ValueError(f"OpenWeather forecast error ({cod}): {msg}")
    
    tz = data["city"]["timezone"]  # seconds offset
    out: List[Dict[str, Any]] = []
    
    # Each item is a 3-hour step. Collect until we cover `hours`.
    max_items = max(1, hours // 3)
    for item in data["list"][:max_items]:
        dt_utc = int(item["dt"])
        time_local = datetime.utcfromtimestamp(dt_utc + tz).strftime("%Y-%m-%d %H:%M")
        main = item["main"]
        out.append({
            "time_local": time_local,
            "temp": round(main["temp"]),
            "feels": round(main["feels_like"]),
            "humidity": int(main["humidity"]),
        })
    return out
    
def summarize_forecast(forecast: List[Dict[str, Any]]) -> Dict[str, Any]:
    temps = [row["temp"] for row in forecast] or [0]
    feels = [row["feels"] for row in forecast] or [0]
    hums  = [row["humidity"] for row in forecast] or [0]
    return {
        "count": len(forecast),
        "temp_min": min(temps),
        "temp_max": max(temps),
        "temp_avg": round(sum(temps) / len(temps), 1),
        "feels_avg": round(sum(feels) / len(feels), 1),
        "humidity_avg": round(sum(hums) / len(hums), 1),
    }

def export_forecast_csv(forecast: List[Dict[str, Any]], path: str) -> None:
    fieldnames = ["time_local", "temp_c", "feels_c", "humidity"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(forecast)