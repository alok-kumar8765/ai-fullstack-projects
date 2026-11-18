import json
from pathlib import Path
from typing import Any, Dict
from utils.logger import setup_logger

logger = setup_logger("SettingsManager")

class SettingsManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                logger.info("Configuration successfully loaded from %s", self.config_path)
            except Exception as e:
                logger.error("Failed to load config file: %s. Using defaults.", e)
                self.config = self._default_config()
        else:
            self.config = self._default_config()
            self.save_config()

    def save_config(self) -> None:
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error("Failed to save configuration: %s", e)

    def get(self, section: str, key: str, default: Any = None) -> Any:
        return self.config.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any) -> None:
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

    def _default_config(self) -> Dict[str, Any]:
        return {
            "camera": {"camera_index": 0, "inference_interval_sec": 0.8, "target_fps": 30},
            "emotion": {"confidence_threshold": 0.65, "debounce_duration_sec": 4.0, "rolling_window_size": 10, "default_mode": "mood_matching"},
            "audio": {"volume": 0.7, "fade_ms": 1000, "music_directory": "music"},
            "privacy": {"save_snapshots": False, "local_logging_only": True},
            "spotify": {"client_id": "", "client_secret": "", "redirect_uri": "http://localhost:8888/callback"}
        }