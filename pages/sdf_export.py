"""Google Ads Editor CSV export page."""
import io
from datetime import date

import pandas as pd
import streamlit as st

# ── Constants ─────────────────────────────────────────────────────────────────

MARKET_LABELS = {
    'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'HR': 'Croatia',
    'CY': 'Cyprus', 'CZ': 'Czech Republic', 'DK': 'Denmark', 'EE': 'Estonia',
    'FI': 'Finland', 'FR': 'France', 'DE': 'Germany', 'GR': 'Greece',
    'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 'LV': 'Latvia',
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'MT': 'Malta', 'NL': 'Netherlands',
    'NO': 'Norway', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania',
    'SK': 'Slovakia', 'SI': 'Slovenia', 'ES': 'Spain', 'SE': 'Sweden',
    'CH': 'Switzerland', 'UK': 'United Kingdom',
}

MARKET_LANGUAGE = {
    'AT': 'German', 'BE': 'French', 'BG': 'Bulgarian', 'HR': 'Croatian',
    'CY': 'Greek', 'CZ': 'Czech', 'DK': 'Danish', 'EE': 'Estonian',
    'FI': 'Finnish', 'FR': 'French', 'DE': 'German', 'GR': 'Greek',
    'HU': 'Hungarian', 'IE': 'English', 'IT': 'Italian', 'LV': 'Latvian',
    'LT': 'Lithuanian', 'LU': 'French', 'MT': 'English', 'NL': 'Dutch',
    'NO': 'Norwegian', 'PL': 'Polish', 'PT': 'Portuguese', 'RO': 'Romanian',
    'SK': 'Slovak', 'SI': 'Slovenian', 'ES': 'Spanish', 'SE': 'Swedish',
    'CH': 'German', 'UK': 'English',
}

# Campaign type per channel (Google Ads Editor values)
GADS_TYPE = {'YouTube': 'Video', 'Search': 'Search'}

# Bid strategy per (channel, goal)
GADS_BID = {
    ('YouTube', 'Awareness'):  'Target CPM',
    ('YouTube', 'Traffic'):    'Maximize conversions',
    ('YouTube', 'Conversion'): 'Target CPA',
    ('Search',  'Awareness'):  'Manual CPC',
    ('Search',  'Traffic'):    'Maximize clicks',
    ('Search',  'Conversion'): 'Target CPA',
}

