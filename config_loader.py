from pathlib import Path
import tomli
import logging

logger = logging.getLogger(__name__)


def load_config():
    config_path = Path(__file__).parent / "config.toml"
    logger.debug(f"Loading config from {config_path}")

    if not config_path.exists():
        logger.exception("config.toml not found at project root")
        raise FileNotFoundError("config.toml not found at project root")

    with open(config_path, "rb") as f:
        conf = tomli.load(f)
        logger.info("Configuration loaded successfully")
        return conf
