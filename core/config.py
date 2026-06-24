import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def load_config():
    config_path = BASE_DIR / 'config.yaml'
    if not config_path.exists():
        raise FileNotFoundError(
            "config.yaml doesn't exist in current directory"
        )
    with open(config_path) as f:
        config = yaml.safe_load(f)
        return config
