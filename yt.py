from __future__ import annotations

import json
from abc import ABC, abstractmethod
from enum import IntEnum, auto
from typing import Any

import streamlit as st
from yt_dlp import YoutubeDL

from column import ColumnDict
from utils import dict_or


class MissingKeysError(ValueError):
    def __init__(self, *keys: str) -> None:
        self.keys = keys

    def __str__(self) -> str:
        return f"Missing keys from dictionary: {', '.join(self.keys)}"

class FormatType(IntEnum):
    AUDIO = auto()
    VIDEO = auto()
    AUDIO_VIDEO = auto()
    INVALID = auto()

class Format(ABC):
    """
    Base class for formats.

    Attributes:
    * bitrate       `float`
    * codec         `tuple[str, str]`
    * extension     `str`
    * format_id     `str`
    * format_note   `str`
    * fps           `int | None`
    * resolution    `str`
    """

    @staticmethod
    def check_missing_keys(d: dict[str, Any], *keys: str) -> None:
        """
        Raise `MissingKeysError` if D is missing any of *KEYS.
        """
        missing_keys: list[str] = []
        for key in keys:
            if key not in d:
                missing_keys.append(key)

        if missing_keys:
            raise MissingKeysError(*missing_keys)

    def __init__(self, d: dict[str, Any]) -> None:
        self.check_missing_keys(d, 'format', 'format_id')
        _, fn = dict_or(d, 'format_note', 'format')

        self.bitrate: float = float("nan")
        self.codec: tuple[str, str] = ("", "")
        self.extension: str = ""
        self.format_id: str = d['format_id']
        self.format_note: str = fn
        self.fps: int | None = None
        self.resolution: str = ""

    def as_dict(self) -> ColumnDict:
        ac, vc = self.codec
        return {
            'Bitrate': f"{round(self.bitrate):,}K",
            'Codec (A/V)': f"{ac}/{vc}",
            'Extension': self.extension,
            'FPS': self.fps,
            'ID': self.format_id,
            'Note': self.format_note,
            'Resolution': self.resolution,
        }

    @property
    @abstractmethod
    def type(self) -> FormatType:
        ...

    @staticmethod
    def from_dict(d: dict) -> Format:
        match d:
            case {'acodec': acodec, 'vcodec': None | "none", **_keys}:
                assert acodec not in (None, "none")
                return AudioFormat(d)

            case {'acodec': None | "none", 'vcodec': vcodec, **_keys}:
                assert vcodec not in (None, "none")
                return VideoFormat(d)

            case {'acodec': acodec, 'vcodec': vcodec, **_keys}:
                assert acodec not in (None, "none")
                assert vcodec not in (None, "none")
                return AudioVideoFormat(d)

        return InvalidFormat(d)

class AudioFormat(Format):
    def __init__(self, d: dict[str, Any]):
        self.check_missing_keys(d, "abr", "acodec", "audio_ext")
        super().__init__(d)
        self.bitrate = d['abr']
        self.codec = (d['acodec'], "")
        self.extension = d['audio_ext']

    @property
    def type(self) -> FormatType:
        return FormatType.AUDIO

class VideoFormat(Format):
    def __init__(self, d: dict[str, Any]):
        self.check_missing_keys(d, "vbr", "vcodec", "video_ext")
        super().__init__(d)
        self.bitrate = d['vbr']
        self.codec = ("", d['vcodec'])
        self.extension = d['video_ext']
        self.fps = d['fps']
        self.resolution = d['resolution']

    @property
    def type(self) -> FormatType:
        return FormatType.VIDEO

class AudioVideoFormat(AudioFormat, VideoFormat):
    def __init__(self, d: dict[str, Any]):
        self.check_missing_keys(d, "abr", "acodec", "vbr", "vcodec", "tbr")
        super().__init__(d)
        self.bitrate = d['tbr']
        self.codec = (d['acodec'], d['vcodec'])
        self.extension = d['ext']

class InvalidFormat(Format):
    @property
    def type(self) -> FormatType:
        return FormatType.INVALID

@st.cache_data
def extract_info(url: str) -> dict[str, Any]:
    """
    Extract the info dictionary for URL.

    Any errors will derive from YoutubeDLError.
    """
    options = {
        "quiet": True,
        "dump_single_json": True,
        "age_limit": 18,
    }

    with YoutubeDL(options) as ydl:
        info: dict | Any = YoutubeDL.sanitize_info(
            ydl.extract_info(url, download=False)
        )
        assert isinstance(info, dict)

    return info

@st.cache_data
def extract_info_from_file(_url: str) -> dict[str, Any]:
    with open("info.json") as fd:
        info: dict[str, Any] = json.load(fd)
        assert isinstance(info, dict)
        return info
