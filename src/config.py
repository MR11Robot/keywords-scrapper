# config.py

import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


COUNTRIES_CONFIG_PATH = os.getenv("COUNTRIES_CONFIG", (BASE_DIR / "countries.json"))


def load_countries(config_path: str = COUNTRIES_CONFIG_PATH) -> list[dict]:
    """
    Load countries configuration from a JSON file.

    Args:
        config_path: Path to the JSON file containing countries config.

    Returns:
        List of country dicts with keys: name, code, homepage, inside, bottom.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        ValueError: If the JSON structure is invalid.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Countries config file not found: '{config_path}'\n"
            f"Please create the file or set the COUNTRIES_CONFIG env variable."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("countries.json must contain a JSON array of country objects.")

    required_keys = {"name", "code", "homepage", "inside", "bottom"}
    for i, country in enumerate(data):
        missing = required_keys - country.keys()
        if missing:
            raise ValueError(
                f"Country at index {i} is missing required fields: {missing}"
            )

    return data