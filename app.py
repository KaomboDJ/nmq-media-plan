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

    .block-container { padding-top: 3.5rem; }

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

    /* Force sidebar logo large — target every possible container */
    div[data-testid="stSidebarHeader"] { min-height: 80px !important; padding: 10px 16px !important; }
    div[data-testid="stSidebarHeader"] a { display: block !important; }
    div[data-testid="stSidebarHeader"] img,
    div[data-testid="stSidebarHeader"] a img,
    [data-testid="stLogo"],
    [data-testid="stLogo"] img {
        height: 60px !important;
        max-height: 60px !important;
        min-height: 60px !important;
        width: auto !important;
        max-width: 200px !important;
        object-fit: contain !important;
    }
</style>
""", unsafe_allow_html=True)

# Apply pending plan load before any widgets render
_LOAD_SKIP = {
    '_pending_load', 'FormSubmitter', '_uploader_v',
    'dup_', 'remove_', 'tpl_apply_', 'grp_', 'eq_', 'cpm_eff_',
    'pin_', 'dl_gads_', 'dl_excel', 'btn_', 'preset_',
}
if '_pending_load' in st.session_state:
    _load_data = st.session_state.pop('_pending_load')
    for k, v in _load_data.items():
        if any(k.startswith(s) for s in _LOAD_SKIP):
            continue
        if isinstance(v, dict) and '__date__' in v:
            st.session_state[k] = date.fromisoformat(v['__date__'])
        else:
            st.session_state[k] = v

st.logo(
    'https://nmqdigital.com/hs-fs/hubfs/raw_assets/public/NMQ-Digital/images/NMQ_Green_Logo.png',
    link='https://nmqdigital.com',
    size='large',
)

pg = st.navigation({
    'NMQ Tools': [
        st.Page('pages/media_plan.py', title='Media Plan', icon='📋'),
        st.Page('pages/sdf_export.py', title='Google Ads Export', icon='⬇'),
        st.Page('pages/kpi_matrix.py', title='KPI Matrix', icon='📊'),
    ]
})
pg.run()
