"""KPI Matrix — reference page for channel × phase × format metrics."""
import streamlit as st

# ── Data ─────────────────────────────────────────────────────────────────────
# badge values: 'core' | 'secondary' | 'caution' | 'diagnostic'
# note (optional): inline caveat shown under the metric label

KPI_MATRIX = {
    'Awareness': {
        'Display': {
            'Responsive Display / Banner': [
                {'metric': 'CPM',           'badge': 'core'},
                {'metric': 'Reach',         'badge': 'core'},
                {'metric': 'Frequency',     'badge': 'core'},
                {'metric': 'Impressions',   'badge': 'secondary'},
                {'metric': 'Clicks / CTR',  'badge': 'diagnostic',
                 'note': 'CTR is very low on display (~0.1–0.3%) — not a meaningful KPI at awareness stage.'},
                {'metric': 'CPC',           'badge': 'diagnostic',
                 'note': 'Not primary — display is CPM-bought.'},
            ],
        },
        'YouTube': {
            'Skippable in-stream': [
                {'metric': 'CPM',                  'badge': 'core'},
                {'metric': 'Reach',                'badge': 'core'},
                {'metric': 'Frequency',            'badge': 'core'},
                {'metric': 'VTR / View-through rate', 'badge': 'core'},
                {'metric': 'CPV',                  'badge': 'core'},
                {'metric': 'Views',                'badge': 'secondary'},
                {'metric': 'Impressions',          'badge': 'secondary'},
                {'metric': 'Clicks / CTR / CPC',  'badge': 'diagnostic',
                 'note': 'Not primary KPIs at awareness stage.'},
            ],
            'Bumper (6s non-skip)': [
                {'metric': 'CPM',        'badge': 'core'},
                {'metric': 'Reach',      'badge': 'core'},
                {'metric': 'Frequency',  'badge': 'core'},
                {'metric': 'Impressions','badge': 'secondary'},
                {'metric': 'VTR',        'badge': 'diagnostic',
                 'note': 'Not applicable — non-skippable format.'},
            ],
            'Demand Gen': [
                {'metric': 'CPM',          'badge': 'core'},
                {'metric': 'Reach',        'badge': 'core'},
                {'metric': 'Brand Lift',   'badge': 'secondary',
                 'note': 'Only if a Brand Lift study is enabled.'},
                {'metric': 'Views',        'badge': 'secondary'},
                {'metric': 'Clicks / CTR', 'badge': 'diagnostic'},
            ],
        },
        'Search': {
            'Brand search / DSA': [
                {'metric': 'Impressions',       'badge': 'core'},
                {'metric': 'Impression Share',  'badge': 'core'},
                {'metric': 'CTR',               'badge': 'secondary'},
                {'metric': 'Clicks',            'badge': 'secondary'},
                {'metric': 'CPM',               'badge': 'diagnostic',
                 'note': 'Not native to Search — CPC-based channel.'},
            ],
        },
        'LinkedIn': {
            'Single Image / Carousel': [
                {'metric': 'CPM',               'badge': 'core'},
                {'metric': 'Reach',             'badge': 'core'},
                {'metric': 'Frequency',         'badge': 'core'},
                {'metric': 'Impressions',       'badge': 'secondary'},
                {'metric': 'Clicks / CTR / CPC','badge': 'diagnostic'},
            ],
            'Video Ad': [
                {'metric': 'CPM',   'badge': 'core'},
                {'metric': 'Reach', 'badge': 'core'},
                {'metric': 'VTR',   'badge': 'core'},
                {'metric': 'CPV',   'badge': 'core'},
                {'metric': 'Views at 25% / 50% / 100% completion', 'badge': 'secondary'},
                {'metric': 'Brand Lift', 'badge': 'secondary',
                 'note': 'Only if a Brand Lift study is enabled.'},
            ],
        },
    },
    'Consideration': {
        'Display': {
            'Responsive Display / Banner': [
                {'metric': 'Clicks',               'badge': 'core'},
                {'metric': 'CTR',                  'badge': 'core',
                 'note': 'Compare vs. benchmark (~0.1–0.3%) not vs. search/social.'},
                {'metric': 'CPC',                  'badge': 'core'},
                {'metric': 'Landing Page Sessions', 'badge': 'secondary'},
                {'metric': 'CPM',                  'badge': 'secondary'},
                {'metric': 'Impressions',          'badge': 'diagnostic'},
            ],
        },
        'YouTube': {
            'Skippable in-stream': [
                {'metric': 'Engaged Views',      'badge': 'core',
                 'note': 'Watched ≥10s without skipping.'},
                {'metric': 'Avg View Duration',  'badge': 'core'},
                {'metric': 'Watch Time',         'badge': 'core'},
                {'metric': 'CTR',                'badge': 'secondary'},
                {'metric': 'CPC',                'badge': 'secondary'},
                {'metric': 'Landing Page Sessions', 'badge': 'secondary'},
            ],
            'Demand Gen': [
                {'metric': 'Clicks',               'badge': 'core'},
                {'metric': 'CTR',                  'badge': 'core'},
                {'metric': 'CPC',                  'badge': 'core'},
                {'metric': 'Landing Page Sessions', 'badge': 'secondary'},
                {'metric': 'Bounce Rate',           'badge': 'secondary',
                 'note': 'Post-click metric — measured in GA4.'},
            ],
        },
        'Search': {
            'Non-brand keywords': [
                {'metric': 'Clicks',    'badge': 'core'},
                {'metric': 'CTR',       'badge': 'core'},
                {'metric': 'CPC',       'badge': 'core'},
                {'metric': 'Impressions',          'badge': 'secondary'},
                {'metric': 'Landing Page Sessions', 'badge': 'secondary'},
                {'metric': 'Time on Site / Pages per Session', 'badge': 'secondary',
                 'note': 'Post-click metric — measured in GA4.'},
            ],
        },
        'LinkedIn': {
            'Single Image / Carousel': [
                {'metric': 'Engagement Rate', 'badge': 'core',
                 'note': 'LinkedIn native: (clicks + reactions + shares + follows) / impressions.'},
                {'metric': 'Clicks',  'badge': 'core'},
                {'metric': 'CTR',     'badge': 'core'},
                {'metric': 'CPC',     'badge': 'core'},
                {'metric': 'Landing Page Sessions',      'badge': 'secondary'},
                {'metric': 'Reactions / Shares / Comments', 'badge': 'secondary'},
            ],
            'Thought Leader / Document Ad': [
                {'metric': 'Engagement Rate', 'badge': 'core'},
                {'metric': 'Page Opens / Reads', 'badge': 'core',
                 'note': 'Document Ad native metric.'},
                {'metric': 'CTR', 'badge': 'secondary'},
                {'metric': 'CPC', 'badge': 'secondary'},
            ],
        },
    },
    'Conversion': {
        'Display': {
            'Remarketing / Responsive Display': [
                {'metric': 'CPA',         'badge': 'core'},
                {'metric': 'Conversions', 'badge': 'core'},
                {'metric': 'CVR',         'badge': 'core',
                 'note': 'Conversions / Clicks — expect low absolute CTR but reasonable CVR if audience is warm.'},
                {'metric': 'CPC',         'badge': 'secondary'},
                {'metric': 'Clicks',      'badge': 'secondary'},
                {'metric': 'View-through Conversions', 'badge': 'caution',
                 'note': 'Very easily inflated on display — verify attribution window carefully.'},
                {'metric': 'Impressions / CPM', 'badge': 'diagnostic'},
            ],
        },
        'YouTube': {
            'Demand Gen / Action': [
                {'metric': 'CPA',         'badge': 'core'},
                {'metric': 'Conversions', 'badge': 'core'},
                {'metric': 'CVR',         'badge': 'core',
                 'note': 'Conversions / Clicks.'},
                {'metric': 'CPC',    'badge': 'secondary'},
                {'metric': 'Clicks', 'badge': 'secondary'},
                {'metric': 'View-through Conversions', 'badge': 'caution',
                 'note': 'Verify attribution window — easily inflated.'},
                {'metric': 'Impressions / CTR', 'badge': 'diagnostic'},
            ],
        },
        'Search': {
            'Performance Max / Search': [
                {'metric': 'CPA',         'badge': 'core'},
                {'metric': 'Conversions', 'badge': 'core'},
                {'metric': 'CVR',         'badge': 'core'},
                {'metric': 'CPC',         'badge': 'core'},
                {'metric': 'Clicks',      'badge': 'secondary'},
                {'metric': 'ROAS',        'badge': 'secondary',
                 'note': 'Only if e-commerce or pipeline value is tracked.'},
                {'metric': 'CTR', 'badge': 'diagnostic'},
            ],
        },
        'LinkedIn': {
            'Lead Gen Form': [
                {'metric': 'CPA / Cost per lead',     'badge': 'core'},
                {'metric': 'Conversions / Form submits', 'badge': 'core'},
                {'metric': 'CVR',                     'badge': 'core'},
                {'metric': 'MQL', 'badge': 'core',
                 'note': 'From CRM — do not rely on LinkedIn\'s conversion count alone.'},
                {'metric': 'SQL', 'badge': 'core',
                 'note': 'From CRM.'},
                {'metric': 'CPC', 'badge': 'secondary'},
                {'metric': 'View-through Conversions', 'badge': 'caution',
                 'note': 'Verify attribution window — easily inflated.'},
                {'metric': 'Impressions / CTR', 'badge': 'diagnostic'},
            ],
            'Single Image → Landing Page': [
                {'metric': 'CPA',         'badge': 'core'},
                {'metric': 'CVR',         'badge': 'core'},
                {'metric': 'Conversions', 'badge': 'core'},
                {'metric': 'MQL', 'badge': 'secondary', 'note': 'From CRM.'},
                {'metric': 'SQL', 'badge': 'secondary', 'note': 'From CRM.'},
                {'metric': 'CPC', 'badge': 'secondary'},
                {'metric': 'View-through Conversions', 'badge': 'caution',
                 'note': 'Verify attribution window — easily inflated.'},
            ],
        },
    },
}

