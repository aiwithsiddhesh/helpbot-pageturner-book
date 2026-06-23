import tomllib
from pathlib import Path

with open(Path(__file__).parent / "registry.toml", "rb") as f:
    INTENT_REGISTRY: dict = tomllib.load(f)
