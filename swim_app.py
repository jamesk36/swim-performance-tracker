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

# Sidebar
with st.sidebar:
    st.image("https://api.dicebear.com/7.x/shapes/svg?seed=swim&backgroundColor=0066CC", width=100)
    st.title("🏊‍♂️ Swim Tracker")
    
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "📁 Upload Data", "🎯 Goals", "📈 Analytics", "⚙️ Settings"],
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
if page == "📊 Dashboard":
    st.title("🏊‍♂️ Swim Performance Dashboard")
    
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
        st.header("🔍 Personal Best Lookup")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        pb_df = get_personal_bests(df)
        events = sorted(pb_df['Event'].unique()) if len(pb_df) > 0 else []
        
        with col1:
            selected_event = st.selectbox("Select Event", events, index=events.index('100 Free') if '100 Free' in events else 0)
        
        with col2:
            selected_course = st.selectbox("Select Course", ['Yards', 'LCM'])
        
        if len(pb_df) > 0:
            pb_row = pb_df[(pb_df['Event'] == selected_event) & (pb_df['Course'] == selected_course)]
            
            if len(pb_row) > 0:
                pb = pb_row.iloc[0]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Best Time", pb['Time'])
                with col2:
                    st.metric("Standard", pb['Standard'])
                with col3:
                    st.metric("Date", pb['Date'].strftime('%m/%d/%Y'))
            else:
                st.info("No personal best for this event/course combination.")
        
        st.markdown("---")
        
        # Time Progression
        st.header("📈 Time Progression")
        
        if selected_event and selected_course:
            chart = create_progression_chart(df, selected_event, selected_course)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("No data available for this event/course combination.")
        
        st.markdown("---")
        
        # Standards Distribution
        st.header("📊 Standards Distribution")
        
        standards_counts = df['Standard'].value_counts().reset_index()
        standards_counts.columns = ['Standard', 'Count']
        
        # Order standards properly
        standard_order = ['AAAA', 'AAA', 'AA', 'A', 'BB', 'B', '<B', 'Unrated']
        standards_counts['Standard'] = pd.Categorical(
            standards_counts['Standard'],
            categories=standard_order,
            ordered=True
        )
        standards_counts = standards_counts.sort_values('Standard')
        
        fig = px.bar(
            standards_counts,
            x='Standard',
            y='Count',
            color='Standard',
            color_discrete_map={
                'AAAA': '#FFD700',
                'AAA': '#C0C0C0',
                'AA': '#CD7F32',
                'A': '#4472C4',
                'BB': '#70AD47',
                'B': '#FFC000',
                '<B': '#E7E6E6',
                'Unrated': '#D9D9D9'
            }
        )
        
        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="Standard",
            yaxis_title="Number of Swims"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Recent Swims
        st.header("🏊 Recent Swims")
        
        recent = df.sort_values('Date', ascending=False).head(10)
        st.dataframe(
            recent[['Date', 'Distance', 'Stroke', 'Course', 'Finals', 'Standard', 'Meet']],
            hide_index=True,
            use_container_width=True
        )

