"""Assets utilities."""

from pathlib import Path


ASSETS_DIR = Path(__file__).parent / "assets"
"""Assets directory."""
assert ASSETS_DIR.is_dir()


ALL_ASSETS: dict[str, Path] = dict()
"""All assets by name."""

for file in ASSETS_DIR.iterdir():
    if not file.is_file() or file.suffix != ".png":
        continue
    ALL_ASSETS[file.stem] = file


def get_image(name: str, /) -> Path:
    """Get an image path by name."""
    return ALL_ASSETS[name]
