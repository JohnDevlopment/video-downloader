from __future__ import annotations

import json
from abc import ABC, abstractmethod
from enum import IntEnum, auto
from typing import Any, cast

import streamlit as st

from utils import dict_or


class FormatType(IntEnum):
    AUDIO = auto()
    VIDEO = auto()
    AUDIO_VIDEO = auto()

class Format(ABC):
    def __init__(self, d: dict[str, Any]):
        match d:
            case {'format_id': fid, **keys}:
                self.format_id = cast(str, fid)
                _, fn = dict_or(keys, 'format', 'format_note')
                self.format_note = cast(str, fn)

            case _:
                # TODO: aaaa
                raise ValueError("Dict missing one or more of: ", d)

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

        raise ValueError("Incorrect dictionary structure")

class AudioFormat(Format):
    def __init__(self, d: dict[str, Any]):
        pass

    @property
    def type(self) -> FormatType:
        return FormatType.AUDIO

class VideoFormat(Format):
    def __init__(self, d: dict[str, Any]):
        pass

class AudioVideoFormat(AudioFormat, VideoFormat):
    def __init__(self, d: dict[str, Any]):
        pass

# @st.cache_data
# def yt_extract_info(url: str) -> dict[str, Any]:
#     """
#     Extract the info dictionary for URL.

#     Any errors will derive from YoutubeDLError.
#     """
#     options = {
#         "quiet": True,
#         "dump_single_json": True,
#         "age_limit": 18,
#     }

#     with YoutubeDL(options) as ydl:
#         info: dict | Any = YoutubeDL.sanitize_info(
#             ydl.extract_info(url, download=False)
#         )
#         assert isinstance(info, dict)

#     return info

@st.cache_data
def extract_info(_url: str) -> dict[str, Any]:
    with open("info.json") as fd:
        info: dict[str, Any] = json.load(fd)
        assert isinstance(info, dict)
        return info
