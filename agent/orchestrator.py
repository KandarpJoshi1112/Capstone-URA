# agent/orchestrator.py
import os
from typing import Any, Dict, Optional
from utils.logger import setup_logger
from utils.config_manager import ConfigManager, Settings
from agent.weather_agent import WeatherAgent

logger = setup_logger("orchestrator", None)

class Orchestrator:
    """
    Orchestrator: central controller. Loads config via ConfigManager.
    Coordinates agent operations, ensures mode is honored and logs runtime mode.
    """

    def __init__(self, config_path: str, cli_mode: Optional[str] = None):
        # callback when config changes
        def _on_change(settings: Settings):
            try:
                logger.info("Config reloaded. New mode=%s", settings.mode)
                # optionally re-init or re-wire agents if necessary
                self._apply_mode(settings.mode)
            except Exception as e:
                logger.exception("Error applying new config: %s", e)

        self.config_manager = ConfigManager(config_path, on_change=_on_change)
        # determine final mode with precedence CLI > ENV > config file
        resolved = self._resolve_mode(cli_mode)
        self._apply_mode(resolved)

    def _resolve_mode(self, cli_mode: Optional[str]) -> str:
        # CLI override
        if cli_mode:
            mode = cli_mode.lower()
            logger.info("Mode resolved from CLI: %s", mode)
        else:
            env_mode = os.getenv("URA_MODE")
            if env_mode:
                mode = env_mode.lower()
                logger.info("Mode resolved from ENV URA_MODE: %s", mode)
            else:
                mode = self.config_manager.settings.mode
                logger.info("Mode resolved from config file: %s", mode)

        if mode not in ("demo", "real"):
            raise ValueError("Invalid mode resolved: must be 'demo' or 'real'")
        return mode

    def _apply_mode(self, mode: str):
        # set current mode
        self.mode = mode
        # update logger file handler (recreate with file path)
        log_path = self.config_manager.settings.logging.get("path")
        # replace logger with file included
        setup_logger("ura", log_path, self.config_manager.settings.logging.get("level", "INFO"))

        # Initialize agent instances with the appropriate tool configs
        weather_cfg = self.config_manager.settings.weather.dict()
        self.weather_agent = WeatherAgent(weather_cfg, mode=self.mode)
        logger.info("Orchestrator applied mode=%s and initialized agents", self.mode)

    def fetch_weather(self, location: str) -> Dict[str, Any]:
        """
        API for other components to get weather. Always logs mode and where data came from.
        """
        logger.info("Orchestrator.fetch_weather invoked with mode=%s for location=%s", self.mode, location)
        result = self.weather_agent.fetch(location)
        logger.info("Orchestrator.fetch_weather result source=%s", result.get("source"))
        return result

    def stop(self):
        # stop config manager observer
        self.config_manager.stop()
