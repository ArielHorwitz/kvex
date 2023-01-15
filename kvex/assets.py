"""Assets utilities."""

from pathlib import Path


ASSETS_DIR = Path(__file__).parent / "assets"
"""Assets directory."""
assert ASSETS_DIR.is_dir()


ALL_ASSETS: dict[str, Path] = dict()

for file in ASSETS_DIR.iterdir():
    if not file.is_file() or file.suffix != ".png":
        continue
    ALL_ASSETS[file.stem] = file


IMAGES = tuple(ALL_ASSETS.keys())
"""Image names."""


def get_image(name: str, /) -> Path:
    """Get an image path by name."""
    return ALL_ASSETS[name]


__all__ = (
    "get_image",
    "IMAGES",
)
