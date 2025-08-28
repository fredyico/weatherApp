# app.py
import os
import argparse
from dotenv import load_dotenv
from weather import (
    get_current_weather,
    get_forecast,
    summarize_forecast,
    export_forecast_csv,
)

def print_multi_city_table(rows, temp_unit: str, speed_unit: str):
    # rows: list of dicts with keys: city, temp, feels, humidity, wind_speed, cloud_pct, description
    headers = [
        ("City", 16),
        (f"Temp({temp_unit})", 12),
        (f"Feels({temp_unit})", 13),
        ("Humidity(%)", 12),
        (f"Wind({speed_unit})", 14),
        ("Clouds(%)", 12),
        ("Description", 20),
    ]
    # header
    line = " ".join([f"{h[0]:<{h[1]}}" for h in headers])
    print("\nCurrent Conditions (multi-city):")
    print(line)
    print("-" * len(line))
    # rows
    for r in rows:
        cells = [
            f"{r['city']:<16}",
            f"{str(r['temp']):<12}",
            f"{str(r['feels']):<13}",
            f"{str(r['humidity']):<12}",
            f"{str(r['wind_speed']):<14}",
            f"{str(r['cloud_pct']):<12}",
            f"{r['description']:<20}",
        ]
        print(" ".join(cells))

def print_forecast_table(rows, temp_unit: str):
    # fixed-width columns: Time | Temp | Feels | Humidity
    print("\nForecast (3h steps):")
    print(f"{'Time':<17} {('Temp(' + temp_unit + ')'):>10} {('Feels(' + temp_unit + ')'):>12} {'Humidity(%)':>12}")
    print("-" * 55)
    for r in rows:
        # support either new keys (temp/feels) or old (temp_c/feels_c)
        t = r.get("temp", r.get("temp_c"))
        f = r.get("feels", r.get("feels_c"))
        h = r.get("humidity", 0)
        print(f"{r['time_local']:<17} {str(t):>10} {str(f):>12} {str(h):>12}")

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Weather CLI")
    parser.add_argument("--city", nargs="+", required=True,
                        help="One or more city names, e.g., --city Miramichi Halifax Toronto")
    parser.add_argument("--compare", action="store_true", default=False,
                        help="Show a side-by-side table for current conditions across all cities.")
    parser.add_argument("--forecast-hours", type=int, default=24,
                        help="Hours ahead to include in forecast (multiple of 3). Default 24.")
    parser.add_argument("--csv", help="Optional path to export forecast CSV, e.g., forecast.csv")
    parser.add_argument("--units", choices=["metric", "imperial"], default="metric",
                        help="Units: 'metric' (°C, km/h) or 'imperial' (°F, mph). Default: metric")
    args = parser.parse_args()

    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        print("Missing OPENWEATHER_API_KEY in your environment or .env file.")
        return

    temp_unit = "°C" if args.units == "metric" else "°F"
    speed_unit = "km/h" if args.units == "metric" else "mph"

    # ----------------------------
    # 1) Fetch current weather for all cities
    rows = []
    for city in args.city:
        try:
            cur = get_current_weather(city, api_key, units=args.units)
            rows.append({
                "city": cur["city"],
                "temp": cur.get("temp", cur.get("temp_c")),
                "feels": cur.get("feels", cur.get("feels_c")),
                "humidity": cur["humidity"],
                "wind_speed": cur.get("wind_speed", cur.get("wind_kmh")),
                "cloud_pct": cur["cloud_pct"],
                "description": cur["description"],
            })
        except ValueError as e:
            rows.append({
                "city": city, "temp": "-", "feels": "-", "humidity": "-",
                "wind_speed": "-", "cloud_pct": "-", "description": f"Error: {e}",
            })

    # ----------------------------
    # 2) Print current conditions
    if args.compare:
        print_multi_city_table(rows, temp_unit, speed_unit)
    else:
        for r in rows:
            print("\n" + "=" * 40)
            if r["temp"] == "-":
                print(f"{r['city']}: {r['description']}")
                continue
            print(
                f"{r['city']}: {r['description']}\n"
                f"Temp: {r['temp']}{temp_unit} (feels {r['feels']}{temp_unit})\n"
                f"Humidity: {r['humidity']}%  \n"
                f"Wind: {r['wind_speed']} {speed_unit}  Clouds: {r['cloud_pct']}%"
            )

    # ----------------------------
    # 3) Forecast per city (optional)
    if args.forecast_hours > 0:
        for city in args.city:
            try:
                forecast = get_forecast(city, api_key, hours=args.forecast_hours, units=args.units)
                print(f"\n----- Forecast for {city} -----")
                print_forecast_table(forecast, temp_unit)
                summary = summarize_forecast(forecast)
                print(
                    f"\nSummary next {args.forecast_hours}h "
                    f"(~{summary['count']} pts): "
                    f"min {summary['temp_min']}{temp_unit}, "
                    f"max {summary['temp_max']}{temp_unit}, "
                    f"avg {summary['temp_avg']}{temp_unit} "
                    f"(feels {summary['feels_avg']}{temp_unit}), "
                    f"humidity avg {summary['humidity_avg']}%"
                )
            except ValueError as e:
                print(f"\nError fetching forecast for {city}: {e}")


if __name__ == "__main__":
    main()