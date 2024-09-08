"""
This module handles the configuration for the Tenzing application.

It reads the configuration from a TOML file located at ~/.config/tenzing/config.toml.

Example ~/.config/tenzing/config.toml:

# Tenzing Configuration File

# List of Basecamp project IDs to track
project_ids = [
    "3668707",  # Project Alpha
    "3668708",  # Project Beta
    "3668709",  # Project Gamma
]

"""

import tomllib
from pathlib import Path
from typing import NamedTuple


class Config(NamedTuple):
    project_ids: list[str]


def read_config() -> Config:
    config_path = Path.home() / ".config" / "tenzing" / "config.toml"

    try:
        with open(config_path, "rb") as f:
            config_data = tomllib.load(f)
    except FileNotFoundError:
        print(f"Config file not found at {config_path}")
        return Config(project_ids=[])
    except tomllib.TOMLDecodeError:
        print(f"Error parsing config file at {config_path}")
        return Config(project_ids=[])

    project_ids = config_data.get("project_ids", [])
    return Config(project_ids=project_ids)