# ── Styling constants ─────────────────────────────────────────────────────────
BADGE_CSS = {
    'core':       ('background:#1a7a5e; color:#fff',  'Core KPI'),
    'secondary':  ('background:#2563eb; color:#fff',  'Secondary'),
    'caution':    ('background:#b45309; color:#fff',  'Caution'),
    'diagnostic': ('background:#4b5563; color:#fff',  'Diagnostic'),
}

CHANNEL_ICON = {'Display': '🖼', 'YouTube': '▶', 'Search': '🔍', 'LinkedIn': '💼'}

PHASE_COLOR = {
    'Awareness':     '#7c3aed',
    'Consideration': '#0369a1',
    'Conversion':    '#065f46',
}

PHASE_ICON = {
    'Awareness':     '👁',
    'Consideration': '🤔',
    'Conversion':    '✅',
}


def _badge(b: str) -> str:
    style, label = BADGE_CSS[b]
    return (
        f'<span style="display:inline-block; padding:2px 8px; border-radius:4px; '
        f'font-size:0.68rem; font-weight:600; letter-spacing:0.04em; {style}">'
        f'{label}</span>'
    )


def _metric_row(m: dict) -> str:
    note_html = ''
    if m.get('note'):
        note_html = (
            f'<div style="font-size:0.72rem; color:#6b7280; margin-top:2px; '
            f'font-style:italic;">{m["note"]}</div>'
        )
    return (
        f'<div style="display:flex; align-items:flex-start; gap:10px; '
        f'padding:7px 0; border-bottom:1px solid #f1f5f9;">'
        f'  <div style="flex:1; font-size:0.88rem; font-weight:500; color:#1e293b;">'
        f'    {m["metric"]}{note_html}'
        f'  </div>'
        f'  <div style="flex-shrink:0; padding-top:1px;">{_badge(m["badge"])}</div>'
        f'</div>'
    )