GADS_COLS = [
    'Campaign', 'Campaign Status', 'Campaign Type',
    'Budget', 'Budget Type',
    'Bid Strategy Type', 'Target CPA', 'Target CPM',
    'Start Date', 'End Date',
    'Location', 'Location Type',
    'Language', 'Language Type',
    'Ad Group', 'Ad Group Status', 'Default Max. CPC',
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _empty():
    return {c: '' for c in GADS_COLS}


def _reconstruct_plan(sid=0):
    """Pull plan config back from session state (set by the Media Plan page)."""
    ss = st.session_state
    campaign_name = ss.get('campaign_name', '')
    start_date    = ss.get('start_date')
    end_date      = ss.get('end_date')
    markets       = ss.get(f'selected_markets_{sid}', [])
    total_budget  = ss.get(f'total_budget_{sid}', 0)

    if not campaign_name or not start_date or not end_date or not markets:
        return None

    market_budgets = {
        mkt: total_budget * ss.get(f'pct_{mkt}_{sid}', 0) / 100
        for mkt in markets
    }

    goal_channels = {}
    for goal in ['Awareness', 'Traffic', 'Conversion']:
        if ss.get(f'sb_goal_{goal}_{sid}', False):
            chs = []
            if ss.get(f'sb_yt_{goal}_{sid}', False):  chs.append('YouTube')
            if ss.get(f'sb_s_{goal}_{sid}',  False):  chs.append('Search')
            if ss.get(f'sb_li_{goal}_{sid}', False):  chs.append('LinkedIn')
            if chs:
                goal_channels[goal] = chs

    if not goal_channels:
        return None

    return {
        'campaign_name':  campaign_name,
        'start_date':     start_date,
        'end_date':       end_date,
        'markets':        markets,
        'market_budgets': market_budgets,
        'goal_channels':  goal_channels,
        'total_budget':   total_budget,
    }


def _channel_budgets(mkt, goal, channels, mkt_budget, sid=0):
    """Reconstruct per-channel budget split from session state."""
    ss = st.session_state
    if len(channels) == 1:
        return {channels[0]: mkt_budget}
    if len(channels) == 2:
        pct_a = ss.get(f'split_{mkt}_{goal}_{sid}', 50)
        pct_b = 100 - pct_a
        return {channels[0]: mkt_budget * pct_a / 100,
                channels[1]: mkt_budget * pct_b / 100}
    pcts = {ch: ss.get(f'split_{mkt}_{goal}_{ch}_{sid}', 100 / len(channels))
            for ch in channels}
    total = sum(pcts.values()) or 1
    return {ch: mkt_budget * pcts[ch] / total for ch in channels}


def _build_gads_csv(plan, sid=0):
    ss   = st.session_state
    rows = []
    start  = plan['start_date']
    end    = plan['end_date']
    days   = max((end - start).days + 1, 1)
    s_date = start.strftime('%m/%d/%Y')
    e_date = end.strftime('%m/%d/%Y')

    for mkt in plan['markets']:
        mkt_budget = plan['market_budgets'][mkt]

        for goal, channels in plan['goal_channels'].items():
            gads_chs = [ch for ch in channels if ch in GADS_TYPE]
            if not gads_chs:
                continue

            ch_buds = _channel_budgets(mkt, goal, gads_chs, mkt_budget, sid)

            for ch in gads_chs:
                daily  = round(ch_buds[ch] / days, 2)
                name   = f'{plan["campaign_name"]}_{mkt}_{goal}_{ch}'
                ctype  = GADS_TYPE[ch]
                bid    = GADS_BID.get((ch, goal), 'Manual CPC')

                # Pull benchmark CPM/CPC from session state if available
                target_cpm = ss.get(f'cpm_{mkt}_{ch}_{goal}_{sid}', '') if ch == 'YouTube' else ''
                target_cpa = ''
                default_cpc = ss.get(f'cpc_{mkt}_{ch}_{goal}_{sid}', '') if ch == 'Search' else ''

                # 1 — Campaign row
                r = _empty()
                r['Campaign']          = name
                r['Campaign Status']   = 'Enabled'
                r['Campaign Type']     = ctype
                r['Budget']            = daily
                r['Budget Type']       = 'Daily'
                r['Bid Strategy Type'] = bid
                r['Target CPM']        = target_cpm
                r['Target CPA']        = target_cpa
                r['Start Date']        = s_date
                r['End Date']          = e_date
                rows.append(r)

                # 2 — Location row
                r = _empty()
                r['Campaign']      = name
                r['Location']      = MARKET_LABELS[mkt]
                r['Location Type'] = 'Location'
                rows.append(r)

                # 3 — Language row
                r = _empty()
                r['Campaign']      = name
                r['Language']      = MARKET_LANGUAGE.get(mkt, 'English')
                r['Language Type'] = 'Language'
                rows.append(r)

                # 4 — Ad group row
                r = _empty()
                r['Campaign']         = name
                r['Ad Group']         = f'{name}_AdGroup_01'
                r['Ad Group Status']  = 'Enabled'
                r['Default Max. CPC'] = default_cpc
                rows.append(r)

    df = pd.DataFrame(rows, columns=GADS_COLS)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode('utf-8')


def _preview_table(plan, sid=0):
    """Build a summary dataframe shown before download."""
    ss   = st.session_state
    days = max((plan['end_date'] - plan['start_date']).days + 1, 1)
    rows = []
    for mkt in plan['markets']:
        mkt_budget = plan['market_budgets'][mkt]
        for goal, channels in plan['goal_channels'].items():
            gads_chs = [ch for ch in channels if ch in GADS_TYPE]
            if not gads_chs:
                continue
            ch_buds = _channel_budgets(mkt, goal, gads_chs, mkt_budget, sid)
            for ch in gads_chs:
                daily = round(ch_buds[ch] / days, 2)
                rows.append({
                    'Campaign Name':   f'{plan["campaign_name"]}_{mkt}_{goal}_{ch}',
                    'Type':            GADS_TYPE[ch],
                    'Market':          MARKET_LABELS[mkt],
                    'Goal':            goal,
                    'Total Budget':    f'€{ch_buds[ch]:,.0f}',
                    'Daily Budget':    f'€{daily:,.2f}',
                    'Bid Strategy':    GADS_BID.get((ch, goal), 'Manual CPC'),
                })
    return pd.DataFrame(rows)


# ── Page UI ───────────────────────────────────────────────────────────────────

st.markdown(
    '<h2 style="margin:0 0 2px 0;font-family:Inter,sans-serif;font-size:1.5rem;color:#1A1A1A">'
    'Google Ads Export</h2>',
    unsafe_allow_html=True,
)
st.caption('Generate a Google Ads Editor CSV ready for bulk campaign upload.')
st.divider()

scenario_names = st.session_state.get('scenario_names', [])
if len(scenario_names) > 1:
    selected_scenario = st.selectbox('Scenario to export', scenario_names, key='sdf_scenario_pick')
    sid = scenario_names.index(selected_scenario)
else:
    sid = 0

plan = _reconstruct_plan(sid)

if plan is None:
    st.info(
        'No plan found in session. Build your plan on the **Media Plan** page first, '
        'then come back here to export — your settings carry over automatically.'
    )
    st.stop()

# ── Plan summary ──────────────────────────────────────────────────────────────
with st.expander('Plan summary', expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Campaign', plan['campaign_name'])
    c2.metric('Total Budget', f'€{plan["total_budget"]:,.0f}')
    c3.metric('Markets', len(plan['markets']))
    c4.metric('Flight', f'{(plan["end_date"] - plan["start_date"]).days + 1} days')

    st.caption(
        f'{plan["start_date"].strftime("%b %d, %Y")} – {plan["end_date"].strftime("%b %d, %Y")}  ·  '
        + '  |  '.join(f'{g}: {", ".join(chs)}' for g, chs in plan["goal_channels"].items())
    )

    linkedin_goals = [g for g, chs in plan['goal_channels'].items() if 'LinkedIn' in chs]
    if linkedin_goals:
        st.warning(
            f'LinkedIn is not supported in Google Ads Editor. '
            f'It will be excluded from the export ({", ".join(linkedin_goals)}).'
        )

# ── Campaign preview ──────────────────────────────────────────────────────────
st.markdown('#### Campaigns to be created')
preview_df = _preview_table(plan, sid)

if preview_df.empty:
    st.warning('No Google Ads compatible channels found (YouTube or Search required).')
    st.stop()

st.dataframe(preview_df, use_container_width=True, hide_index=True)
st.caption(
    f'{len(preview_df)} campaigns · one ad group each · '
    'geo and language targeting set per market · '
    'fill in creatives and audiences after import'
)

# ── Download ──────────────────────────────────────────────────────────────────
st.divider()
csv_bytes = _build_gads_csv(plan, sid)
st.download_button(
    label='⬇ Download Google Ads Editor CSV',
    data=csv_bytes,
    file_name=f'{plan["campaign_name"]}_google_ads_editor.csv',
    mime='text/csv',
    use_container_width=True,
)

st.markdown(
    '<div style="background:#f5f7f7;border-left:3px solid #2BB5A5;padding:10px 14px;'
    'border-radius:0 4px 4px 0;font-size:0.85rem;margin-top:8px">'
    '<strong>How to import:</strong> Open Google Ads Editor → File → Import → '
    'Import CSV → select this file → Review changes → Apply.'
    '<br><strong>What to complete after import:</strong> ad creatives, audience targeting, '
    'and Target CPA / Target CPM values where applicable.'
    '</div>',
    unsafe_allow_html=True,
)
