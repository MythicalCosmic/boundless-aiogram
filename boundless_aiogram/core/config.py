import yaml
from pathlib import Path
from typing import Optional


def load_config(project_root: str) -> Optional[dict]:
    config_path = Path(project_root) / ".boundless.yml"
    if not config_path.exists():
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f) or {}
