import re
from pathlib import Path
from xml.etree import ElementTree

LEVELS_DIRECTORY = Path(__file__).parent.parent / "levels"


def _natural_sort_key(path):
    return tuple(
        (0, int(part)) if part.isdigit() else (1, part)
        for part in re.split(r"(\d+)", path.stem.lower())
    )


def _load_level(path):
    root = ElementTree.parse(path).getroot()
    width, height = int(root.attrib["width"]), int(root.attrib["height"])
    layer = root.find("./layer[@name='Bricks']")
    if layer is None:
        raise ValueError(f"{path} does not contain a Bricks layer")
    data = layer.find("data")
    if data is None or data.attrib.get("encoding") != "csv":
        raise ValueError(f"{path} has no CSV tile data")

    tile_ids = [int(value) for value in data.text.split(",") if value.strip()]
    if len(tile_ids) != width * height:
        raise ValueError(f"{path} has {len(tile_ids)} tiles; expected {width * height}")
    if any(tile_id not in range(15) for tile_id in tile_ids):
        raise ValueError(f"{path} contains an unsupported brick tile")

    return [
        [tile_id - 1 if tile_id else None for tile_id in tile_ids[row * width : (row + 1) * width]]
        for row in range(height)
    ]


LEVELS = tuple(
    _load_level(path)
    for path in sorted(LEVELS_DIRECTORY.glob("*.tmx"), key=_natural_sort_key)
)