def _format_card(fmt_name: str, metrics: list) -> str:
    rows = ''.join(_metric_row(m) for m in metrics)
    return (
        f'<div style="background:#fff; border:1px solid #e2e8f0; border-radius:8px; '
        f'padding:14px 16px; margin-bottom:12px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
        f'  <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; '
        f'letter-spacing:0.06em; color:#64748b; margin-bottom:8px;">{fmt_name}</div>'
        f'  {rows}'
        f'</div>'
    )


# ── Page ──────────────────────────────────────────────────────────────────────
st.markdown('## KPI Matrix')
st.caption('Reference guide — which metrics to track, report, and optimise by channel, phase, and format.')

st.markdown("""
<style>
.kpi-legend { display:flex; gap:16px; flex-wrap:wrap; margin-bottom:1.2rem; }
.kpi-legend-item { display:flex; align-items:center; gap:6px; font-size:0.8rem; color:#374151; }
</style>
<div class="kpi-legend">
  <div class="kpi-legend-item"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#1a7a5e"></span>Core KPI — optimise and report against this</div>
  <div class="kpi-legend-item"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#2563eb"></span>Secondary — useful supporting context</div>
  <div class="kpi-legend-item"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#b45309"></span>Caution — available but handle carefully</div>
  <div class="kpi-legend-item"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#4b5563"></span>Diagnostic — troubleshooting only, not a reportable KPI</div>
</div>
""", unsafe_allow_html=True)

