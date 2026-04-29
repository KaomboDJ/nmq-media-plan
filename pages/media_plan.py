"""Media Plan page."""
import calendar
import io
import json
import os
from datetime import date, timedelta

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import toml

# ── Constants ─────────────────────────────────────────────────────────────────

MARKET_LABELS = {
    'AT': 'Austria',
    'BE': 'Belgium',
    'BG': 'Bulgaria',
    'HR': 'Croatia',
    'CY': 'Cyprus',
    'CZ': 'Czech Republic',
    'DK': 'Denmark',
    'EE': 'Estonia',
    'FI': 'Finland',
    'FR': 'France',
    'DE': 'Germany',
    'GR': 'Greece',
    'HU': 'Hungary',
    'IE': 'Ireland',
    'IT': 'Italy',
    'LV': 'Latvia',
    'LT': 'Lithuania',
    'LU': 'Luxembourg',
    'MT': 'Malta',
    'NL': 'Netherlands',
    'NO': 'Norway',
    'PL': 'Poland',
    'PT': 'Portugal',
    'RO': 'Romania',
    'SK': 'Slovakia',
    'SI': 'Slovenia',
    'ES': 'Spain',
    'SE': 'Sweden',
    'CH': 'Switzerland',
    'UK': 'United Kingdom',
}

# Default benchmark values — markets with known data have specific values,
# others fall back to regional averages (Western EU vs Eastern EU).
# CPM YouTube | CPM LinkedIn | View Rate | CTR YT | CTR LI | Frequency
# CPC Search  | CTR Search   | Click→Session | Conv Rate

def _default_bench(cpm_yt, cpm_li, view_rate, ctr_yt, ctr_li, freq,
                   cpc_s, ctr_s, c2s_yt=0.80, c2s_li=0.82, c2s_s=0.86, cr=0.02):
    return {
        'YouTube':  {'cpm': cpm_yt, 'view_rate': view_rate, 'ctr': ctr_yt,  'frequency': freq, 'click_to_session': c2s_yt, 'conv_rate': cr},
        'LinkedIn': {'cpm': cpm_li, 'ctr': ctr_li,  'frequency': freq, 'click_to_session': c2s_li, 'conv_rate': cr},
        'Search':   {'cpc': cpc_s,  'ctr': ctr_s,   'click_to_session': c2s_s, 'conv_rate': cr},
    }

BENCH = {
    'AT': _default_bench(11.0, 18.0, 0.31, 0.0035, 0.0038, 3.0, 2.30, 0.030),
    'BE': _default_bench(11.0, 17.0, 0.31, 0.0035, 0.0038, 3.0, 2.20, 0.030),
    'BG': _default_bench(3.5,  7.0,  0.30, 0.0028, 0.0032, 3.0, 0.70, 0.022),
    'HR': _default_bench(4.5,  9.0,  0.30, 0.0030, 0.0033, 3.0, 0.90, 0.023),
    'CY': _default_bench(7.0, 13.0,  0.30, 0.0030, 0.0035, 3.0, 1.50, 0.026),
    'CZ': _default_bench(5.0,  9.5,  0.30, 0.0030, 0.0033, 3.0, 1.00, 0.024),
    'DK': _default_bench(13.0, 21.0, 0.31, 0.0035, 0.0040, 3.0, 2.80, 0.032),
    'EE': _default_bench(4.5,  9.0,  0.30, 0.0030, 0.0033, 3.0, 0.90, 0.023),
    'FI': _default_bench(12.0, 19.0, 0.31, 0.0035, 0.0038, 3.0, 2.50, 0.030),
    'FR': _default_bench(10.0, 17.0, 0.31, 0.0033, 0.0038, 3.0, 2.00, 0.028),
    'DE': _default_bench(11.0, 18.0, 0.31, 0.0035, 0.0038, 3.0, 2.20, 0.030),
    'GR': _default_bench(5.0,  10.0, 0.30, 0.0028, 0.0032, 3.0, 1.00, 0.024),
    'HU': _default_bench(4.0,  8.0,  0.30, 0.0028, 0.0032, 3.0, 0.80, 0.022),
    'IE': _default_bench(12.0, 19.0, 0.31, 0.0035, 0.0040, 3.0, 2.50, 0.032),
    'IT': _default_bench(8.0,  14.0, 0.30, 0.0030, 0.0035, 3.0, 1.60, 0.026),
    'LV': _default_bench(4.5,  9.0,  0.30, 0.0030, 0.0033, 3.0, 0.90, 0.023),
    'LT': _default_bench(4.5,  9.0,  0.30, 0.0030, 0.0033, 3.0, 0.90, 0.023),
    'LU': _default_bench(12.0, 18.0, 0.31, 0.0035, 0.0038, 3.0, 2.40, 0.030),
    'MT': _default_bench(7.0,  13.0, 0.30, 0.0030, 0.0035, 3.0, 1.40, 0.025),
    'NL': _default_bench(10.0, 16.0, 0.31, 0.0035, 0.0040, 3.0, 2.00, 0.030),
    'NO': _default_bench(13.0, 22.0, 0.31, 0.0035, 0.0040, 3.0, 2.80, 0.032),
    'PL': _default_bench( 5.0,  9.0, 0.30, 0.0030, 0.0035, 3.0, 1.00, 0.025),
    'PT': _default_bench( 6.0, 11.0, 0.30, 0.0030, 0.0035, 3.0, 1.20, 0.025),
    'RO': _default_bench( 3.5,  7.0, 0.30, 0.0028, 0.0032, 3.0, 0.70, 0.022),
    'SK': _default_bench( 4.5,  9.0, 0.30, 0.0030, 0.0033, 3.0, 0.90, 0.023),
    'SI': _default_bench( 5.0, 10.0, 0.30, 0.0030, 0.0033, 3.0, 1.00, 0.024),
    'ES': _default_bench( 6.0, 12.0, 0.30, 0.0030, 0.0035, 3.0, 1.50, 0.025),
    'SE': _default_bench(12.0, 20.0, 0.31, 0.0035, 0.0040, 3.0, 2.60, 0.031),
    'CH': _default_bench(13.0, 21.0, 0.31, 0.0035, 0.0040, 3.0, 2.90, 0.032),
    'UK': _default_bench(12.0, 20.0, 0.31, 0.0035, 0.0040, 3.0, 2.50, 0.035),
}

CH_COLORS = {
    'YouTube':  ['#1F497D', '#437CA3', '#6B9FBF', '#9FC3D5', '#C5DCE8'],
    'LinkedIn': ['#1F6152', '#2E8A72', '#4DB896', '#7DCFB0', '#A8E4D0'],
    'Search':   ['#4285F4', '#5A95F5', '#74A5F6', '#8EB5F7', '#A8C5F8'],
}

ALL_GOALS = ['Awareness', 'Traffic', 'Conversion']

ADDITIVE = ['Budget', 'impressions', 'reach', 'views', 'clicks', 'sessions', 'conversions']