elif page == "📁 Upload Data":
    st.title("📁 Upload Swim Data")
    
    st.markdown("""
    Upload your GoMotion results and add high school swims to process and analyze your data.
    """)
    
    # GoMotion Upload
    st.header("1️⃣ Upload GoMotion Results")
    
    uploaded_file = st.file_uploader(
        "Upload swim_history.html from GoMotion",
        type=['html'],
        help="Save the GoMotion results page as HTML and upload it here"
    )
    
    if uploaded_file:
        st.success(f"✅ Uploaded: {uploaded_file.name}")
        
        # Save the file
        with open('swim_history.html', 'wb') as f:
            f.write(uploaded_file.getbuffer())
      
    if st.button("🔄 Process GoMotion Data", type="primary"):
    with st.spinner("Processing data..."):
        # Import and run scripts
        import subprocess
        
        progress_bar = st.progress(0)
        status = st.empty()
        
        # Run scraper
        status.text("⏳ Extracting data from HTML...")
        result = subprocess.run(['python', 'scraper.py'], capture_output=True, text=True)  
       
                if result.returncode == 0:
                    st.success("✅ Data extracted successfully")
                    progress_bar.progress(33)
                else:
                    st.error(f"❌ Scraper failed: {result.stderr}")
                    st.stop()
                
                # Run cleaner
                status.text("⏳ Cleaning and formatting data...")
                result = subprocess.run(['python', 'cleaner.py'], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Data cleaned successfully")
                    progress_bar.progress(66)
                else:
                    st.error(f"❌ Cleaner failed: {result.stderr}")
                    st.stop()
                
                # Run grader
                status.text("⏳ Grading performances...")
                result = subprocess.run(['python', 'grader.py'], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Data graded successfully")
                    progress_bar.progress(100)
                    st.balloons()
                    status.text("✨ All done! Check the Dashboard to see your results.")
                else:
                    st.error(f"❌ Grader failed: {result.stderr}")
    
    st.markdown("---")
    
    # High School Swims
    st.header("2️⃣ Add High School Swims")
    
    st.markdown("""
    Enter high school swims that aren't in GoMotion. These will be merged with your GoMotion data.
    """)
    
    # Load existing high school swims
    if os.path.exists('high_school_swims.csv'):
        hs_df = pd.read_csv('high_school_swims.csv')
    else:
        hs_df = pd.DataFrame(columns=['Date', 'Age', 'Distance', 'Stroke', 'Round', 'Course', 'Finals', 'Time_Seconds', 'Meet'])
    
    # Show existing swims
    if len(hs_df) > 0:
        st.subheader("Existing High School Swims")
        st.dataframe(hs_df, use_container_width=True, hide_index=True)
    
    # Add new swim form
    with st.expander("➕ Add New High School Swim"):
        with st.form("add_hs_swim"):
            col1, col2 = st.columns(2)
            
            with col1:
                swim_date = st.date_input("Date", datetime.now())
                age = st.number_input("Age", min_value=8, max_value=18, value=14)
                distance = st.selectbox("Distance", [25, 50, 100, 200, 400, 500, 800, 1000, 1500, 1650])
                stroke = st.selectbox("Stroke", ['Free', 'Back', 'Breast', 'Fly', 'IM'])
            
            with col2:
                round_type = st.selectbox("Round", ['Finals', 'Prelims'])
                course = st.selectbox("Course", ['Yards', 'LCM'])
                time_input = st.text_input("Time", placeholder="e.g., 52.45 or 1:02.34")
                meet = st.text_input("Meet Name", placeholder="e.g., HS Dual Meet vs Rogers")
            
            submitted = st.form_submit_button("Add Swim", type="primary")
            
            if submitted:
                # Parse time
                try:
                    if ':' in time_input:
                        parts = time_input.split(':')
                        time_seconds = float(parts[0]) * 60 + float(parts[1])
                    else:
                        time_seconds = float(time_input)
                    
                    finals_str = f"{time_input}{'Y' if course == 'Yards' else 'L'}"
                    
                    # Add to dataframe
                    new_swim = pd.DataFrame([{
                        'Date': swim_date.strftime('%Y-%m-%d'),
                        'Age': age,
                        'Distance': distance,
                        'Stroke': stroke,
                        'Round': round_type,
                        'Course': course,
                        'Finals': finals_str,
                        'Time_Seconds': time_seconds,
                        'Meet': meet
                    }])
                    
                    hs_df = pd.concat([hs_df, new_swim], ignore_index=True)
                    hs_df.to_csv('high_school_swims.csv', index=False)
                    
                    st.success("✅ Swim added! Run merge below to include it.")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error adding swim: {e}")
    
    if len(hs_df) > 0:
        if st.button("🔄 Merge High School Swims", type="primary"):
            with st.spinner("Merging data..."):
                result = subprocess.run(['python', 'merge_swims.py'], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ High school swims merged!")
                    st.info("💡 Now run 'python grader.py' and 'python create_dashboard.py' from terminal to update.")
                else:
                    st.error(f"❌ Merge failed: {result.stderr}")

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
                            # Still working toward goal
                            st.progress(0)
                        else:
                            # Goal achieved or exceeded
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

elif page == "📈 Analytics":
    st.title("📈 Advanced Analytics")
    
    data = load_data()
    
    if data['swims'] is None:
        st.warning("⚠️ No swim data found.")
    else:
        df = data['swims']
        
        # Event comparison
        st.header("Event Comparison")
        
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
                title="Strength by Stroke"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Improvement over time
        st.header("Improvement Timeline")
        
        # Select event for timeline
        events = sorted((df['Distance'].astype(str) + ' ' + df['Stroke']).unique())
        selected = st.selectbox("Select Event", events)
        
        if selected:
            dist, stroke = selected.split(' ', 1)
            event_data = df[
                (df['Distance'] == int(dist)) & 
                (df['Stroke'] == stroke)
            ].sort_values('Date')
            
            if len(event_data) > 1:
                # Calculate improvement
                event_data['Improvement'] = event_data['Time_Seconds'].diff() * -1  # Negative diff = faster
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=event_data['Date'],
                    y=event_data['Improvement'],
                    mode='lines+markers',
                    name='Improvement',
                    fill='tozeroy',
                    line=dict(color='#00A3E0', width=2),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title=f"{selected} - Improvement per Swim",
                    xaxis_title="Date",
                    yaxis_title="Improvement (seconds)",
                    height=400,
                    hovermode='closest'
                )
                
                st.plotly_chart(fig, use_container_width=True)

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
    
    Version 1.0
    
    This app helps track and analyze competitive swimming performance using USA Swimming standards.
    
    Features:
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
