"""NMQ Media Plan Generator — entry point and navigation."""
import json
from datetime import date

import streamlit as st

st.set_page_config(
    page_title='NMQ Media Plan Generator',
    page_icon='https://nmqdigital.com/hs-fs/hubfs/raw_assets/public/NMQ-Digital/images/NMQ_Green_Logo.png',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .block-container { padding-top: 1.2rem; }

    h3 { color: #2BB5A5; }

    div.stButton > button[kind="primary"],
    div.stButton > button {
        background-color: #2BB5A5;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        transition: background 0.2s;
    }
    div.stButton > button:hover {
        background-color: #229990;
        color: white;
    }

    div.stDownloadButton > button {
        background-color: #1A1A1A;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        transition: background 0.2s;
    }
    div.stDownloadButton > button:hover {
        background-color: #2BB5A5;
        color: white;
    }

    div[data-testid="stMetric"] label { font-size: 0.75rem; }

    .nmq-sidebar-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
    .nmq-sidebar-logo img { height: 32px; }
</style>
""", unsafe_allow_html=True)

# Apply pending plan load before any widgets render
if '_pending_load' in st.session_state:
    _load_data = st.session_state.pop('_pending_load')
    for k, v in _load_data.items():
        if isinstance(v, dict) and '__date__' in v:
            st.session_state[k] = date.fromisoformat(v['__date__'])
        else:
            st.session_state[k] = v

st.logo(
    'https://nmqdigital.com/hs-fs/hubfs/raw_assets/public/NMQ-Digital/images/NMQ_Green_Logo.png',
    link='https://nmqdigital.com',
    size='large',
)

with st.sidebar:
    st.markdown(
        '<p style="margin:0 0 4px 0;font-weight:700;font-size:0.95rem;color:#1A1A1A">'
        'Media Plan Generator</p>',
        unsafe_allow_html=True,
    )
    st.markdown('---')

pg = st.navigation({
    'NMQ Tools': [
        st.Page('pages/media_plan.py', title='Media Plan', icon='📋'),
        st.Page('pages/sdf_export.py', title='Google Ads Export', icon='⬇'),
    ]
})
pg.run()
