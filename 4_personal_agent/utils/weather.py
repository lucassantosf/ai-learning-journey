import requests

class Weather:
    BASE_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

    def __init__(self, user_agent="MyWeatherApp/1.0 lucas@email.com", default_lat=-23.4773222, default_lon=-47.5078991):
        self.user_agent = user_agent
        self.default_lat = default_lat
        self.default_lon = default_lon

    def get_forecast(self, lat=None, lon=None):
        lat = lat or self.default_lat
        lon = lon or self.default_lon

        headers = {
            "User-Agent": self.user_agent
        }
        params = {
            "lat": lat,
            "lon": lon,
        }
        resp = requests.get(self.BASE_URL, headers=headers, params=params)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"Error fetching forecast from met.no: {resp.text}")

    def process_forecast(self, forecast_json, hours=6):
        """Returns a friendly summary for the next `hours` forecast periods."""
        summary = []
        timeseries = forecast_json["properties"]["timeseries"][:hours]
        for entry in timeseries:
            time = entry["time"]
            details = entry["data"]["instant"]["details"]
            temp = details.get("air_temperature")

            # Try to get weather symbol for next hour (most detailed)
            symbol = "-"
            if "next_1_hours" in entry["data"]:
                symbol = entry["data"]["next_1_hours"]["summary"]["symbol_code"]
            elif "next_6_hours" in entry["data"]:
                symbol = entry["data"]["next_6_hours"]["summary"]["symbol_code"]
            elif "next_12_hours" in entry["data"]:
                symbol = entry["data"]["next_12_hours"]["summary"]["symbol_code"]

            # Format output line
            summary.append(f"{time}: {temp}°C, Weather: {symbol.replace('_', ' ').title()}")
        return "\n".join(summary)

# Example usage
if __name__ == "__main__":
    weather = Weather()

    forecast = weather.get_forecast()
    print("\n=== Processed Forecast ===")
    print(weather.process_forecast(forecast, hours=24))
