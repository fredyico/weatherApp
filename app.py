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
    parser.add_argument("--city", required=True, help="City name, e.g., 'Miramichi'")
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

    # Labels based on units
    temp_unit = "°C" if args.units == "metric" else "°F"
    speed_unit = "km/h" if args.units == "metric" else "mph"

    try:
        # ---- Current weather ----
        data = get_current_weather(args.city, api_key, units=args.units)

        # handle both new + old key names
        temp = data.get("temp", data.get("temp_c"))
        feels = data.get("feels", data.get("feels_c"))
        wind = data.get("wind_speed", data.get("wind_kmh"))

        print(
            f"{data['city']}: {data['description']}\n"
            f"Temp: {temp}{temp_unit} (feels {feels}{temp_unit})\n"
            f"Humidity: {data['humidity']}%  Pressure: {data['pressure']} hPa\n"
            f"Wind: {wind} {speed_unit}  Clouds: {data['cloud_pct']}%\n"
            f"Sunrise: {data['sunrise_local']}  Sunset: {data['sunset_local']}"
        )

        # ---- Forecast ----
        if args.forecast_hours > 0:
            forecast = get_forecast(args.city, api_key, hours=args.forecast_hours, units=args.units)
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

            if args.csv:
                export_forecast_csv(forecast, args.csv)
                print(f"\nCSV exported to: {args.csv}")

    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()