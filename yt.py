from __future__ import annotations

import streamlit as st

@st.cache_data
def yt_extract_info(url: str) -> dict[str, Any]:
    with open("info.json") as fd:
        return json.load(fd)
