import json
from pathlib import Path
from typing import Dict, Any, Optional

CONFIG_DIR = Path.home() / '.ecsctl'
CONFIG_FILE = CONFIG_DIR / 'config.json'

class ClusterConfig:
    """Manages ECS cluster configuration."""
    
    def __init__(self):
        """Initialize configuration management."""
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        """Create config directory and file if they don't exist."""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self._save_config({'current-cluster': None})

    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def get_current_cluster(self) -> Optional[str]:
        """Get current cluster name."""
        config = self._load_config()
        return config.get('current-cluster')

    def set_current_cluster(self, cluster_name: str):
        """Set current cluster name."""
        config = self._load_config()
        config['current-cluster'] = cluster_name
        self._save_config(config)
  