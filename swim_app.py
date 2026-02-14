import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import io
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Swim Performance Tracker",
    page_icon=":swimmer:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS theme
st.markdown("""
<style>
    /* Import professional sans-serif font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ===== ROOT VARIABLES ===== */
    :root {
        --primary-blue: #0c0599;
        --secondary-blue: #1a3fa0;
        --accent-blue: #2d6bcf;
        --dark-blue: #060340;
        --light-blue: #eef2fb;
        --surface-white: #ffffff;
        --stripe-gray: #f3f3f3;
        --text-primary: #1a1a2e;
        --text-secondary: #555570;
        --border-color: #d0d5e0;
        --gold: #FFD700;
        --silver: #C0C0C0;
        --bronze: #CD7F32;
        --freestyle-blue: #0c0599;
        --backstroke-green: #00875a;
        --breaststroke-orange: #e8910c;
        --butterfly-red: #d94f1a;
        --im-purple: #6b21a8;
        --card-shadow: 0 2px 12px rgba(12, 5, 153, 0.08);
        --card-radius: 12px;
    }

    /* ===== GLOBAL TYPOGRAPHY ===== */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* ===== HEADINGS ===== */
    h1 {
        color: var(--dark-blue);
        font-weight: 700;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid var(--primary-blue);
        font-size: 1.8rem;
        letter-spacing: -0.02em;
    }

    h2 {
        color: var(--primary-blue);
        font-weight: 600;
        margin-top: 1.5rem;
        font-size: 1.35rem;
    }

    h3 {
        color: var(--secondary-blue);
        font-weight: 600;
        font-size: 1.1rem;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--dark-blue) 0%, var(--primary-blue) 100%);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stRadio label span {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.2);
    }

    /* Sidebar radio buttons as nav items */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        padding: 0.6rem 1rem;
        border-radius: 8px;
        margin-bottom: 2px;
        transition: background 0.2s ease;
        cursor: pointer;
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(255,255,255,0.12);
    }

    [data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: rgba(255,255,255,0.2);
        font-weight: 600;
    }

    /* Sidebar metrics */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.5rem;
    }

    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: rgba(255,255,255,0.8) !important;
    }

    /* ===== CARD CONTAINER ===== */
    .pro-card {
        background: var(--surface-white);
        border-radius: var(--card-radius);
        box-shadow: var(--card-shadow);
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        border: 1px solid var(--border-color);
    }

    .pro-card-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--dark-blue);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--light-blue);
    }

    /* ===== STROKE CARDS ===== */
    .stroke-card {
        background: var(--surface-white);
        border-radius: var(--card-radius);
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
        border: 1px solid var(--border-color);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        overflow: hidden;
    }

    .stroke-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(12, 5, 153, 0.12);
    }

    .stroke-card .pro-table {
        font-size: 0.82rem;
        table-layout: auto;
    }

    .freestyle-card { border-left: 5px solid var(--freestyle-blue); }
    .backstroke-card { border-left: 5px solid var(--backstroke-green); }
    .breaststroke-card { border-left: 5px solid var(--breaststroke-orange); }
    .butterfly-card { border-left: 5px solid var(--butterfly-red); }
    .im-card { border-left: 5px solid var(--im-purple); }

    /* ===== STYLED HTML TABLES ===== */
    .pro-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border: 2px solid var(--primary-blue);
        border-radius: 8px;
        overflow: hidden;
        font-size: 0.9rem;
    }

    .pro-table thead th {
        background: var(--primary-blue);
        color: #ffffff;
        font-weight: 600;
        padding: 0.5rem 0.6rem;
        text-align: left;
        border: none;
        letter-spacing: 0.02em;
        font-size: 0.8rem;
        text-transform: uppercase;
        white-space: nowrap;
    }

    .pro-table tbody tr:nth-child(even) {
        background-color: var(--stripe-gray);
    }

    .pro-table tbody tr:nth-child(odd) {
        background-color: var(--surface-white);
    }

    .pro-table tbody tr:hover {
        background-color: var(--light-blue);
    }

    .pro-table tbody td {
        padding: 0.5rem 0.6rem;
        border-top: 1px solid var(--border-color);
        color: var(--text-primary);
        white-space: nowrap;
    }

    /* ===== STANDARD BADGES ===== */
    .standard-badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.8rem;
        margin: 0.15rem;
        letter-spacing: 0.02em;
    }

    .standard-AAAA { background-color: #FFD700; color: #000; }
    .standard-AAA { background-color: #C0C0C0; color: #000; }
    .standard-AA { background-color: #CD7F32; color: #FFF; }
    .standard-A { background-color: var(--primary-blue); color: #FFF; }
    .standard-BB { background-color: var(--accent-blue); color: #FFF; }
    .standard-B { background-color: #87CEEB; color: #000; }

    /* ===== SUMMARY TABLE (replaces st.metric rows) ===== */
    .summary-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 0;
    }

    .summary-table td {
        padding: 0.75rem 1rem;
        vertical-align: top;
    }

    .summary-table .stat-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .summary-table .stat-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--primary-blue);
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: var(--primary-blue);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        letter-spacing: 0.02em;
    }

    .stButton > button:hover {
        background: var(--dark-blue);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(12, 5, 153, 0.25);
    }

    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--accent-blue);
        border-radius: 8px;
        padding: 1rem;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 1rem;
    }

    /* ===== MAIN METRIC STYLING ===== */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--primary-blue);
    }

    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: var(--dark-blue);
    }

    /* ===== DATAFRAME ===== */
    .dataframe {
        font-size: 0.9rem;
    }

    /* ===== FOOTER ===== */
    .pro-footer {
        text-align: center;
        color: var(--text-secondary);
        padding: 1.5rem 0;
        font-size: 0.85rem;
        border-top: 1px solid var(--border-color);
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Plotly chart theme
PLOTLY_THEME = dict(
    template='plotly_white',
    font=dict(family='Inter, sans-serif', size=12, color='#1a1a2e'),
    title_font=dict(size=14, color='#060340'),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    colorway=['#0c0599', '#1a3fa0', '#2d6bcf', '#00875a', '#e8910c', '#d94f1a', '#6b21a8'],
)

# Helper functions
def load_data():
    """Load all necessary data files"""
    data = {}

    if os.path.exists('graded_swim_data.xlsx'):
        data['swims'] = pd.read_excel('graded_swim_data.xlsx')
        data['swims']['Date'] = pd.to_datetime(data['swims']['Date'])
    else:
        data['swims'] = None

    if os.path.exists('standards.json'):
        with open('standards.json', 'r') as f:
            data['standards'] = json.load(f)
    else:
        data['standards'] = None

    if os.path.exists('goals.csv'):
        data['goals'] = pd.read_csv('goals.csv')
    else:
        data['goals'] = None

    return data

def get_personal_bests(df):
    """Calculate personal bests for each event"""
    if df is None or len(df) == 0:
        return pd.DataFrame()

    pb_data = df[df['Standard'] != 'Unrated'].copy()
    pb_data['Event'] = pb_data['Distance'].astype(str) + ' ' + pb_data['Stroke']

    pb_list = []
    for (event, course), group in pb_data.groupby(['Event', 'Course']):
        fastest = group.loc[group['Time_Seconds'].idxmin()]
        pb_list.append({
            'Event': event,
            'Course': course,
            'Time': fastest['Finals'],
            'Seconds': fastest['Time_Seconds'],
            'Standard': fastest['Standard'],
            'Date': fastest['Date'],
            'Age': fastest['Age']
        })

    return pd.DataFrame(pb_list).sort_values(['Event', 'Course'])

def get_stroke_bests(df, stroke, course):
    """Get best times for specific stroke and course"""
    if df is None or len(df) == 0:
        return []

    if stroke == 'Free':
        if course == 'Yards':
            distances = [50, 100, 200, 500, 800, 1000, 1650]
        else:
            distances = [50, 100, 200, 400, 800, 1500]
    elif stroke in ['Back', 'Breast', 'Fly']:
        distances = [50, 100, 200]
    elif stroke == 'IM':
        distances = [100, 200, 400]
    else:
        return []

    results = []
    for distance in distances:
        event_data = df[
            (df['Distance'] == distance) &
            (df['Stroke'] == stroke) &
            (df['Course'] == course) &
            (df['Standard'] != 'Unrated')
        ]

        if len(event_data) > 0:
            best = event_data.loc[event_data['Time_Seconds'].idxmin()]
            results.append({
                'Distance': distance,
                'Time': best['Finals'],
                'Standard': best['Standard'],
                'Date': best['Date'].strftime('%m/%d/%Y')
            })

    return results

def render_summary_row(items):
    """Render a row of stat items as an HTML summary table inside a card."""
    cells = ""
    for item in items:
        cells += (
            f"<td>"
            f"<div class='stat-label'>{item['label']}</div>"
            f"<div class='stat-value'>{item['value']}</div>"
            f"</td>"
        )
    return (
        f"<div class='pro-card'>"
        f"<table class='summary-table'><tr>{cells}</tr></table>"
        f"</div>"
    )

def render_html_table(df, columns=None):
    """Render a pandas DataFrame as a styled HTML table inside a card."""
    if columns is None:
        columns = {c: c for c in df.columns}

    headers = "".join(f"<th>{v}</th>" for v in columns.values())

    rows = ""
    for _, row in df.iterrows():
        cells = ""
        for col_key in columns.keys():
            val = row[col_key]
            if hasattr(val, 'strftime'):
                val = val.strftime('%m/%d/%Y')
            if col_key == 'Standard' and isinstance(val, str) and val in ('AAAA', 'AAA', 'AA', 'A', 'BB', 'B'):
                cells += f"<td><span class='standard-badge standard-{val}'>{val}</span></td>"
            else:
                cells += f"<td>{val}</td>"
        rows += f"<tr>{cells}</tr>"

    return (
        f"<div class='pro-card'>"
        f"<table class='pro-table'>"
        f"<thead><tr>{headers}</tr></thead>"
        f"<tbody>{rows}</tbody>"
        f"</table>"
        f"</div>"
    )

def card_open(title=None):
    """Return opening HTML for a card container."""
    header = f"<div class='pro-card-header'>{title}</div>" if title else ""
    return f"<div class='pro-card'>{header}"

def card_close():
    """Return closing HTML for a card container."""
    return "</div>"

def create_progression_chart(df, event, course):
    """Create time progression chart for an event"""
    event_data = df[
        (df['Distance'].astype(str) + ' ' + df['Stroke'] == event) &
        (df['Course'] == course)
    ].sort_values('Date')

    if len(event_data) == 0:
        return None

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=event_data['Date'],
        y=event_data['Time_Seconds'],
        mode='lines+markers',
        name='Time',
        line=dict(color='#0c0599', width=3),
        marker=dict(size=8, color='#2d6bcf'),
        hovertemplate='<b>%{y:.2f}s</b><br>%{x|%b %d, %Y}<extra></extra>'
    ))

    fig.update_layout(
        **PLOTLY_THEME,
        title=f'{event} ({course}) Progression',
        xaxis_title='Date',
        yaxis_title='Time (seconds)',
        hovermode='closest',
        height=400,
        yaxis=dict(autorange='reversed')
    )

    return fig

def display_stroke_card(stroke, color, css_class, df, course):
    """Display a stroke summary card with an HTML table."""
    stroke_data = get_stroke_bests(df, stroke, course)

    if not stroke_data:
        return

    rows_html = ""
    for row in stroke_data:
        std = row['Standard']
        badge = f"<span class='standard-badge standard-{std}'>{std}</span>"
        rows_html += (
            f"<tr>"
            f"<td><strong>{row['Distance']}</strong></td>"
            f"<td style='font-family:monospace; font-weight:600;'>{row['Time']}</td>"
            f"<td>{badge}</td>"
            f"<td style='color:var(--text-secondary);'>{row['Date']}</td>"
            f"</tr>"
        )

    html = (
        f"<div class='stroke-card {css_class}'>"
        f"<div class='pro-card-header'>{stroke}</div>"
        f"<table class='pro-table'>"
        f"<thead><tr><th>Dist</th><th>Best Time</th><th>Standard</th><th>Date</th></tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        f"</table>"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(
        "<div style='text-align:center; padding: 1.5rem 0 1rem;'>"
        "<div style='font-size:2rem; font-weight:700; color:#ffffff; letter-spacing:-0.02em;'>Swim Tracker</div>"
        "<div style='font-size:0.8rem; color:rgba(255,255,255,0.6); margin-top:0.25rem;'>Performance Analytics</div>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["Stroke Overview", "Quick Lookup", "Deep Analytics", "Goals", "Upload Data", "Settings"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    data = load_data()
    if data['swims'] is not None:
        st.metric("Total Swims", len(data['swims']))
        st.metric("AAA Times", len(data['swims'][data['swims']['Standard'] == 'AAA']))
        st.metric("AA Times", len(data['swims'][data['swims']['Standard'] == 'AA']))

# Main content
if page == "Stroke Overview":
    st.title("Stroke Overview")

    data = load_data()

    if data['swims'] is None:
        st.warning("No swim data found. Please upload data in the Upload Data section.")
    else:
        df = data['swims']

        st.markdown("### Select Course")
        course_option = st.radio(
            "Course Type",
            ["Yards", "LCM"],
            horizontal=True,
            label_visibility="collapsed"
        )

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            display_stroke_card('Free', '#0c0599', 'freestyle-card', df, course_option)
            display_stroke_card('Breast', '#e8910c', 'breaststroke-card', df, course_option)
            display_stroke_card('IM', '#6b21a8', 'im-card', df, course_option)

        with col2:
            display_stroke_card('Back', '#00875a', 'backstroke-card', df, course_option)
            display_stroke_card('Fly', '#d94f1a', 'butterfly-card', df, course_option)

elif page == "Quick Lookup":
    st.title("Personal Best Quick Lookup")

    data = load_data()

    if data['swims'] is None:
        st.warning("No swim data found. Please upload data in the Upload Data section.")
    else:
        df = data['swims']

        # Key metrics as summary row
        st.markdown(render_summary_row([
            {"label": "Total Swims", "value": len(df)},
            {"label": "AAA", "value": len(df[df['Standard'] == 'AAA'])},
            {"label": "AA", "value": len(df[df['Standard'] == 'AA'])},
            {"label": "A", "value": len(df[df['Standard'] == 'A'])},
            {"label": "Current Age", "value": df['Age'].max()},
        ]), unsafe_allow_html=True)

        st.markdown("---")

        st.header("Personal Best Lookup")

        col1, col2, col3 = st.columns([2, 1, 2])

        pb_df = get_personal_bests(df)
        events = sorted(pb_df['Event'].unique()) if len(pb_df) > 0 else []

        with col1:
            if events:
                selected_event = st.selectbox("Select Event", events)
            else:
                st.info("No events with times yet")
                selected_event = None

        with col2:
            course = st.selectbox("Course", ['Yards', 'LCM'])

        if selected_event:
            pb_row = pb_df[(pb_df['Event'] == selected_event) & (pb_df['Course'] == course)]

            if len(pb_row) > 0:
                pb = pb_row.iloc[0]

                st.markdown("---")

                # PB details as summary row
                st.markdown(render_summary_row([
                    {"label": "Best Time", "value": pb['Time']},
                    {"label": "Standard", "value": pb['Standard']},
                    {"label": "Date", "value": pb['Date'].strftime('%m/%d/%Y')},
                    {"label": "Age", "value": pb['Age']},
                ]), unsafe_allow_html=True)

                # Progression chart in card
                st.markdown("---")
                st.markdown(card_open("Time Progression"), unsafe_allow_html=True)
                fig = create_progression_chart(df, selected_event, course)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                st.markdown(card_close(), unsafe_allow_html=True)

                # All times as styled table
                st.markdown("---")
                all_times = df[
                    (df['Distance'].astype(str) + ' ' + df['Stroke'] == selected_event) &
                    (df['Course'] == course)
                ].sort_values('Date', ascending=False)[['Date', 'Finals', 'Standard', 'Meet', 'Age']]

                st.markdown(
                    render_html_table(all_times, {
                        'Date': 'Date',
                        'Finals': 'Time',
                        'Standard': 'Standard',
                        'Meet': 'Meet',
                        'Age': 'Age'
                    }),
                    unsafe_allow_html=True
                )
            else:
                st.info(f"No times recorded for {selected_event} ({course})")

elif page == "Deep Analytics":
    st.title("Deep Analytics")

    data = load_data()

    if data['swims'] is None:
        st.warning("No swim data found.")
    else:
        df = data['swims']

        # Standards distribution
        st.markdown(card_open("Standards Distribution"), unsafe_allow_html=True)

        standards_count = df[df['Standard'] != 'Unrated']['Standard'].value_counts()

        fig = px.bar(
            x=standards_count.index,
            y=standards_count.values,
            labels={'x': 'Standard', 'y': 'Count'},
            title='Number of Swims by Standard',
            color=standards_count.index,
            color_discrete_map={
                'AAAA': '#FFD700',
                'AAA': '#C0C0C0',
                'AA': '#CD7F32',
                'A': '#0c0599',
                'BB': '#2d6bcf',
                'B': '#87CEEB'
            }
        )
        fig.update_layout(**PLOTLY_THEME)

        st.plotly_chart(fig, use_container_width=True)
        st.markdown(card_close(), unsafe_allow_html=True)

        st.markdown("---")

        # Stroke strength comparison
        st.markdown(card_open("Stroke Strength Comparison"), unsafe_allow_html=True)

        pb_df = get_personal_bests(df)

        stroke_standards = []
        for stroke in ['Free', 'Back', 'Breast', 'Fly', 'IM']:
            stroke_data = pb_df[pb_df['Event'].str.contains(stroke)]
            if len(stroke_data) > 0:
                aaa_count = len(stroke_data[stroke_data['Standard'] == 'AAA'])
                aa_count = len(stroke_data[stroke_data['Standard'] == 'AA'])
                a_count = len(stroke_data[stroke_data['Standard'] == 'A'])
                total_events = len(stroke_data)

                score = (aaa_count * 3 + aa_count * 2 + a_count * 1) / max(total_events, 1)

                stroke_standards.append({
                    'Stroke': stroke,
                    'Score': score
                })

        if stroke_standards:
            fig = go.Figure(data=go.Scatterpolar(
                r=[s['Score'] for s in stroke_standards],
                theta=[s['Stroke'] for s in stroke_standards],
                fill='toself',
                line_color='#0c0599'
            ))

            fig.update_layout(
                **PLOTLY_THEME,
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 3]
                    )
                ),
                showlegend=False,
                title="Strength by Stroke (AAA=3, AA=2, A=1)"
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown(card_close(), unsafe_allow_html=True)

        st.markdown("---")

        # Event progression analysis
        st.markdown(card_open("Event Progression Analysis"), unsafe_allow_html=True)

        events = sorted((df['Distance'].astype(str) + ' ' + df['Stroke']).unique())
        selected = st.selectbox("Select Event for Analysis", events)
        course_select = st.selectbox("Course", ['Yards', 'LCM'], key='analytics_course')

        if selected:
            dist, stroke = selected.split(' ', 1)
            event_data = df[
                (df['Distance'] == int(dist)) &
                (df['Stroke'] == stroke) &
                (df['Course'] == course_select)
            ].sort_values('Date')

            if len(event_data) > 1:
                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=event_data['Date'],
                    y=event_data['Time_Seconds'],
                    mode='lines+markers',
                    name='Time',
                    line=dict(color='#0c0599', width=3),
                    marker=dict(size=10, color='#2d6bcf'),
                    hovertemplate='<b>%{y:.2f}s</b><br>%{x|%b %d, %Y}<extra></extra>'
                ))

                fig.update_layout(
                    **PLOTLY_THEME,
                    title=f"{selected} ({course_select}) - Time Progression",
                    xaxis_title="Date",
                    yaxis_title="Time (seconds)",
                    height=400,
                    hovermode='closest',
                    yaxis=dict(autorange='reversed')
                )

                st.plotly_chart(fig, use_container_width=True)

                # Improvement chart
                event_data = event_data.copy()
                event_data['Improvement'] = event_data['Time_Seconds'].diff() * -1

                fig2 = go.Figure()

                fig2.add_trace(go.Bar(
                    x=event_data['Date'][1:],
                    y=event_data['Improvement'][1:],
                    marker_color=['#00875a' if x > 0 else '#d94f1a' for x in event_data['Improvement'][1:]],
                    name='Improvement'
                ))

                fig2.update_layout(
                    **PLOTLY_THEME,
                    title=f"{selected} - Improvement Between Swims",
                    xaxis_title="Date",
                    yaxis_title="Improvement (seconds)",
                    height=400,
                    hovermode='closest'
                )

                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Need at least 2 swims for this event to show progression")

        st.markdown(card_close(), unsafe_allow_html=True)

elif page == "Upload Data":
    st.title("Upload Swim Data")

    st.markdown("""
    Upload your graded swim data Excel file to update the tracker.

    **Expected format:** `graded_swim_data.xlsx`

    The file should contain columns for:
    - Date, Age, Distance, Stroke, Course, Finals, Time_Seconds, Standard, Meet
    """)

    uploaded_file = st.file_uploader("Choose graded_swim_data.xlsx file", type=['xlsx'])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)

            required_cols = ['Date', 'Age', 'Distance', 'Stroke', 'Course', 'Finals', 'Time_Seconds', 'Standard', 'Meet']
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
            else:
                df.to_excel('graded_swim_data.xlsx', index=False)
                st.success("Data uploaded successfully!")

                # Data preview as styled table
                st.subheader("Data Preview")
                st.markdown(render_html_table(df.head(10)), unsafe_allow_html=True)

                # Summary stats
                st.markdown(render_summary_row([
                    {"label": "Total Swims", "value": len(df)},
                    {"label": "Date Range", "value": f"{df['Date'].min()} to {df['Date'].max()}"},
                    {"label": "Unique Events", "value": len(df.groupby(['Distance', 'Stroke']))},
                ]), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error reading file: {e}")

    st.markdown("---")

    st.header("Merge High School Data")

    st.markdown("""
    Upload high school swim data (CSV format) to merge with GoMotion data.

    **Expected format:**
    - Date, Age, Distance, Stroke, Course, Time, Meet
    """)

    hs_file = st.file_uploader("Choose high school CSV file", type=['csv'])

    if hs_file is not None:
        try:
            hs_df = pd.read_csv(hs_file)
            st.success("High school data loaded!")

            if st.button("Merge with Existing Data"):
                st.info("Merge functionality coming soon - requires grader.py integration")

        except Exception as e:
            st.error(f"Error reading file: {e}")

elif page == "Goals":
    st.title("Season Goals")

    data = load_data()

    if data['swims'] is None:
        st.warning("No swim data found. Upload data first.")
    else:
        df = data['swims']
        pb_df = get_personal_bests(df)

        if os.path.exists('goals.csv'):
            goals_df = pd.read_csv('goals.csv')
        else:
            goals_df = pd.DataFrame(columns=['Event', 'Course', 'Goal_Time_Seconds', 'Goal_Standard', 'Notes'])

        st.header("Current Goals")

        if len(goals_df) > 0:
            for idx, goal in goals_df.iterrows():
                pb_row = pb_df[(pb_df['Event'] == goal['Event']) & (pb_df['Course'] == goal['Course'])]

                if len(pb_row) > 0:
                    pb = pb_row.iloc[0]
                    current = pb['Seconds']
                    goal_time = goal['Goal_Time_Seconds']
                    to_drop = current - goal_time

                    if to_drop <= 0:
                        status_text = "<span style='color:#00875a; font-weight:600;'>Goal Achieved</span>"
                    elif to_drop <= 1:
                        status_text = "<span style='color:#e8910c; font-weight:600;'>Almost There</span>"
                    else:
                        status_text = f"{to_drop:.2f}s to drop"

                    html = (
                        f"<div class='pro-card'>"
                        f"<div class='pro-card-header'>{goal['Event']} ({goal['Course']})</div>"
                        f"<table class='pro-table'>"
                        f"<thead><tr><th>Current Best</th><th>Goal</th><th>Time to Drop</th><th>Status</th></tr></thead>"
                        f"<tbody><tr>"
                        f"<td style='font-weight:600;'>{current:.2f}s</td>"
                        f"<td>{goal_time:.2f}s</td>"
                        f"<td>{to_drop:.2f}s</td>"
                        f"<td>{status_text}</td>"
                        f"</tr></tbody>"
                        f"</table>"
                        f"</div>"
                    )
                    st.markdown(html, unsafe_allow_html=True)

                    if to_drop > 0:
                        progress = max(0, 1 - (to_drop / max(to_drop, 5)))
                        st.progress(progress)
                    else:
                        st.progress(1.0)
                else:
                    st.markdown(
                        f"<div class='pro-card'>"
                        f"<div class='pro-card-header'>{goal['Event']} ({goal['Course']})</div>"
                        f"<p style='color:var(--text-secondary);'>No current time for this event yet.</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                if goal.get('Notes') and pd.notna(goal.get('Notes')):
                    st.caption(goal['Notes'])
        else:
            st.info("No goals set yet. Add some goals below.")

        st.markdown("---")

        # Add new goal
        st.header("Add New Goal")

        st.markdown(card_open(), unsafe_allow_html=True)
        with st.form("add_goal"):
            col1, col2 = st.columns(2)

            with col1:
                goal_event = st.text_input("Event", placeholder="e.g., 100 Free")
                goal_course = st.selectbox("Course", ['Yards', 'LCM'])
                goal_time_input = st.text_input("Goal Time", placeholder="e.g., 50.00 or 1:45.00")

            with col2:
                goal_standard = st.selectbox("Target Standard", ['AAAA', 'AAA', 'AA', 'A', 'BB', 'B', ''], index=6)
                goal_notes = st.text_input("Notes", placeholder="e.g., Winter Championships")

            if st.form_submit_button("Add Goal", type="primary"):
                try:
                    if ':' in goal_time_input:
                        parts = goal_time_input.split(':')
                        goal_seconds = float(parts[0]) * 60 + float(parts[1])
                    else:
                        goal_seconds = float(goal_time_input)

                    new_goal = pd.DataFrame([{
                        'Event': goal_event,
                        'Course': goal_course,
                        'Goal_Time_Seconds': goal_seconds,
                        'Goal_Standard': goal_standard,
                        'Notes': goal_notes
                    }])

                    goals_df = pd.concat([goals_df, new_goal], ignore_index=True)
                    goals_df.to_csv('goals.csv', index=False)

                    st.success("Goal added!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {e}")
        st.markdown(card_close(), unsafe_allow_html=True)

elif page == "Settings":
    st.title("Settings")

    st.markdown(card_open("Data Management"), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download All Data"):
            st.info("Feature coming soon")
    with col2:
        if st.button("Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared")
    st.markdown(card_close(), unsafe_allow_html=True)

    st.markdown(card_open("About"), unsafe_allow_html=True)
    st.markdown("""
    **Swim Performance Tracker** -- Version 2.0

    Track and analyze competitive swimming performance using USA Swimming standards.

    - **Stroke Overview** -- Best times by stroke at a glance
    - **Deep Analytics** -- Advanced performance analysis
    - GoMotion and high school data import
    - Personal best tracking
    - Goal setting and progress monitoring
    - Interactive visualizations

    Built with Streamlit and Python
    """)
    st.markdown(card_close(), unsafe_allow_html=True)

# Footer
st.markdown(
    "<div class='pro-footer'>Swim Performance Tracker  |  Built with Python and Streamlit</div>",
    unsafe_allow_html=True
)
