from __future__ import annotations

import json
import time
from enum import Enum
from functools import partial
from itertools import chain, filterfalse
from typing import Any, TypeAlias, TypedDict, cast

import pandas as pd
import streamlit as st
from icecream import ic
from yt_dlp import YoutubeDL
from yt_dlp.utils import ExtractorError


class Column(str, Enum):
    ID = "ID"
    EXTENSION = "Extension"
    RESOLUTION = "Resolution"
    FPS = "FPS"
    NOTE = "Note"
    BITRATE = "Bitrate"
    CODEC = "Codec (A/V)"

ColumnDict = TypedDict('ColumnDict', {
    'ID': str,
    'Extension': str,
    'Resolution': str,
    'FPS': int | None,
    'Note': str,
    'Bitrate': int | None,
    'Codec (A/V)': str,
})

URL = "https://www.youtube.com/watch?v=MNruRgXGFdk"

if 'info_dict' not in st.session_state:
    st.session_state.info_dict = None

st.title("Video Downloader")

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

def dict_or(d: dict, *keys: Any, default: Any=None) -> tuple[Any, Any]:
    for key in keys:
        if key in d:
            return (key, d[key])
    return (None, default)

@st.fragment
def extract_info(url: str):
    """
    Fragment run when the process-button is clicked.

    * This is a fragment.
    * This sets state key "info_dict".
    """
    st.session_state.info_dict = None

    info = None
    try:
        # Extract info dictionary with a nifty spinner
        with st.spinner("Extracting info from URL..."):
            time.sleep(1)
            info = yt_extract_info(url)
    except ExtractorError as e:
        st.error(f"Failed to extract info: {e}")
        return

    # Type checker stuff
    assert isinstance(info, dict)
    info = cast(dict[str, Any], info)

    if st.session_state.is_raw_json:
        st.code(json.dumps(info))

    process_info_dict(info)

    # This is effectively the return value
    st.session_state.info_dict = info

def not_zero(*args: int, check_none=False) -> bool:
    """
    Return true if all arguments are not zero.
    """
    if check_none:
        values = map(lambda x: x != 0 and x is not None, args)
    else:
        values = map(lambda x: x != 0, args)
    return all(values)

not_zero_or_none = partial(not_zero, check_none=True)

def subst_none(val: Any | None, alt: Any) -> Any:
    """
    Return VAL unless it is None, otherwise return ALT.
    """
    return alt if val is None else val

def process_info_dict(info: dict[str, Any]):
    df = pd.DataFrame({
        Column.ID: [],
        Column.EXTENSION: [],
        Column.RESOLUTION: [],
        Column.FPS: [],
        Column.BITRATE: [],
        Column.NOTE: [],
        Column.CODEC: [],
    })
    video_only: list[ColumnDict] = []
    audio_only: list[ColumnDict] = []
    audio_video: list[ColumnDict] = []

    # Set type of each row
    df[Column.ID] = df[Column.ID].astype(str)
    df[Column.EXTENSION] = df[Column.EXTENSION].astype(str)
    df[Column.RESOLUTION] = df[Column.RESOLUTION].astype(str)
    df[Column.NOTE] = df[Column.NOTE].astype(str)
    df[Column.FPS] = df[Column.FPS].astype(pd.Int8Dtype())
    df[Column.BITRATE] = df[Column.BITRATE].astype(pd.Float32Dtype())
    df[Column.CODEC] = df[Column.CODEC].astype(str)

    def _filter(x: dict[str, Any]):
        # Used to filter out unwanted items
        fn = subst_none(x.get('format_note'), "<undefined>")

        return (
            subst_none(x['protocol'], "<undefined>") == "mhtml" or
            fn.lower() == "storyboard"
        )

    it = filterfalse(_filter, info['formats'])
    for i, fmt in enumerate(it):
        key, fn = dict_or(fmt, 'format', 'format_note')
        match fmt:
            case {'abr': 0, 'vbr': vbr,
                  'format_id': fid,
                  'video_ext': ext,
                  'resolution': res,
                  'fps': fps,
                  'acodec': None | "none", 'vcodec': vc,
                  **_other}:
                # Video only
                video_only.append({
                    'ID': fid,
                    'Extension': ext,
                    'Resolution': res,
                    'FPS': fps,
                    'Bitrate': vbr,
                    'Note': fn,
                    'Codec (A/V)': f"/{vc}",
                })

            case {'abr': abr, 'vbr': 0,
                  'format_id': fid,
                  'audio_ext': ext,
                  'acodec': ac, 'vcodec': None | "none",
                  **_other}:
                # Audio only
                audio_only.append({
                    'ID': fid,
                    'Extension': ext,
                    'Resolution': "",
                    'FPS': None,
                    'Bitrate': abr,
                    'Note': fn,
                    'Codec (A/V)': f"{ac}/",
                })

    for i, fmt in enumerate(chain(audio_only, video_only, audio_video)):
        df.loc[i] = fmt

    st.dataframe(df)

col1, col2 = st.columns([2, 1])

with col1:
    url = st.text_input("URL:", value=URL)

with col2:
    st.session_state.is_raw_json = st.checkbox("Print Raw JSON")
    process = st.button("Process")

if process:
    extract_info(url)

# col1, col2 = st.columns([2, 1])
