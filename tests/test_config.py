from pathlib import Path

from scholaros.config import ConfigManager


def test_default_config():

    manager = ConfigManager()

    manager.load(Path("configs/default.toml"))

    assert manager.config.app_name == "ScholarOS"