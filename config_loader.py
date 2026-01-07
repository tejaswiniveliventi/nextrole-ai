from pathlib import Path
import tomli


def load_config():
    config_path = Path(__file__).parent / "config.toml"

    if not config_path.exists():
        raise FileNotFoundError("config.toml not found at project root")

    with open(config_path, "rb") as f:
        return tomli.load(f)
