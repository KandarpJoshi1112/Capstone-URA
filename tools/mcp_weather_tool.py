# tools/mcp_weather_tool.py
import time
import requests
from typing import Dict, Any, Optional
from utils.file_utils import read_json_file
from utils.logger import setup_logger

logger = setup_logger("mcp_weather_tool", None)

class WeatherToolError(Exception):
    pass

class MCPWeatherTool:
    """
    Unified weather tool:
      - demo: reads mock JSON
      - real: uses Open-Meteo geocoding + forecast (no API key required)
    """

    def __init__(self, config: Dict[str, Any], mode: str):
        self.mode = mode.lower()
        self.config = config
        if self.mode not in ("demo", "real"):
            raise WeatherToolError(f"Unsupported mode: {mode}")

        self.timeout = int(config.get("timeout_seconds", 8))
        self.max_retries = int(config.get("max_retries", 2))

        # Demo path validation
        self.demo_data_path = config.get("demo_data_path")
        if self.mode == "demo":
            if not self.demo_data_path:
                raise WeatherToolError("demo_data_path must be set for demo mode")

        # Real endpoints configuration (Open-Meteo)
        if self.mode == "real":
            self.geocode_endpoint = config.get("geocoding_endpoint")
            self.forecast_endpoint = config.get("forecast_endpoint")
            self.timezone = config.get("timezone", "UTC")
            self.units = config.get("units", "metric")
            if not self.geocode_endpoint or not self.forecast_endpoint:
                raise WeatherToolError("Missing Open-Meteo endpoints in config for real mode")

    def get_weather(self, location: str) -> Dict[str, Any]:
        if self.mode == "demo":
            return self._get_demo_weather(location)
        else:
            return self._get_real_weather(location)

    def _get_demo_weather(self, location: str) -> Dict[str, Any]:
        data = read_json_file(self.demo_data_path)
        data["queried_location"] = location
        data["source"] = "mock"
        logger.info("Returning mock weather data for location=%s", location)
        return data

    def _get_real_weather(self, location: str) -> Dict[str, Any]:
        """
        Steps:
          1) Geocode city -> lat/lon via Open-Meteo geocoding API
          2) Call forecast endpoint with current_weather=true
          3) Normalize and return structured result
        """
        # 1) Geocoding
        geocode_params = {"name": location, "count": 1}
        geocode_resp = self._request_with_retries(self.geocode_endpoint, params=geocode_params, desc="geocoding")
        # Validate geocoding response
        if not geocode_resp or "results" not in geocode_resp or not geocode_resp["results"]:
            raise WeatherToolError(f"Geocoding failed for location '{location}' - no results")

        geores = geocode_resp["results"][0]
        latitude = geores.get("latitude")
        longitude = geores.get("longitude")
        resolved_name = geores.get("name") or location
        country = geores.get("country")

        if latitude is None or longitude is None:
            raise WeatherToolError(f"Geocoding response missing coordinates for '{location}'")

        # 2) Forecast (current weather)
        forecast_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true",
            "timezone": self.timezone
        }
        forecast_resp = self._request_with_retries(self.forecast_endpoint, params=forecast_params, desc="forecast")
        if not forecast_resp or "current_weather" not in forecast_resp:
            raise WeatherToolError(f"Forecast API returned unexpected payload for {location}")

        cw = forecast_resp["current_weather"]
        # Try to extract humidity if hourly relative humidity is available; otherwise leave None
        humidity = None
        try:
            hourly = forecast_resp.get("hourly")
            if isinstance(hourly, dict):
                rh = hourly.get("relativehumidity_2m")
                # if list-like and same length as time, pick the first (closest hour)
                if isinstance(rh, list) and len(rh) > 0:
                    humidity = rh[0]
                elif isinstance(rh, (int, float)):
                    humidity = rh
        except Exception:
            humidity = None

        structured = {
            "location": f"{resolved_name}, {country}" if country else resolved_name,
            "timestamp": cw.get("time"),
            "weather": {
                "summary": self._map_weathercode_to_summary(cw.get("weathercode")),
                "temperature_c": cw.get("temperature"),
                "humidity": humidity,
                "wind_kmph": cw.get("windspeed")
            },
            "raw": {
                "geocoding": geores,
                "forecast": forecast_resp
            },
            "source": "real"
        }
        logger.info("Open-Meteo returned weather for %s (lat=%s lon=%s)", resolved_name, latitude, longitude)
        return structured

    def _request_with_retries(self, url: str, params: Optional[Dict[str, Any]] = None, desc: str = "request") -> Dict[str, Any]:
        last_exc = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info("Calling %s (attempt %d) url=%s params=%s", desc, attempt, url, params)
                resp = requests.get(url, params=params, timeout=self.timeout)
                if resp.status_code != 200:
                    logger.warning("%s responded with status %s: %s", desc, resp.status_code, resp.text)
                    raise WeatherToolError(f"{desc} status {resp.status_code}")
                payload = resp.json()
                return payload
            except Exception as e:
                logger.exception("Error during %s attempt %d: %s", desc, attempt, e)
                last_exc = e
                # exponential-ish backoff
                time.sleep(min(1 + attempt * 0.5, 5))
        raise WeatherToolError(f"All attempts for {desc} failed: {last_exc}")

    def _map_weathercode_to_summary(self, code: Optional[int]) -> str:
        """
        Minimal mapping of Open-Meteo weathercode to human summary.
        Reference: https://open-meteo.com/en/docs#api_form
        """
        mapping = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        try:
            if code is None:
                return "Unknown"
            return mapping.get(int(code), f"Weather code {code}")
        except Exception:
            return "Unknown"
