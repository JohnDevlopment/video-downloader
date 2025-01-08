from __future__ import annotations

from enum import Enum
from typing import TypedDict


class Column(str, Enum):
    ID = "ID"
    EXTENSION = "Extension"
    RESOLUTION = "Resolution"
    FPS = "FPS"
    BITRATE = "Bitrate"
    CODEC = "Codec (A/V)"
    NOTE = "Note"

ColumnDict = TypedDict(
    "ColumnDict",
    {
        "Bitrate": str,
        "Codec (A/V)": str,
        "Extension": str,
        "FPS": int | None,
        "ID": str,
        "Note": str,
        "Resolution": str,
    }
)
