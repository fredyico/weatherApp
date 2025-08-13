import os
import argparse
from dotenv import load_dotenv
from weather import (
    get_current_weather,
    get_forecast,
    summarize_forecast,
    export_forecast_csv,
)

def print_forecast_table(rows):
    # fixed-width columns: Time | Temp | Feels | Humidity
    print("\nForecast (3h steps):")
    print(f"{'Time':<17} {'Temp(°C)':>8} {'Feels(°C)':>10} {'Humidity(%)':>12}")
    print("-" * 50)
    for r in rows:
        print(f"{r['time_local']:<17} {r['temp_c']:>8} {r['feels_c']:>10} {r['humidity']:>12}")

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Weather CLI")
    parser.add_argument("--city", required=True, help="City name, e.g., 'Miramichi'")
    parser.add_argument("--forecast-hours", type=int, default=24,
                        help="Hours ahead to include in forecast (multiple of 3). Default 24.")
    parser.add_argument("--csv", help="Optional path to export forecast CSV, e.g., forecast.csv") 
    args = parser.parse_args()
    #remember to erase the hardcode key. Test porpuse only.   
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        print("Missing OPENWEATHER_API_KEY in your environment or .env file. Set it and try again.")
        return
    try:
        # Current weather
        data = get_current_weather(args.city, api_key)
        print(
            f"{data['city']}: {data['description']}\n"
            f"Temp: {data['temp_c']} °C (feels {data['feels_c']} °C)\n"
            f"Humidity: {data['humidity']} % Pressure: {data['pressure']} hPa\n"
            f"Wind: {data['wind_kmh']} km/h Clouds: {data['cloud_pct']} %\n"
            f"Sunrise: {data['sunrise_local']} Sunset: {data['sunset_local']}\n"
        )
        
        # Forecast
        if args.forecast_hours > 0:
            forecast = get_forecast(args.city, api_key, hours=args.forecast_hours)
            print_forecast_table(forecast)
            summary = summarize_forecast(forecast)
            print(
                f"\nSummary next {args.forecast_hours}h "
                f"(~{summary['count']} pts): "
                f"min {summary['temp_min']}°C, max {summary['temp_max']}°C, "
                f"avg {summary['temp_avg']}°C (feels {summary['feels_avg']}°C), "
                f"humidity avg {summary['humidity_avg']}%"
            )
            if args.csv:
                export_forecast_csv(forecast, args.csv)
                print(f"\nCSV exported to: {args.csv}")        
    except ValueError as e:
        print(f"Error: {e}")
        
if __name__ == '__main__':
    main()