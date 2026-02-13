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
    page_icon="🏊‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-blue: #0066CC;
        --secondary-blue: #00A3E0;
        --dark-blue: #003D66;
        --light-blue: #E6F3FF;
        --gold: #FFD700;
        --silver: #C0C0C0;
        --bronze: #CD7F32;
        --freestyle-blue: #0066CC;
        --backstroke-green: #00A651;
        --breaststroke-yellow: #FFA500;
        --butterfly-orange: #FF6B35;
        --im-purple: #7B2CBF;
    }
    
    /* Headers */
    h1 {
        color: var(--dark-blue);
        font-weight: 700;
        padding-bottom: 1rem;
        border-bottom: 3px solid var(--primary-blue);
    }
    
    h2 {
        color: var(--primary-blue);
        font-weight: 600;
        margin-top: 2rem;
    }
    
    h3 {
        color: var(--secondary-blue);
        font-weight: 500;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-blue);
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: var(--dark-blue);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F8FBFF;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: var(--primary-blue);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
    }
    
    .stButton>button:hover {
        background-color: var(--dark-blue);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--secondary-blue);
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Dataframe */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Stroke cards */
    .stroke-card {
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .freestyle-card { border-left: 5px solid var(--freestyle-blue); }
    .backstroke-card { border-left: 5px solid var(--backstroke-green); }
    .breaststroke-card { border-left: 5px solid var(--breaststroke-yellow); }
    .butterfly-card { border-left: 5px solid var(--butterfly-orange); }
    .im-card { border-left: 5px solid var(--im-purple); }
    
    /* Standard badges */
    .standard-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.2rem;
    }
    
    .standard-AAAA { background-color: #FFD700; color: #000; }
    .standard-AAA { background-color: #C0C0C0; color: #000; }
    .standard-AA { background-color: #CD7F32; color: #FFF; }
    .standard-A { background-color: #0066CC; color: #FFF; }
    .standard-BB { background-color: #00A3E0; color: #FFF; }
    .standard-B { background-color: #87CEEB; color: #000; }
</style>
""", unsafe_allow_html=True)

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
    
    # Define distance sets for each stroke type
    if stroke == 'Free':
        distances = [50, 100, 200, 500]
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

def create_progression_chart(df, event, course):
    """Create time progression chart for an event"""
    event_data = df[
        (df['Distance'].astype(str) + ' ' + df['Stroke'] == event) & 
        (df['Course'] == course)
    ].sort_values('Date')
    
    if len(event_data) == 0:
        return None
    
    fig = go.Figure()
    
    # Add line trace
    fig.add_trace(go.Scatter(
        x=event_data['Date'],
        y=event_data['Time_Seconds'],
        mode='lines+markers',
        name='Time',
        line=dict(color='#0066CC', width=3),
        marker=dict(size=8, color='#00A3E0'),
        hovertemplate='<b>%{y:.2f}s</b><br>%{x|%b %d, %Y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'{event} ({course}) Progression',
        xaxis_title='Date',
        yaxis_title='Time (seconds)',
        hovermode='closest',
        height=400,
        template='plotly_white',
        font=dict(size=12),
        yaxis=dict(autorange='reversed')  # Lower times are better
    )
    
    return fig

def display_stroke_card(stroke, color, df, course):
    """Display a stroke summary card"""
    stroke_data = get_stroke_bests(df, stroke, course)
    
    if not stroke_data:
        return  # Don't show card if no data
    
    st.markdown(f"### {stroke}")
    
    # Create DataFrame for display
    display_df = pd.DataFrame(stroke_data)
    
    # Format the table with colored badges
    for idx, row in display_df.iterrows():
        col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
        
        with col1:
            st.markdown(f"**{row['Distance']}**")
        with col2:
            st.markdown(f"`{row['Time']}`")
        with col3:
            # Color-coded standard badge
            st.markdown(
                f"<span class='standard-badge standard-{row['Standard']}'>{row['Standard']}</span>",
                unsafe_allow_html=True
            )
        with col4:
            st.markdown(f"*{row['Date']}*")

# Sidebar
with st.sidebar:
    st.image("https://api.dicebear.com/7.x/shapes/svg?seed=swim&backgroundColor=0066CC", width=100)
    st.title("🏊‍♂️ Swim Tracker")
    
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏊 Stroke Overview", "🔍 Quick Lookup", "📊 Deep Analytics", "🎯 Goals", "📁 Upload Data", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick stats in sidebar
    data = load_data()
    if data['swims'] is not None:
        st.metric("Total Swims", len(data['swims']))
        st.metric("AAA Times", len(data['swims'][data['swims']['Standard'] == 'AAA']))
        st.metric("AA Times", len(data['swims'][data['swims']['Standard'] == 'AA']))

# Main content
if page == "🏊 Stroke Overview":
    st.title("🏊‍♂️ Stroke Overview")
    
    data = load_data()
    
    if data['swims'] is None:
        st.warning("⚠️ No swim data found. Please upload data in the 'Upload Data' section.")
    else:
        df = data['swims']
        
        # Course toggle at the top
        st.markdown("### Select Course")
        course_option = st.radio(
            "Course Type",
            ["Yards", "LCM"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Create 5 stroke cards in a grid
        col1, col2 = st.columns(2)
        
        with col1:
            # Freestyle
            with st.container():
                st.markdown("<div class='stroke-card freestyle-card'>", unsafe_allow_html=True)
                display_stroke_card('Free', '#0066CC', df, course_option)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Breaststroke
            with st.container():
                st.markdown("<div class='stroke-card breaststroke-card'>", unsafe_allow_html=True)
                display_stroke_card('Breast', '#FFA500', df, course_option)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # IM
            with st.container():
                st.markdown("<div class='stroke-card im-card'>", unsafe_allow_html=True)
                display_stroke_card('IM', '#7B2CBF', df, course_option)
                st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            # Backstroke
            with st.container():
                st.markdown("<div class='stroke-card backstroke-card'>", unsafe_allow_html=True)
                display_stroke_card('Back', '#00A651', df, course_option)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Butterfly
            with st.container():
                st.markdown("<div class='stroke-card butterfly-card'>", unsafe_allow_html=True)
                display_stroke_card('Fly', '#FF6B35', df, course_option)
                st.markdown("</div>", unsafe_allow_html=True)

elif page == "🔍 Quick Lookup":
    st.title("🔍 Personal Best Quick Lookup")
    
    data = load_data()
    
    if data['swims'] is None:
        st.warning("⚠️ No swim data found. Please upload data in the 'Upload Data' section.")
    else:
        df = data['swims']
        
        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Swims", len(df))
        with col2:
            st.metric("AAA", len(df[df['Standard'] == 'AAA']))
        with col3:
            st.metric("AA", len(df[df['Standard'] == 'AA']))
        with col4:
            st.metric("A", len(df[df['Standard'] == 'A']))
        with col5:
            current_age = df['Age'].max()
            st.metric("Current Age", current_age)
        
        st.markdown("---")
        
        # Personal Best Lookup
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
                
                # Display PB details
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Best Time", pb['Time'])
                with col2:
                    st.metric("Standard", pb['Standard'])
                with col3:
                    st.metric("Date", pb['Date'].strftime('%m/%d/%Y'))
                with col4:
                    st.metric("Age", pb['Age'])
                
                # Show progression chart
                st.markdown("---")
                fig = create_progression_chart(df, selected_event, course)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Show all times for this event
                st.markdown("---")
                st.subheader("All Times")
                
                all_times = df[
                    (df['Distance'].astype(str) + ' ' + df['Stroke'] == selected_event) & 
                    (df['Course'] == course)
                ].sort_values('Date', ascending=False)[['Date', 'Finals', 'Standard', 'Meet', 'Age']]
                
                st.dataframe(all_times, use_container_width=True, hide_index=True)
            else:
                st.info(f"No times recorded for {selected_event} ({course})")

elif page == "📊 Deep Analytics":
    st.title("📊 Deep Analytics")
    
    data = load_data()
    
    if data['swims'] is None:
        st.warning("⚠️ No swim data found.")
    else:
        df = data['swims']
        
        # Standards distribution
        st.header("Standards Distribution")
        
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
                'A': '#0066CC',
                'BB': '#00A3E0',
                'B': '#87CEEB'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Event comparison
        st.header("Stroke Strength Comparison")
        
        pb_df = get_personal_bests(df)
        
        # Create radar chart of standards by stroke
        stroke_standards = []
        for stroke in ['Free', 'Back', 'Breast', 'Fly', 'IM']:
            stroke_data = pb_df[pb_df['Event'].str.contains(stroke)]
            if len(stroke_data) > 0:
                # Count AAA, AA, A times
                aaa_count = len(stroke_data[stroke_data['Standard'] == 'AAA'])
                aa_count = len(stroke_data[stroke_data['Standard'] == 'AA'])
                a_count = len(stroke_data[stroke_data['Standard'] == 'A'])
                total_events = len(stroke_data)
                
                # Calculate score
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
                line_color='#0066CC'
            ))
            
            fig.update_layout(
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
        
        st.markdown("---")
        
        # Improvement over time
        st.header("Event Progression Analysis")
        
        # Select event for timeline
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
                # Time progression
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=event_data['Date'],
                    y=event_data['Time_Seconds'],
                    mode='lines+markers',
                    name='Time',
                    line=dict(color='#0066CC', width=3),
                    marker=dict(size=10, color='#00A3E0'),
                    hovertemplate='<b>%{y:.2f}s</b><br>%{x|%b %d, %Y}<extra></extra>'
                ))
                
                fig.update_layout(
                    title=f"{selected} ({course_select}) - Time Progression",
                    xaxis_title="Date",
                    yaxis_title="Time (seconds)",
                    height=400,
                    hovermode='closest',
                    yaxis=dict(autorange='reversed')
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate improvement
                event_data['Improvement'] = event_data['Time_Seconds'].diff() * -1  # Negative diff = faster
                
                fig2 = go.Figure()
                
                fig2.add_trace(go.Bar(
                    x=event_data['Date'][1:],
                    y=event_data['Improvement'][1:],
                    marker_color=['green' if x > 0 else 'red' for x in event_data['Improvement'][1:]],
                    name='Improvement'
                ))
                
                fig2.update_layout(
                    title=f"{selected} - Improvement Between Swims",
                    xaxis_title="Date",
                    yaxis_title="Improvement (seconds)",
                    height=400,
                    hovermode='closest'
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Need at least 2 swims for this event to show progression")

elif page == "📁 Upload Data":
    st.title("📁 Upload Swim Data")
    
    st.markdown("""
    Upload your graded swim data Excel file to update the tracker.
    
    **Expected format:** `graded_swim_data.xlsx`
    
    The file should contain columns for:
    - Date, Age, Distance, Stroke, Course, Finals, Time_Seconds, Standard, Meet
    """)
    
    uploaded_file = st.file_uploader("Choose graded_swim_data.xlsx file", type=['xlsx'])
    
    if uploaded_file is not None:
        try:
            # Read the uploaded file
            df = pd.read_excel(uploaded_file)
            
            # Validate columns
            required_cols = ['Date', 'Age', 'Distance', 'Stroke', 'Course', 'Finals', 'Time_Seconds', 'Standard', 'Meet']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
            else:
                # Save the file
                df.to_excel('graded_swim_data.xlsx', index=False)
                st.success("✅ Data uploaded successfully!")
                
                # Show preview
                st.subheader("Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Show summary stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Swims", len(df))
                with col2:
                    st.metric("Date Range", f"{df['Date'].min()} to {df['Date'].max()}")
                with col3:
                    st.metric("Unique Events", len(df.groupby(['Distance', 'Stroke'])))
                
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
    
    st.markdown("---")
    
    # High School swim merging section
    st.header("🏫 Merge High School Data")
    
    st.markdown("""
    Upload high school swim data (CSV format) to merge with GoMotion data.
    
    **Expected format:**
    - Date, Age, Distance, Stroke, Course, Time, Meet
    """)
    
    hs_file = st.file_uploader("Choose high school CSV file", type=['csv'])
    
    if hs_file is not None:
        try:
            hs_df = pd.read_csv(hs_file)
            st.success("✅ High school data loaded!")
            
            if st.button("Merge with Existing Data"):
                # Logic to merge and regrade would go here
                st.info("Merge functionality coming soon - requires grader.py integration")
                
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")

elif page == "🎯 Goals":
    st.title("🎯 Season Goals")
    
    data = load_data()
    
    if data['swims'] is None:
        st.warning("⚠️ No swim data found. Upload data first.")
    else:
        df = data['swims']
        pb_df = get_personal_bests(df)
        
        # Load goals
        if os.path.exists('goals.csv'):
            goals_df = pd.read_csv('goals.csv')
        else:
            goals_df = pd.DataFrame(columns=['Event', 'Course', 'Goal_Time_Seconds', 'Goal_Standard', 'Notes'])
        
        # Display goals
        st.header("Current Goals")
        
        if len(goals_df) > 0:
            for idx, goal in goals_df.iterrows():
                with st.container():
                    st.markdown(f"### {goal['Event']} ({goal['Course']})")
                    
                    # Get current best
                    pb_row = pb_df[(pb_df['Event'] == goal['Event']) & (pb_df['Course'] == goal['Course'])]
                    
                    if len(pb_row) > 0:
                        pb = pb_row.iloc[0]
                        current = pb['Seconds']
                        goal_time = goal['Goal_Time_Seconds']
                        to_drop = current - goal_time
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Current Best", f"{current:.2f}s")
                        with col2:
                            st.metric("Goal", f"{goal_time:.2f}s")
                        with col3:
                            delta_color = "inverse" if to_drop > 0 else "normal"
                            st.metric("To Drop", f"{to_drop:.2f}s", delta=None)
                        with col4:
                            if to_drop <= 0:
                                st.success("🎉 Goal Achieved!")
                            elif to_drop <= 1:
                                st.warning("🔥 So Close!")
                            else:
                                st.info(f"📊 Keep Working!")
                        
                        # Progress bar
                        if to_drop > 0:
                            progress = max(0, 1 - (to_drop / max(to_drop, 5)))  # Cap at 5 seconds for visualization
                            st.progress(progress)
                        else:
                            st.progress(1.0)
                    else:
                        st.info("No current time for this event yet.")
                    
                    if goal.get('Notes'):
                        st.caption(f"📝 {goal['Notes']}")
                    
                    st.markdown("---")
        else:
            st.info("No goals set yet. Add some goals below!")
        
        # Add new goal
        st.header("Add New Goal")
        
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
                    # Parse goal time
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
                    
                    st.success("✅ Goal added!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")

elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    
    st.header("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download All Data"):
            # Create zip of all data files
            st.info("Feature coming soon!")
    
    with col2:
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.success("✅ Cache cleared!")
    
    st.markdown("---")
    
    st.header("About")
    
    st.markdown("""
    **Swim Performance Tracker**
    
    Version 2.0
    
    This app helps track and analyze competitive swimming performance using USA Swimming standards.
    
    Features:
    - **Stroke Overview** - Quick view of best times by stroke
    - **Deep Analytics** - Advanced performance analysis
    - GoMotion data import
    - High school swim tracking
    - Personal best tracking
    - Goal setting and progress monitoring
    - Interactive visualizations
    
    Built with Streamlit and Python 🐍
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "🏊‍♂️ Swim Performance Tracker | Made with ❤️ and Python"
    "</div>",
    unsafe_allow_html=True
)
