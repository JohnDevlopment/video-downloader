from __future__ import annotations

import json
import time
from enum import Enum
from itertools import chain, filterfalse
from typing import Any, TypedDict, cast

import pandas as pd
import streamlit as st
from yt_dlp.utils import ExtractorError

from utils import dict_or, subst_none
import yt


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

@st.fragment
def extract_info(url: str):
    """
    Fragment run when the process-button is clicked.

    * This is a fragment.
    * This sets state key `info_dict`.
    """
    st.session_state.info_dict = None

    info = None
    try:
        # Extract info dictionary with a nifty spinner
        with st.spinner("Extracting info from URL..."):
            time.sleep(1)
            info = yt.extract_info_from_file(url)
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
    video_only: list[yt.Format] = []
    audio_only: list[yt.Format] = []
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
        fmt = yt.Format.from_dict(fmt)
        if fmt.type == yt.FormatType.AUDIO:
            audio_only.append(fmt)

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
