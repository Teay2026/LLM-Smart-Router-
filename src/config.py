import yaml
from pathlib import Path
from typing import Dict, List, Any


class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    @property
    def models(self) -> Dict[str, Dict[str, Any]]:
        return self._config.get('models', {})

    @property
    def routing_keywords(self) -> Dict[str, List[str]]:
        return self._config.get('routing', {}).get('keywords', {})

    @property
    def fallback_model(self) -> str:
        return self._config.get('routing', {}).get('fallback_model', 'llama3.2-1b-fast')

    @property
    def timeout_seconds(self) -> int:
        return self._config.get('routing', {}).get('timeout_seconds', 30)

    @property
    def max_retries(self) -> int:
        return self._config.get('routing', {}).get('max_retries', 2)

    @property
    def metrics_port(self) -> int:
        return self._config.get('metrics', {}).get('port', 9090)