# ── Filters ───────────────────────────────────────────────────────────────────
all_phases   = list(KPI_MATRIX.keys())
all_channels = ['Display', 'YouTube', 'Search', 'LinkedIn']

filter_col1, filter_col2 = st.columns([1, 1])
with filter_col1:
    sel_phases = st.multiselect(
        'Funnel phase',
        all_phases,
        default=all_phases,
        key='kpi_phase_filter',
    )
with filter_col2:
    sel_channels = st.multiselect(
        'Channel',
        all_channels,
        default=all_channels,
        key='kpi_channel_filter',
    )

if not sel_phases:
    sel_phases = all_phases
if not sel_channels:
    sel_channels = all_channels

st.divider()

# ── Render ────────────────────────────────────────────────────────────────────
nothing_shown = True

for phase in all_phases:
    if phase not in sel_phases:
        continue

    phase_channels = {
        ch: formats for ch, formats in KPI_MATRIX[phase].items()
        if ch in sel_channels
    }
    if not phase_channels:
        continue

    nothing_shown = False
    phase_color = PHASE_COLOR[phase]
    phase_icon  = PHASE_ICON[phase]

    st.markdown(
        f'<h3 style="color:{phase_color}; margin-top:0.4rem; margin-bottom:0.8rem;">'
        f'{phase_icon} {phase}</h3>',
        unsafe_allow_html=True,
    )

    ch_cols = st.columns(len(phase_channels))
    for col, (channel, formats) in zip(ch_cols, phase_channels.items()):
        icon = CHANNEL_ICON.get(channel, '')
        with col:
            st.markdown(
                f'<div style="font-size:1rem; font-weight:700; color:#1e293b; '
                f'margin-bottom:10px; padding-bottom:6px; '
                f'border-bottom:2px solid {phase_color};">'
                f'{icon} {channel}</div>',
                unsafe_allow_html=True,
            )
            for fmt_name, metrics in formats.items():
                st.markdown(_format_card(fmt_name, metrics), unsafe_allow_html=True)

    st.divider()

if nothing_shown:
    st.info('No results for the selected filters.')