COL_FMT = {
    'Budget':           ('Budget (€)',     lambda x: f'€{x:,.0f}'),
    'impressions':      ('Impressions',    lambda x: f'{int(round(x)):,}'),
    'reach':            ('Reach',          lambda x: f'{int(round(x)):,}'),
    'views':            ('Views',          lambda x: f'{int(round(x)):,}'),
    'clicks':           ('Clicks',         lambda x: f'{int(round(x)):,}'),
    'sessions':         ('Sessions',       lambda x: f'{int(round(x)):,}'),
    'conversions':      ('Conversions',    lambda x: f'{int(round(x)):,}'),
    'view_rate':        ('View Rate',      lambda x: f'{x*100:.1f}%'),
    'ctr':              ('CTR',            lambda x: f'{x*100:.2f}%'),
    'click_to_session': ('Click→Session',  lambda x: f'{x*100:.0f}%'),
    'cpv':              ('CPV (€)',         lambda x: f'€{x:.2f}'),
    'cpc':              ('CPC (€)',         lambda x: f'€{x:.2f}'),
    'cpa':              ('CPA (€)',         lambda x: f'€{x:.2f}'),
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def generate_periods(start, end, breakdown):
    periods, cur = [], start
    if breakdown == 'Daily':
        while cur <= end:
            periods.append({'label': cur.strftime('%b %d, %Y'), 'days': 1})
            cur += timedelta(days=1)
    elif breakdown == 'Weekly':
        while cur <= end:
            p_end = min(cur + timedelta(days=6), end)
            periods.append({'label': f"{cur.strftime('%b %d')} – {p_end.strftime('%b %d')}", 'days': (p_end - cur).days + 1})
            cur += timedelta(days=7)
    elif breakdown == 'Bi-Weekly':
        while cur <= end:
            p_end = min(cur + timedelta(days=13), end)
            periods.append({'label': f"{cur.strftime('%b %d')} – {p_end.strftime('%b %d')}", 'days': (p_end - cur).days + 1})
            cur += timedelta(days=14)
    elif breakdown == 'Monthly':
        while cur <= end:
            last = calendar.monthrange(cur.year, cur.month)[1]
            p_end = min(date(cur.year, cur.month, last), end)
            periods.append({'label': cur.strftime('%B %Y'), 'days': (p_end - cur).days + 1})
            cur = date(cur.year + 1, 1, 1) if cur.month == 12 else date(cur.year, cur.month + 1, 1)
    return periods


def calc_row(budget, bm, goal, channel, conv_rate):
    if budget <= 0:
        return {'Budget': budget}
    r = {'Budget': budget}

    if channel == 'Search':
        cpc = bm.get('cpc', 2.0)
        ctr = bm.get('ctr', 0.03)
        c2s = bm.get('click_to_session', 0.85)
        if cpc <= 0:
            return r
        clicks = budget / cpc
        impressions = clicks / ctr if ctr > 0 else 0
        r.update({'impressions': impressions, 'clicks': clicks, 'cpc': cpc})
        if goal in ('Traffic', 'Conversion'):
            r['sessions'] = clicks * c2s
        if goal == 'Conversion':
            convs = r['sessions'] * conv_rate
            r['conversions'] = convs
            r['cpa'] = budget / convs if convs > 0 else 0

    else:
        cpm = bm.get('cpm', 10.0)
        ctr = bm.get('ctr', 0.003)
        freq = bm.get('frequency', 3.0)
        c2s = bm.get('click_to_session', 0.80)
        if cpm <= 0:
            return r
        imp = (budget / cpm) * 1000
        reach = imp / freq if freq > 0 else 0
        clicks = imp * ctr
        r.update({
            'impressions': imp,
            'reach': reach,
            'clicks': clicks,
            'cpc': budget / clicks if clicks > 0 else 0,
        })
        if goal == 'Awareness' and channel == 'YouTube':
            vr = bm.get('view_rate', 0.31)
            views = imp * vr
            r['views'] = views
            r['cpv'] = budget / views if views > 0 else 0
        if goal in ('Traffic', 'Conversion'):
            r['sessions'] = clicks * c2s
        if goal == 'Conversion':
            convs = r['sessions'] * conv_rate
            r['conversions'] = convs
            r['cpa'] = budget / convs if convs > 0 else 0

    return r


def build_table(periods, total_budget, bm, goal, channel, conv_rate):
    total_days = sum(p['days'] for p in periods) or 1
    rows = []
    for p in periods:
        bud = total_budget * p['days'] / total_days
        m = calc_row(bud, bm, goal, channel, conv_rate)
        rows.append({'Period': p['label'], 'Days': p['days'], **m})
    df = pd.DataFrame(rows)
    total_m = calc_row(total_budget, bm, goal, channel, conv_rate)
    total_df = pd.DataFrame([{'Period': 'TOTAL', 'Days': total_days, **total_m}])
    return pd.concat([df, total_df], ignore_index=True)


def fmt_df(df):
    out = df[['Period', 'Days']].copy()
    for raw, (label, fn) in COL_FMT.items():
        if raw in df.columns:
            out[label] = df[raw].apply(fn)
    return out


def make_funnel(df, goal, channel, title):
    t = df[df['Period'] == 'TOTAL'].iloc[0]
    colors = CH_COLORS.get(channel, CH_COLORS['YouTube'])

    if channel == 'Search':
        if goal == 'Awareness':
            stages = [('Impressions', 'impressions'), ('Clicks', 'clicks')]
        elif goal == 'Traffic':
            stages = [('Impressions', 'impressions'), ('Clicks', 'clicks'), ('Sessions', 'sessions')]
        else:
            stages = [('Impressions', 'impressions'), ('Clicks', 'clicks'), ('Sessions', 'sessions'), ('Conversions', 'conversions')]
    elif channel == 'YouTube':
        if goal == 'Awareness':
            stages = [('Impressions', 'impressions'), ('Reach', 'reach'), ('Views', 'views'), ('Clicks', 'clicks')]
        elif goal == 'Traffic':
            stages = [('Impressions', 'impressions'), ('Clicks', 'clicks'), ('Sessions', 'sessions')]
        else:
            stages = [('Impressions', 'impressions'), ('Clicks', 'clicks'), ('Sessions', 'sessions'), ('Conversions', 'conversions')]
    else:  # LinkedIn
        if goal == 'Awareness':
            stages = [('Impressions', 'impressions'), ('Reach', 'reach'), ('Clicks', 'clicks')]
        elif goal == 'Traffic':
            stages = [('Impressions', 'impressions'), ('Clicks', 'clicks'), ('Sessions', 'sessions')]
        else:
            stages = [('Impressions', 'impressions'), ('Clicks', 'clicks'), ('Sessions', 'sessions'), ('Conversions', 'conversions')]

    labels = [s[0] for s in stages]
    values = [t.get(s[1], 0) for s in stages]

    fig = go.Figure(go.Funnel(
        y=labels,
        x=values,
        textinfo='value+percent initial',
        marker={'color': colors[:len(stages)]},
        textfont={'size': 10},
        connector={'line': {'color': 'rgba(0,0,0,0.1)', 'width': 1}},
    ))
    fig.update_layout(
        title={'text': title, 'font': {'size': 12, 'color': '#1F497D'}, 'x': 0.5, 'xanchor': 'center'},
        margin={'t': 40, 'b': 10, 'l': 10, 'r': 10},
        height=265,
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def benchmark_inputs(ch, mkt, goal, sid=0):
    """Render benchmark inputs for one channel/market/goal. Returns a benchmark dict."""
    b = BENCH[mkt][ch]

    fields = []
    if ch == 'Search':
        fields = [
            ('cpc',   'CPC (€)',    b['cpc'],                                0.10, '%.2f', False),
            ('ctr',   'CTR %',      b['ctr'] * 100,                          0.5,  '%.1f', True),
        ]
        if goal in ('Traffic', 'Conversion'):
            fields.append(('click_to_session', 'Click→Session %', b.get('click_to_session', 0.85) * 100, 1.0, '%.0f', True))
        if goal == 'Conversion':
            fields.append(('conv_rate', 'Conv. Rate %', b.get('conv_rate', 0.03) * 100, 0.1, '%.1f', True))

    elif ch == 'YouTube':
        fields = [('cpm', 'CPM (€)', b['cpm'], 0.5, '%.2f', False)]
        if goal == 'Awareness':
            fields.append(('view_rate', 'View Rate %', b.get('view_rate', 0.31) * 100, 0.5, '%.1f', True))
        fields += [
            ('ctr',       'CTR %',     b['ctr'] * 100,          0.01, '%.2f', True),
            ('frequency', 'Frequency', b.get('frequency', 3.0), 0.5,  '%.1f', False),
        ]
        if goal in ('Traffic', 'Conversion'):
            fields.append(('click_to_session', 'Click→Session %', b.get('click_to_session', 0.80) * 100, 1.0, '%.0f', True))
        if goal == 'Conversion':
            fields.append(('conv_rate', 'Conv. Rate %', b.get('conv_rate', 0.02) * 100, 0.1, '%.1f', True))

    else:  # LinkedIn
        fields = [
            ('cpm',       'CPM (€)',   b['cpm'],                0.5,  '%.2f', False),
            ('ctr',       'CTR %',     b['ctr'] * 100,          0.01, '%.2f', True),
            ('frequency', 'Frequency', b.get('frequency', 3.0), 0.5,  '%.1f', False),
        ]
        if goal in ('Traffic', 'Conversion'):
            fields.append(('click_to_session', 'Click→Session %', b.get('click_to_session', 0.82) * 100, 1.0, '%.0f', True))
        if goal == 'Conversion':
            fields.append(('conv_rate', 'Conv. Rate %', b.get('conv_rate', 0.02) * 100, 0.1, '%.1f', True))

    cols = st.columns(len(fields))
    raw = {}
    for i, (key, label, default, step, fmt, _) in enumerate(fields):
        raw[key] = cols[i].number_input(label, value=float(default), step=step, format=fmt,
                                        key=f'{key}_{mkt}_{ch}_{goal}_{sid}')

    bm = {}
    for key, _, _, _, _, is_pct in fields:
        bm[key] = raw[key] / 100.0 if is_pct else raw[key]

    # Carry over non-editable defaults
    if ch == 'YouTube' and goal != 'Awareness':
        bm['view_rate'] = b.get('view_rate', 0.31)
    if ch in ('YouTube', 'LinkedIn') and 'frequency' not in bm:
        bm['frequency'] = b.get('frequency', 3.0)
    if 'click_to_session' not in bm:
        bm['click_to_session'] = b.get('click_to_session', 0.80)
    if 'conv_rate' not in bm:
        bm['conv_rate'] = b.get('conv_rate', 0.02)

    return bm


def _channel_budget_split(mkt, goal, goal_chs, mkt_budget, sid=0):
    """Render per-channel budget split for one market/goal pair. Returns {ch: budget}."""
    if len(goal_chs) == 1:
        return {goal_chs[0]: mkt_budget}

    st.markdown('**Channel budget split**')

    if len(goal_chs) == 2:
        ch_a, ch_b = goal_chs
        pct_a = st.slider(
            f'{ch_a}  ←——→  {ch_b}',
            min_value=0, max_value=100, value=50, step=5,
            key=f'split_{mkt}_{goal}_{sid}',
            format='%d%%',
        )
        pct_b = 100 - pct_a
        bud_a = mkt_budget * pct_a / 100
        bud_b = mkt_budget * pct_b / 100
        # Show the resulting amounts side by side
        ca, cb = st.columns(2)
        ca.metric(ch_a, f'€{bud_a:,.0f}', f'{pct_a}%')
        cb.metric(ch_b, f'€{bud_b:,.0f}', f'{pct_b}%')
        return {ch_a: bud_a, ch_b: bud_b}

    # 3 channels: individual % inputs that should sum to 100
    default_pct = round(100 / len(goal_chs), 1)
    pcts = {}
    cols = st.columns(len(goal_chs))
    for i, ch in enumerate(goal_chs):
        pcts[ch] = cols[i].number_input(
            f'{ch} %', min_value=0.0, max_value=100.0,
            value=default_pct, step=5.0, format='%.0f',
            key=f'split_{mkt}_{goal}_{ch}_{sid}'
        )
    pct_sum = sum(pcts.values())
    ch_budgets = {ch: mkt_budget * pcts[ch] / pct_sum for ch in goal_chs} if pct_sum > 0 else {ch: 0 for ch in goal_chs}
    if abs(pct_sum - 100) > 0.5:
        st.caption(f'Percentages sum to {pct_sum:.0f}% — normalising proportionally.')
    amt_cols = st.columns(len(goal_chs))
    for i, ch in enumerate(goal_chs):
        amt_cols[i].metric(ch, f'€{ch_budgets[ch]:,.0f}')
    return ch_budgets


def render_goal_section(mkt, goal, selected_channels, ch_budgets, periods, grand_totals, sid=0):
    """Render benchmarks + table + funnel for one market/goal combo."""
    bm_all = {}
    with st.expander('Edit benchmarks', expanded=True):
        for ch in selected_channels:
            st.markdown(f'**{ch}**')
            bm_all[ch] = benchmark_inputs(ch, mkt, goal, sid)

    for ch in selected_channels:
        bm = bm_all[ch]
        ch_bud = ch_budgets[ch]
        conv_rate = bm.get('conv_rate', 0.02)

        df = build_table(periods, ch_bud, bm, goal, ch, conv_rate)

        col_t, col_f = st.columns([3, 2])
        with col_t:
            st.markdown(f'**{ch}** — €{ch_bud:,.0f}')
            st.dataframe(fmt_df(df), use_container_width=True, hide_index=True)
        with col_f:
            st.plotly_chart(
                make_funnel(df, goal, ch, f'{mkt} — {ch}'),
                use_container_width=True,
                config={'displayModeBar': False},
                key=f'funnel_{mkt}_{ch}_{goal}_{sid}',
            )

        t_row = df[df['Period'] == 'TOTAL'].copy()
        t_row['Market'] = MARKET_LABELS[mkt]
        grand_totals[goal][ch].append(t_row)


# ── Save / Load helpers ───────────────────────────────────────────────────────

_SKIP_KEYS = {'_pending_load', 'FormSubmitter'}

def _serialise_state():
    data = {'scenario_names': st.session_state.get('scenario_names', ['Scenario 1'])}
    for k, v in st.session_state.items():
        if any(k.startswith(s) for s in _SKIP_KEYS):
            continue
        if isinstance(v, date):
            data[k] = {'__date__': v.isoformat()}
        elif isinstance(v, (str, int, float, bool, list)):
            data[k] = v
    return json.dumps(data, indent=2).encode('utf-8')


# ── Excel builder ─────────────────────────────────────────────────────────────

_NMQ_TEAL   = '2BB5A5'
_NMQ_BLACK  = '1A1A1A'
_NMQ_LIGHT  = 'F5F7F7'

def _xl_header(ws, row_num):
    fill = PatternFill('solid', fgColor=_NMQ_TEAL)
    font = Font(bold=True, color='FFFFFF', name='Calibri')
    for cell in ws[row_num]:
        if cell.value is not None:
            cell.fill = fill
            cell.font = font
            cell.alignment = Alignment(horizontal='center')


def _build_excel(s, campaign_name, start_date, end_date, audience_type, industry):
    wb = openpyxl.Workbook()

    # ── Config sheet ──────────────────────────────────────────────────────────
    ws_cfg = wb.active
    ws_cfg.title = 'Config'
    cfg_rows = [
        ('Campaign Name', campaign_name),
        ('Scenario', s['name']),
        ('Audience Type', audience_type),
        ('Industry', industry),
        ('Start Date', start_date.strftime('%b %d, %Y')),
        ('End Date', end_date.strftime('%b %d, %Y')),
        ('Total Budget (€)', s['grand_total_bud']),
        ('', ''),
        ('Market', 'Budget (€)', 'Share (%)'),
    ]
    for row in cfg_rows:
        ws_cfg.append(list(row))
    _xl_header(ws_cfg, 9)
    for mkt in s['selected_markets']:
        ws_cfg.append([MARKET_LABELS[mkt], round(s['market_budgets'][mkt], 2), round(s['market_pcts'][mkt], 1)])
    ws_cfg.column_dimensions['A'].width = 26
    ws_cfg.column_dimensions['B'].width = 20
    ws_cfg.column_dimensions['C'].width = 14

    # ── KPI Summary sheet ─────────────────────────────────────────────────────
    ws_sum = wb.create_sheet('KPI Summary')
    sum_headers = ['Goal', 'Channel'] + [COL_FMT[c][0] for c in ADDITIVE if c in COL_FMT]
    ws_sum.append(sum_headers)
    _xl_header(ws_sum, 1)
    for goal, chs in s['grand_totals'].items():
        for ch, rows in chs.items():
            if not rows:
                continue
            gdf = pd.concat(rows, ignore_index=True)
            row = [goal, ch]
            for col in ADDITIVE:
                row.append(round(gdf[col].sum(), 0) if col in gdf.columns else 0)
            ws_sum.append(row)
    for i, col in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'], 1):
        ws_sum.column_dimensions[col].width = 18

    # ── Per goal+channel sheets ───────────────────────────────────────────────
    for goal, chs in s['grand_totals'].items():
        for ch, rows in chs.items():
            if not rows:
                continue
            gdf = pd.concat(rows, ignore_index=True)
            sheet_name = f'{goal[:9]}_{ch[:7]}'[:31]
            ws = wb.create_sheet(sheet_name)
            raw_cols = ['Market', 'Period', 'Days'] + [c for c in ADDITIVE if c in gdf.columns]
            display_cols = ['Market', 'Period', 'Days'] + [COL_FMT[c][0] for c in ADDITIVE if c in gdf.columns]
            ws.append(display_cols)
            _xl_header(ws, 1)
            for _, r in gdf[raw_cols].iterrows():
                ws.append([round(r[c], 0) if isinstance(r.get(c), float) else r.get(c, '') for c in raw_cols])
            ws.column_dimensions['A'].width = 20
            ws.column_dimensions['B'].width = 20
            for col_letter in ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
                ws.column_dimensions[col_letter].width = 16

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# ── Step label helper ─────────────────────────────────────────────────────────
def _step(n, label):
    return (
        f'<p style="margin:6px 0 2px 0;font-weight:600;font-size:0.88rem;color:#1A1A1A">'
        f'<span style="background:#2BB5A5;color:white;border-radius:50%;'
        f'width:18px;height:18px;display:inline-flex;align-items:center;justify-content:center;'
        f'font-size:0.68rem;font-weight:700;margin-right:6px;flex-shrink:0">{n}</span>'
        f'{label}</p>'
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(_step(1, 'Campaign Name'), unsafe_allow_html=True)
    campaign_name = st.text_input('Campaign Name', value='Campaign — 2026',
                                  key='campaign_name', label_visibility='collapsed')

    st.markdown(_step(2, 'Audience Type'), unsafe_allow_html=True)
    audience_type = st.radio('Audience', ['B2B', 'B2C'], horizontal=True,
                             label_visibility='collapsed', key='audience_type')

    st.markdown(_step(3, 'Industry'), unsafe_allow_html=True)
    INDUSTRIES_SB = [
        'Logistics, Supply Chain & Transportation',
        'Industrial, Manufacturing & Materials',
        'Enterprise SaaS, Technology & Platforms',
        'Financial Services, Fintech & Insurance',
        'Healthcare, Pharma & Life Sciences',
        'Consumer Brands & Retail',
        'Mobility, Travel & Automotive',
        'Information Services & Professional Platforms',
    ]
    industry = st.selectbox('Industry', INDUSTRIES_SB, label_visibility='collapsed', key='industry')

    st.markdown('---')
    st.markdown(_step(4, 'Flight Dates'), unsafe_allow_html=True)
    col_s, col_e = st.columns(2)
    start_date = col_s.date_input('Start', value=date(2026, 5, 12), key='start_date')
    end_date   = col_e.date_input('End',   value=date(2026, 6, 29), key='end_date')

    if end_date <= start_date:
        st.error('End must be after Start.')
        st.stop()

    st.caption(f'{(end_date - start_date).days + 1} days total')

    st.markdown(_step(5, 'Period Breakdown'), unsafe_allow_html=True)
    breakdown = st.selectbox('Breakdown', ['Daily', 'Weekly', 'Bi-Weekly', 'Monthly'],
                             index=1, label_visibility='collapsed', key='breakdown')

    st.markdown('---')
    st.markdown(_step(6, 'Goals & Channels'), unsafe_allow_html=True)
    st.caption('Tick which channels apply to each goal.')
    hc = st.columns([2, 1, 1, 1])
    hc[1].markdown('<small>YT</small>', unsafe_allow_html=True)
    hc[2].markdown('<small>Search</small>', unsafe_allow_html=True)
    hc[3].markdown('<small>LinkedIn</small>', unsafe_allow_html=True)

    goal_channels = {}
    for goal_key in ['Awareness', 'Traffic', 'Conversion']:
        rc = st.columns([2, 1, 1, 1])
        goal_on = rc[0].checkbox(goal_key, value=False, key=f'sb_goal_{goal_key}')
        yt_on = rc[1].checkbox('YT', value=False, key=f'sb_yt_{goal_key}', label_visibility='collapsed', disabled=not goal_on)
        s_on  = rc[2].checkbox('S',  value=False, key=f'sb_s_{goal_key}',  label_visibility='collapsed', disabled=not goal_on)
        li_on = rc[3].checkbox('LI', value=False, key=f'sb_li_{goal_key}', label_visibility='collapsed', disabled=not goal_on)
        if goal_on:
            chs = [ch for ch, on in [('YouTube', yt_on), ('Search', s_on), ('LinkedIn', li_on)] if on]
            if chs:
                goal_channels[goal_key] = chs

    if not goal_channels:
        st.warning('Select at least one goal + channel.')
        st.stop()

    selected_goals = list(goal_channels.keys())

    # ── Save / Load ───────────────────────────────────────────────────────────
    st.markdown('---')
    st.markdown('**💾 Save / Load Plan**')
    st.download_button(
        label='Download plan (.json)',
        data=_serialise_state(),
        file_name=f'{campaign_name.replace(" ", "_")}_plan.json',
        mime='application/json',
        use_container_width=True,
    )
    uploaded = st.file_uploader('Load plan (.json)', type='json', label_visibility='collapsed')
    if uploaded is not None:
        try:
            payload = json.loads(uploaded.read().decode('utf-8'))
            st.session_state['_pending_load'] = payload
            st.rerun()
        except Exception as e:
            st.error(f'Could not load plan: {e}')


# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown(
    f'<h2 style="margin:0 0 2px 0;font-family:Inter,sans-serif;font-size:1.5rem;color:#1A1A1A">'
    f'{campaign_name}</h2>',
    unsafe_allow_html=True,
)
st.caption(f'{start_date.strftime("%b %d, %Y")} – {end_date.strftime("%b %d, %Y")}  ·  {breakdown}  ·  {audience_type}  ·  {industry}')
st.divider()

# Scenario management via session state
if 'scenario_names' not in st.session_state:
    st.session_state.scenario_names = ['Scenario 1']

add_col, _ = st.columns([1, 6])
if add_col.button('＋ Add Scenario'):
    n = len(st.session_state.scenario_names) + 1
    st.session_state.scenario_names.append(f'Scenario {n}')

periods = generate_periods(start_date, end_date, breakdown)

_has_compare = len(st.session_state.scenario_names) >= 2
_tab_labels = (['⚖ Compare'] if _has_compare else []) + st.session_state.scenario_names
_all_tabs = st.tabs(_tab_labels)
compare_tab = _all_tabs[0] if _has_compare else None
scenario_tabs = _all_tabs[1:] if _has_compare else _all_tabs
all_scenarios_data = []  # collected for AI section and Compare tab


def _render_scenario(sid):
    """Render per-scenario config (markets, budget, split) then tables and funnels."""

    # ── Per-scenario config ───────────────────────────────────────────────────
    cfg1, cfg2 = st.columns([4, 1])
    with cfg1:
        st.markdown('**Markets**')
        s_markets = st.multiselect(
            'Markets', list(MARKET_LABELS.keys()), default=[],
            format_func=lambda k: f'{k} — {MARKET_LABELS[k]}',
            label_visibility='collapsed',
            key=f'selected_markets_{sid}',
        )
    with cfg2:
        st.markdown('**Total Budget (€)**')
        s_budget = st.number_input(
            'Budget', min_value=0, value=0, step=500,
            label_visibility='collapsed', key=f'total_budget_{sid}'
        )

    s_market_budgets, s_market_pcts = {}, {}
    if s_markets:
        n_mkts = len(s_markets)
        default_pct = round(100.0 / n_mkts, 1)
        st.markdown('**Market Split (%)**')
        per_row = min(n_mkts, 4)
        for row_start in range(0, n_mkts, per_row):
            row_mkts = s_markets[row_start:row_start + per_row]
            row_cols = st.columns(len(row_mkts) * 2)
            for i, mkt in enumerate(row_mkts):
                pct = row_cols[i * 2].number_input(
                    f'{mkt}', min_value=0.0, max_value=100.0,
                    value=default_pct, step=0.5, format='%.1f',
                    key=f'pct_{mkt}_{sid}'
                )
                s_market_pcts[mkt] = pct
                s_market_budgets[mkt] = s_budget * pct / 100
                row_cols[i * 2 + 1].metric(mkt, f'€{s_market_budgets[mkt]:,.0f}')
        pct_sum = sum(s_market_pcts.values())
        if abs(pct_sum - 100) > 0.5:
            st.warning(f'Split: {pct_sum:.1f}% — adjust to 100%')
        else:
            st.success(f'✓ €{s_budget:,} allocated')
    else:
        st.info('Select at least one market above to build the plan.')
        return None

    if not goal_channels:
        st.info('Enable at least one goal and channel in the sidebar.')
        return None

    st.divider()

    # ── Plan tables ───────────────────────────────────────────────────────────
    grand_totals = {g: {ch: [] for ch in chs} for g, chs in goal_channels.items()}

    for mkt in s_markets:
        mkt_budget = s_market_budgets[mkt]
        st.subheader(MARKET_LABELS[mkt])

        if len(selected_goals) > 1:
            goal_tabs = st.tabs(selected_goals)
            for tab, goal in zip(goal_tabs, selected_goals):
                with tab:
                    goal_chs = goal_channels[goal]
                    ch_budgets = _channel_budget_split(mkt, goal, goal_chs, mkt_budget, sid)
                    render_goal_section(mkt, goal, goal_chs, ch_budgets, periods, grand_totals, sid)
        else:
            goal = selected_goals[0]
            goal_chs = goal_channels[goal]
            ch_budgets = _channel_budget_split(mkt, goal, goal_chs, mkt_budget, sid)
            render_goal_section(mkt, goal, goal_chs, ch_budgets, periods, grand_totals, sid)

        st.divider()

    st.subheader('Grand Total — All Markets')
    for goal in selected_goals:
        if len(selected_goals) > 1:
            st.markdown(f'### {goal}')
        for ch in goal_channels[goal]:
            rows = grand_totals[goal][ch]
            if not rows:
                continue
            gdf = pd.concat(rows, ignore_index=True)
            st.markdown(f'**{ch} — per market**')
            disp = gdf[['Market']].copy()
            for col in ADDITIVE:
                if col in gdf.columns and col in COL_FMT:
                    label, fn = COL_FMT[col]
                    disp[label] = gdf[col].apply(fn)
            st.dataframe(disp, use_container_width=True, hide_index=True)
            grand = {'Period': 'TOTAL', 'Days': int(gdf['Days'].sum())}
            for col in ADDITIVE:
                if col in gdf.columns:
                    grand[col] = gdf[col].sum()
            grand_df = pd.DataFrame([grand])
            g1, g2 = st.columns([2, 3])
            with g1:
                st.markdown(f'**{ch} — combined totals**')
                rows_disp = [{'Metric': COL_FMT[c][0], 'Value': COL_FMT[c][1](grand[c])}
                             for c in ADDITIVE if c in grand and c in COL_FMT]
                st.dataframe(pd.DataFrame(rows_disp), use_container_width=True, hide_index=True)
            with g2:
                st.plotly_chart(
                    make_funnel(grand_df, goal, ch, f'Grand Total — {ch} ({goal})'),
                    use_container_width=True, config={'displayModeBar': False},
                    key=f'grand_{goal}_{ch}_{sid}',
                )
        if len(selected_goals) > 1:
            st.divider()

    return {
        'name': st.session_state.scenario_names[sid],
        'grand_totals': grand_totals,
        'goal_channels': goal_channels,
        'selected_markets': s_markets,
        'market_budgets': s_market_budgets,
        'market_pcts': s_market_pcts,
        'grand_total_bud': s_budget,
    }


for sid, s_tab in enumerate(scenario_tabs):
    with s_tab:
        if len(st.session_state.scenario_names) > 1:
            _, x_col = st.columns([9, 1])
            if x_col.button('✕ Remove', key=f'remove_{sid}', help=f'Remove {st.session_state.scenario_names[sid]}'):
                st.session_state.scenario_names.pop(sid)
                st.rerun()
        s_data = _render_scenario(sid)
        if s_data:
            all_scenarios_data.append(s_data)
            st.divider()
            xl_bytes = _build_excel(s_data, campaign_name, start_date, end_date, audience_type, industry)
            st.download_button(
                label=f'⬇ Download {s_data["name"]} as Excel',
                data=xl_bytes,
                file_name=f'{campaign_name.replace(" ", "_")}_{s_data["name"].replace(" ", "_")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key=f'dl_excel_{sid}',
            )


# ── Compare tab (only when 2+ scenarios) ─────────────────────────────────────

def get_api_key():
    # Streamlit Cloud: secrets injected via dashboard
    try:
        key = st.secrets['anthropic'].get('api_key') or st.secrets['anthropic'].get('ANTHROPIC_API_KEY', '')
        if key:
            return key
    except Exception:
        pass
    # Local fallback: read from .streamlit/secrets.toml next to app file
    local = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
    try:
        s = toml.load(local)
        return s['anthropic'].get('api_key') or s['anthropic'].get('ANTHROPIC_API_KEY', '')
    except Exception:
        return ''

def _aggregate_scenario_metrics(s):
    """Sum all additive metrics across goals and channels for a scenario."""
    totals = {col: 0 for col in ADDITIVE}
    for goal, chs in s['grand_totals'].items():
        for ch, rows in chs.items():
            if not rows:
                continue
            gdf = pd.concat(rows, ignore_index=True)
            for col in ADDITIVE:
                if col in gdf.columns:
                    totals[col] += gdf[col].sum()
    return totals


def _kpi_rows(s, metrics):
    """Build text lines per goal+channel for the AI prompt."""
    lines = []
    for goal, chs in s['grand_totals'].items():
        for ch, rows in chs.items():
            if not rows:
                continue
            gdf = pd.concat(rows, ignore_index=True)
            parts = []
            for col in ADDITIVE:
                if col in gdf.columns and gdf[col].sum() > 0:
                    parts.append(f'{COL_FMT[col][0]}: {COL_FMT[col][1](gdf[col].sum())}')
            if parts:
                lines.append(f'    [{goal} / {ch}] {" | ".join(parts)}')
    return '\n'.join(lines)


if compare_tab is not None:
    with compare_tab:
        st.caption('Side-by-side KPI comparison and AI recommendation — budget efficiency, reach, and funnel performance.')
        if len(all_scenarios_data) < 2:
            st.info('Fill in at least two scenarios (markets, goals, channels, and budgets) to run a comparison.')
        else:
            # ── KPI summary table (always visible, no button needed) ──────────
            st.markdown('#### KPI Summary')
            metric_labels = {col: COL_FMT[col][0] for col in ADDITIVE if col in COL_FMT}
            summary_rows = []
            for s in all_scenarios_data:
                agg = _aggregate_scenario_metrics(s)
                row = {'Scenario': s['name'], 'Budget (€)': f"€{agg['Budget']:,.0f}"}
                for col in ADDITIVE:
                    if col == 'Budget':
                        continue
                    if agg.get(col, 0) > 0:
                        row[metric_labels[col]] = COL_FMT[col][1](agg[col])
                summary_rows.append(row)
            st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

            # ── Winner callouts per metric ────────────────────────────────────
            st.markdown('#### Which scenario leads on each KPI?')
            winner_cols = st.columns(len(ADDITIVE) - 1)  # skip Budget
            col_idx = 0
            for col in ADDITIVE:
                if col == 'Budget':
                    continue
                vals = [(s['name'], _aggregate_scenario_metrics(s).get(col, 0)) for s in all_scenarios_data]
                best = max(vals, key=lambda x: x[1])
                if best[1] > 0:
                    winner_cols[col_idx].metric(metric_labels[col], best[0], help=f'Highest {metric_labels[col]} across all scenarios')
                col_idx += 1

            st.divider()

            # ── AI deep-dive ──────────────────────────────────────────────────
            if st.button('Generate AI Comparison', key='btn_compare'):
                api_key = get_api_key()
                if not api_key:
                    st.error('No API key found in .streamlit/secrets.toml')
                else:
                    def _scenario_block(s):
                        agg = _aggregate_scenario_metrics(s)
                        lines = [f"Scenario: {s['name']}"]
                        lines.append(f"  Total budget: €{s['grand_total_bud']:,.0f}")
                        lines.append(f"  Markets ({len(s['selected_markets'])}): {', '.join(MARKET_LABELS[m] for m in s['selected_markets'])}")
                        for goal, chs in s['goal_channels'].items():
                            lines.append(f"  Goal: {goal} | Channels: {', '.join(chs)}")
                        lines.append('  Aggregated KPIs:')
                        for col in ADDITIVE:
                            if col in agg and agg[col] > 0:
                                lines.append(f'    {COL_FMT[col][0]}: {COL_FMT[col][1](agg[col])}')
                        lines.append('  KPIs by goal and channel:')
                        lines.append(_kpi_rows(s, agg))
                        return '\n'.join(lines)

                    scenarios_text = '\n\n'.join(_scenario_block(s) for s in all_scenarios_data)
                    compare_prompt = f"""You are a senior paid media strategist comparing {len(all_scenarios_data)} media plan scenarios for a {audience_type} brand in the {industry} sector.

{scenarios_text}

For each scenario write a clearly labelled block using exactly this format (one block per scenario):

SCENARIO: [name]
STRENGTHS: [60–80 words — what this scenario does well for a {audience_type} {industry} brand: market coverage, channel fit, which KPIs it leads on and why that matters for this industry]
WEAKNESSES: [60–80 words — where this scenario underperforms: KPIs it loses on, missing markets, channel imbalance, or poor fit with {audience_type} buyer journeys in {industry}]
VERDICT: [25–35 words — one direct sentence on the single best use case for this scenario]

After all scenario blocks, write these two final sections:

BEST FOR BUDGET EFFICIENCY:
[50–60 words — which scenario delivers the most value per euro spent, referencing the actual KPI numbers. Frame this for a {audience_type} {industry} brand where budget scrutiny is typical.]

BEST FOR KPI PERFORMANCE:
[50–60 words — which scenario wins on raw KPI delivery per funnel stage (awareness → traffic → conversion), and what that means for a {audience_type} {industry} campaign objective.]

No bullet points. Write like a strategist presenting to a client."""

                    import anthropic as _anthropic
                    client = _anthropic.Anthropic(api_key=api_key)
                    with st.spinner('Comparing scenarios...'):
                        msg = client.messages.create(
                            model='claude-haiku-4-5-20251001',
                            max_tokens=1100,
                            messages=[{'role': 'user', 'content': compare_prompt}]
                        )
                    raw = msg.content[0].text
                    import re as _re
                    blocks = _re.split(r'\n(SCENARIO|STRENGTHS|WEAKNESSES|VERDICT|BEST FOR BUDGET EFFICIENCY|BEST FOR KPI PERFORMANCE):\s*', raw)
                    if len(blocks) > 1:
                        labels = blocks[1::2]
                        bodies = blocks[2::2]
                        palette = {
                            'SCENARIO':                   ('#1F497D', 'white'),
                            'STRENGTHS':                  ('#1F6152', 'white'),
                            'WEAKNESSES':                 ('#8B3A3A', 'white'),
                            'VERDICT':                    ('#437CA3', 'white'),
                            'BEST FOR BUDGET EFFICIENCY': ('#5A3E7A', 'white'),
                            'BEST FOR KPI PERFORMANCE':   ('#2D6A8A', 'white'),
                        }
                        for label, body in zip(labels, bodies):
                            bg, fg = palette.get(label, ('#555', 'white'))
                            st.markdown(
                                f'<div style="background:{bg};color:{fg};padding:6px 12px;border-radius:4px 4px 0 0;'
                                f'font-weight:bold;margin-top:10px">{label}</div>'
                                f'<div style="background:#f5f5f5;padding:10px 12px;border-radius:0 0 4px 4px;'
                                f'margin-bottom:2px">{body.strip()}</div>',
                                unsafe_allow_html=True,
                            )
                    else:
                        st.markdown(raw)


# ── AI Insights & Recommendations ────────────────────────────────────────────
st.divider()
st.subheader('AI Insights & Recommendations')

if all_scenarios_data:
    scenario_options = [s['name'] for s in all_scenarios_data]
    ai_scenario_name = st.selectbox('Scenario to analyse', scenario_options)
    ai_data = next(s for s in all_scenarios_data if s['name'] == ai_scenario_name)
else:
    ai_data = None

st.caption(f'Insights framed for **{audience_type}** · **{industry}**')

def build_plan_summary():
    """Compile a plain-text plan summary from the selected scenario's data."""
    if not ai_data:
        return 'No scenario data available.'
    d = ai_data
    lines = [
        f'Campaign: {campaign_name}  ({d["name"]})',
        f'Audience: {audience_type}  |  Industry: {industry}',
        f'Flight: {start_date.strftime("%b %d, %Y")} – {end_date.strftime("%b %d, %Y")} ({(end_date - start_date).days + 1} days)',
        f'Total budget: €{d["grand_total_bud"]:,}',
        f'Markets: {", ".join(MARKET_LABELS[m] for m in d["selected_markets"])}',
        '',
    ]
    for goal, chs in d['goal_channels'].items():
        lines.append(f'Goal: {goal}  |  Channels: {", ".join(chs)}')
        for ch in chs:
            rows = d['grand_totals'][goal][ch]
            if not rows:
                continue
            gdf = pd.concat(rows, ignore_index=True)
            grand = {col: gdf[col].sum() for col in ADDITIVE if col in gdf.columns}
            parts = [f'{COL_FMT[col][0]}: {COL_FMT[col][1](grand[col])}'
                     for col in ADDITIVE if col in grand and col in COL_FMT]
            lines.append(f'  {ch}: {" | ".join(parts)}')
        lines.append('')
    return '\n'.join(lines)

ai_tab_insights, ai_tab_recs, ai_tab_benchmarks = st.tabs([
    'Plan Insights', 'Market Recommendations', 'Benchmark Explanations'
])

with ai_tab_insights:
    st.caption('High-level read of the plan — what the numbers say, what looks strong, what to watch.')
    if st.button('Generate Plan Insights', key='btn_insights'):
        api_key = get_api_key()
        if not api_key:
            st.error('No API key found in .streamlit/secrets.toml')
        else:
            summary = build_plan_summary()
            prompt = f"""You are a senior paid media strategist reviewing a digital media plan for a {audience_type} brand in the {industry} sector.

{summary}

Write a concise but sharp analysis (150–200 words). Cover:
1. Overall scale and reach potential given the budget and markets — frame this for {audience_type} {industry} audiences specifically
2. Channel mix strengths or gaps for the selected goals — comment on what works for {audience_type} in this sector
3. Any markets where the allocation looks strong or under-invested for this industry
4. One clear watch-out or risk relevant to {audience_type} {industry} campaigns

Be direct. No headers. No bullet points. Write in plain paragraphs like a strategist talking to a client."""
            import anthropic as _anthropic
            client = _anthropic.Anthropic(api_key=api_key)
            with st.spinner('Thinking...'):
                msg = client.messages.create(
                    model='claude-haiku-4-5-20251001',
                    max_tokens=400,
                    messages=[{'role': 'user', 'content': prompt}]
                )
            st.markdown(msg.content[0].text)

with ai_tab_recs:
    st.caption('Budget allocation recommendations — which markets or channels deserve more weight and why.')
    if st.button('Generate Market Recommendations', key='btn_recs'):
        api_key = get_api_key()
        if not api_key:
            st.error('No API key found in .streamlit/secrets.toml')
        else:
            summary = build_plan_summary()
            mkt_list = '\n'.join(
                f'- {MARKET_LABELS[m]}: {ai_data["market_pcts"][m]:.1f}% (€{ai_data["market_budgets"][m]:,.0f})'
                for m in ai_data['selected_markets']
            ) if ai_data else 'No data.'
            channels_in_use = sorted({ch for chs in (ai_data['goal_channels'].values() if ai_data else []) for ch in chs})
            prompt = f"""You are a senior paid media strategist advising a {audience_type} brand in the {industry} sector on market budget allocation across {', '.join(channels_in_use) if channels_in_use else 'digital channels'}.

{summary}

Current market split:
{mkt_list}

Write exactly 3 recommendation sections, each starting with its label on its own line:

CURRENT ALLOCATION:
[50–60 words assessing whether the current market split makes sense for a {audience_type} {industry} brand — consider CPM efficiency vs audience quality for this sector and whether the channels in use ({', '.join(channels_in_use) if channels_in_use else 'the selected channels'}) justify the current weights]

REBALANCING OPTION:
[50–60 words suggesting one concrete rebalancing move — e.g. shift 10% from X to Y — grounded in what works for {audience_type} audiences in {industry} and the channel mix being used]

BEST ALLOCATION:
[50–60 words giving a direct final recommendation on the optimal split, framed specifically for a {audience_type} {industry} brand running {', '.join(channels_in_use) if channels_in_use else 'these channels'}]

Be direct. No bullet points within sections."""
            import anthropic as _anthropic
            client = _anthropic.Anthropic(api_key=api_key)
            with st.spinner('Thinking...'):
                msg = client.messages.create(
                    model='claude-haiku-4-5-20251001',
                    max_tokens=500,
                    messages=[{'role': 'user', 'content': prompt}]
                )
            raw = msg.content[0].text
            # Render each section with a styled header
            import re as _re
            sections = _re.split(r'\n(CURRENT ALLOCATION|REBALANCING OPTION|BEST ALLOCATION):\n', raw)
            if len(sections) > 1:
                labels = sections[1::2]
                bodies = sections[2::2]
                colors = {'CURRENT ALLOCATION': '#437CA3', 'REBALANCING OPTION': '#437CA3', 'BEST ALLOCATION': '#1F6152'}
                for label, body in zip(labels, bodies):
                    color = colors.get(label, '#437CA3')
                    st.markdown(f'<div style="background:{color};color:white;padding:6px 10px;border-radius:4px;font-weight:bold;margin-top:8px">{label}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="background:#f2f2f2;padding:10px;border-radius:0 0 4px 4px;margin-bottom:4px">{body.strip()}</div>', unsafe_allow_html=True)
            else:
                st.markdown(raw)

with ai_tab_benchmarks:
    st.caption('Plain-English explanations of the benchmark values used in this plan.')

    def _bench_context():
        """Build a reusable benchmark context block for AI prompts."""
        bench_lines = []
        for mkt in (ai_data['selected_markets'] if ai_data else []):
            for goal, chs in (ai_data['goal_channels'].items() if ai_data else []):
                for ch in chs:
                    b = BENCH[mkt][ch]
                    if ch == 'Search':
                        bench_lines.append(f'{MARKET_LABELS[mkt]} / {ch}: CPC €{b["cpc"]:.2f}, CTR {b["ctr"]*100:.1f}%, Click→Session {b.get("click_to_session",0.85)*100:.0f}%')
                    else:
                        bench_lines.append(f'{MARKET_LABELS[mkt]} / {ch}: CPM €{b["cpm"]:.2f}, CTR {b["ctr"]*100:.2f}%, Freq {b.get("frequency",3.0):.1f}' + (f', View Rate {b.get("view_rate",0.31)*100:.0f}%' if ch == 'YouTube' else ''))
        channels_in_use = sorted({ch for chs in (ai_data['goal_channels'].values() if ai_data else []) for ch in chs})
        return bench_lines, channels_in_use

    if st.button('Generate Benchmark Explanations', key='btn_bench'):
        api_key = get_api_key()
        if not api_key:
            st.error('No API key found in .streamlit/secrets.toml')
        else:
            bench_lines, channels_in_use = _bench_context()
            prompt = f"""You are a senior paid media strategist explaining benchmark values to a {audience_type} client in the {industry} sector.

The plan uses these channels: {', '.join(channels_in_use) if channels_in_use else 'various digital channels'}.

Benchmarks in use:
{chr(10).join(bench_lines)}

Write a short explanation (150–180 words) covering:
- What CPM / CPC levels mean in the context of {audience_type} {industry} campaigns — why some markets cost more and whether that premium makes sense for this sector
- Why CTR and View Rate vary between markets and channels — relate this to {audience_type} audience behaviour (e.g. professional vs consumer mindset, intent signals)
- What Frequency means for brand recall in {industry}, and how it should be managed differently depending on whether the goal is awareness or conversion

Write in plain English. No jargon. One paragraph per topic. Frame everything for someone who understands the {industry} business, not a media buyer."""
            import anthropic as _anthropic
            client = _anthropic.Anthropic(api_key=api_key)
            with st.spinner('Thinking...'):
                msg = client.messages.create(
                    model='claude-haiku-4-5-20251001',
                    max_tokens=400,
                    messages=[{'role': 'user', 'content': prompt}]
                )
            st.markdown(msg.content[0].text)

    st.divider()
    st.markdown('#### Ask a question about the benchmarks')
    st.caption('Ask anything — why a market costs more, whether a CTR looks realistic, what to adjust for your industry, etc.')
    bench_question = st.text_area(
        'Your question',
        placeholder='e.g. Why is the CPM in Germany higher than in Poland? Should I adjust the view rate for a B2B audience?',
        key='bench_question',
        label_visibility='collapsed',
        height=90,
    )
    if st.button('Ask AI', key='btn_bench_ask'):
        if not bench_question.strip():
            st.warning('Type a question first.')
        else:
            api_key = get_api_key()
            if not api_key:
                st.error('No API key found in .streamlit/secrets.toml')
            else:
                bench_lines, channels_in_use = _bench_context()
                ask_prompt = f"""You are a senior paid media strategist advising a {audience_type} client in the {industry} sector.

The plan uses these channels: {', '.join(channels_in_use) if channels_in_use else 'various digital channels'}.

Benchmarks in use:
{chr(10).join(bench_lines)}

The client's question:
{bench_question.strip()}

Answer in 100–150 words. Be direct and practical. Reference the actual benchmark numbers where relevant. Frame everything for a {audience_type} {industry} context. No bullet points — plain paragraphs, like a strategist talking to a client."""
                import anthropic as _anthropic
                client = _anthropic.Anthropic(api_key=api_key)
                with st.spinner('Thinking...'):
                    msg = client.messages.create(
                        model='claude-haiku-4-5-20251001',
                        max_tokens=350,
                        messages=[{'role': 'user', 'content': ask_prompt}]
                    )
                st.markdown(
                    f'<div style="background:#f0faf9;border-left:3px solid #2BB5A5;padding:12px 14px;'
                    f'border-radius:0 4px 4px 0;margin-top:8px">{msg.content[0].text}</div>',
                    unsafe_allow_html=True,
                )
