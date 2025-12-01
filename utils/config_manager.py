# utils/config_manager.py
import os
import json
import threading
from typing import Dict, Any, Callable, Optional
from pydantic import BaseModel, Field, validator
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

# Allowed modes
ALLOWED_MODES = {"demo", "real"}

class WeatherConfig(BaseModel):
    """
    Flexible WeatherConfig supporting:
     - OpenWeatherMap style: real_endpoint + real_api_key_env
     - Open-Meteo style: geocoding_endpoint + forecast_endpoint
     - demo_data_path always optional but recommended for demo.
    Fields are optional here so Settings can be parsed even if only one style is present.
    Individual tools should perform stricter runtime validation depending on the selected mode.
    """
    # OpenWeatherMap-style (optional)
    real_endpoint: Optional[str] = None
    real_api_key_env: Optional[str] = None

    # Open-Meteo-style (optional)
    geocoding_endpoint: Optional[str] = None
    forecast_endpoint: Optional[str] = None

    # Common
    demo_data_path: Optional[str] = None
    timeout_seconds: int = 8
    max_retries: int = 2

class Settings(BaseModel):
    mode: str = Field("demo", description="Execution mode: demo or real")
    weather: WeatherConfig
    logging: Dict[str, Any] = {"level": "INFO", "path": "logs/app.log"}

    @validator("mode")
    def mode_must_be_valid(cls, v):
        if not v:
            raise ValueError("mode must be set")
        vv = v.lower()
        if vv not in ALLOWED_MODES:
            raise ValueError(f"mode must be one of {ALLOWED_MODES}")
        return vv

class ConfigManager:
    def __init__(self, path: str, on_change: Optional[Callable[[Settings], None]] = None):
        self.path = path
        self.on_change = on_change
        self._lock = threading.RLock()
        # load settings (tolerate BOM)
        self.settings: Settings = self._load()
        self._observer: Optional[Observer] = None
        # Start watcher for hot-reload
        self._start_watcher()

    def _load(self) -> Settings:
        """
        Load JSON using utf-8-sig to handle BOM if present.
        Returns a Settings instance (does not enforce mode-specific runtime constraints here).
        """
        p = Path(self.path)
        if not p.exists():
            raise FileNotFoundError(f"Config file not found at {self.path}")
        with p.open("r", encoding="utf-8-sig") as f:
            raw = json.load(f)
        return Settings(**raw)

    def reload(self) -> Settings:
        with self._lock:
            new_settings = self._load()
            self.settings = new_settings
            if self.on_change:
                try:
                    self.on_change(new_settings)
                except Exception:
                    # caller should handle exceptions; keep reload robust
                    pass
            return new_settings

    def _start_watcher(self):
        # Watch the config file's parent directory and reload on modifications of that exact file
        class _Handler(FileSystemEventHandler):
            def __init__(self, outer):
                self.outer = outer
            def on_modified(self, event):
                try:
                    src = Path(event.src_path).resolve()
                    target = Path(self.outer.path).resolve()
                    if src == target:
                        try:
                            self.outer.reload()
                        except Exception:
                            pass
                except Exception:
                    pass

        observer = Observer()
        handler = _Handler(self)
        observe_path = str(Path(self.path).parent or ".")
        observer.schedule(handler, path=observe_path, recursive=False)
        observer.daemon = True
        observer.start()
        self._observer = observer

    def stop(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()
