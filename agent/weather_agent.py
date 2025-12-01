# agent/weather_agent.py
from typing import Dict, Any
from tools.mcp_weather_tool import MCPWeatherTool, WeatherToolError
from utils.logger import setup_logger

logger = setup_logger("weather_agent", None)

class WeatherAgent:
    """
    WeatherAgent: high-level agent that decides whether to call mock or real tool,
    validate results, and return a stable structure for orchestrator.
    """

    def __init__(self, tool_config: Dict[str, Any], mode: str):
        self.mode = mode.lower()
        self.tool = MCPWeatherTool(tool_config, mode=self.mode)
        logger.info("WeatherAgent initialized in mode=%s", self.mode)

    def fetch(self, location: str) -> Dict[str, Any]:
        """
        Fetch weather with error handling and normalized output.
        """
        try:
            resp = self.tool.get_weather(location)
            # Normalize response (ensure keys exist)
            normalized = {
                "location": resp.get("location") or location,
                "timestamp": resp.get("timestamp"),
                "summary": resp.get("weather", {}).get("summary"),
                "temperature_c": resp.get("weather", {}).get("temperature_c"),
                "humidity": resp.get("weather", {}).get("humidity"),
                "wind_kmph": resp.get("weather", {}).get("wind_kmph"),
                "source": resp.get("source", "unknown"),
                "raw": resp.get("raw")
            }
            logger.info("WeatherAgent.fetch returned source=%s for location=%s", normalized["source"], location)
            return normalized
        except WeatherToolError as e:
            logger.error("WeatherAgent failed to fetch weather: %s", e)
            # In demo mode, we might want to surface error differently; here we re-raise to orchestrator
            raise
        except Exception as e:
            logger.exception("Unexpected error in WeatherAgent.fetch: %s", e)
            raise
