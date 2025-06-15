import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Simlane Analytics Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        background-color: #4A7BFF;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        width: 100%;
    }
    .login-container {
        max-width: 400px;
        margin: auto;
        padding: 2rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZATION AND DATA FUNCTIONS
# ============================================================================

def init_session_state():
    """Initialize all session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'setup_complete' not in st.session_state:
        st.session_state.setup_complete = False
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'member_data' not in st.session_state:
        st.session_state.member_data = None
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = False

def generate_demo_data():
    """Generate demo data for testing"""
    np.random.seed(42)
    n_members = 500
    
    data = {
        'member_id': [f'M{str(i).zfill(4)}' for i in range(n_members)],
        'group_id': [f'G{np.random.randint(1, 20)}' for _ in range(n_members)],
        'enrollment_date': pd.date_range(end=datetime.now(), periods=n_members).tolist(),
        'tenure_days': np.random.randint(1, 1000, n_members),
        'virtual_care_visits': np.random.poisson(2, n_members),
        'in_person_visits': np.random.poisson(3, n_members),
        'lifetime_value': np.random.uniform(1000, 10000, n_members),
        'estimated_days_to_churn': np.random.choice([30, 60, 90, 180, 365], n_members, p=[0.2, 0.2, 0.2, 0.2, 0.2]),
        'risk_score': np.random.uniform(0, 1, n_members),
        'segment': np.random.choice(['Emerging', 'Stable', 'At-Risk', 'High-Value'], n_members)
    }
    
    df = pd.DataFrame(data)
    
    # Assign risk levels based on risk score
    df['risk_level'] = pd.cut(df['risk_score'], 
                              bins=[0, 0.25, 0.5, 0.75, 1.0],
                              labels=['Low', 'Medium', 'High', 'Immediate'])
    
    # Convert enrollment_date to datetime
    df['enrollment_date'] = pd.to_datetime(df['enrollment_date'])
    
    return df

# ============================================================================
# LOGIN AND AUTHENTICATION
# ============================================================================

def show_login():
    """Display login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <div style='background-color: #D4E6D3; padding: 2rem; border-radius: 12px; display: inline-block;'>
                <h1 style='color: #2E7D32; font-size: 3rem; margin: 0;'>🎯 Simlane</h1>
            </div>
            <h3 style='color: #666; margin-top: 1rem;'>Advanced Member Analytics Platform</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Sign In", use_container_width=True):
                    if username and password:
                        st.session_state.logged_in = True
                        st.session_state.setup_complete = True
                        st.rerun()
            
            with col2:
                if st.button("Use Demo Data", use_container_width=True, type="secondary"):
                    st.session_state.logged_in = True
                    st.session_state.demo_mode = True
                    st.session_state.member_data = generate_demo_data()
                    st.session_state.setup_complete = True
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: CHURN PREDICTIONS
# ============================================================================

def show_churn_predictions():
    """Display churn predictions page"""
    st.title("🎯 Churn Predictions")
    st.markdown("AI-powered member retention insights and risk analysis")
    
    df = st.session_state.member_data
    
    # Ensure risk_level column exists
    if 'risk_level' not in df.columns:
        df['risk_level'] = pd.cut(df['risk_score'], 
                                  bins=[0, 0.25, 0.5, 0.75, 1.0],
                                  labels=['Low', 'Medium', 'High', 'Immediate'])
    
    # Risk summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    risk_counts = df['risk_level'].value_counts()
    
    with col1:
        st.metric("🔴 Immediate Risk", 
                  risk_counts.get('Immediate', 0),
                  "Next 30 days")
    with col2:
        st.metric("🟠 High Risk", 
                  risk_counts.get('High', 0),
                  "30-90 days")
    with col3:
        st.metric("🔵 Medium Risk", 
                  risk_counts.get('Medium', 0),
                  "90-180 days")
    with col4:
        st.metric("🟢 Low Risk", 
                  risk_counts.get('Low', 0),
                  "180+ days")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### How many members fall into each risk bucket?")
        
        fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            color=risk_counts.index,
            color_discrete_map={
                'Immediate': '#FF4B4B',
                'High': '#FF8C00',
                'Medium': '#4A7BFF',
                'Low': '#28A745'
            }
        )
        fig.update_layout(showlegend=False, xaxis_title="Risk Category", yaxis_title="Number of Members")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### When will members likely churn?")
        
        churn_dist = df['estimated_days_to_churn'].value_counts().sort_index()
        fig = px.bar(
            x=churn_dist.index,
            y=churn_dist.values,
            color_discrete_sequence=['#4A7BFF']
        )
        fig.update_layout(xaxis_title="Days Until Churn", yaxis_title="Number of Members")
        st.plotly_chart(fig, use_container_width=True)
    
    # High-Priority Members table
    st.markdown("### 🎯 High-Priority Members")
    st.markdown("Members at immediate risk - take action now")
    
    # Filter controls
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search members", placeholder="Showing only HIGH risk members")
    with col2:
        if st.button("Clear filter"):
            st.rerun()
    
    # Display high-risk members
    high_risk = df[df['risk_level'].isin(['Immediate', 'High'])].head(10)
    
    if len(high_risk) > 0:
        # Create display dataframe
        display_data = {
            'Member ID': high_risk['member_id'].tolist(),
            'Group': high_risk['group_id'].tolist(),
            'Risk': high_risk['risk_level'].tolist(),
            'Days to Churn': high_risk['estimated_days_to_churn'].tolist(),
            'Tenure': (high_risk['tenure_days'].astype(str) + ' days').tolist(),
            'Visits': (high_risk['virtual_care_visits'] + high_risk['in_person_visits']).tolist(),
            'Value': ('$' + high_risk['lifetime_value'].round(2).astype(str)).tolist(),
            'Actions': ['View Details'] * len(high_risk)
        }
        display_df = pd.DataFrame(display_data)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No high-risk members found.")

# ============================================================================
# PAGE: CUSTOMER SEGMENTS
# ============================================================================

def show_customer_segments():
    """Display customer segments page"""
    st.title("👥 Customer Segments")
    st.markdown("Deep dive into customer segmentation and behavioral patterns")
    
    df = st.session_state.member_data
    
    # Segment insights cards
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info("✅ Cluster 3 has the highest average lifetime value at $1,258")
        st.warning("⚠️ Cluster 0 has the highest churn rate at 32.5%")
    
    # Segment visualization
    st.markdown("### 📊 Member Engagement Patterns")
    
    # Create scatter plot
    fig = px.scatter(
        df,
        x='tenure_days',
        y='virtual_care_visits',
        color='segment',
        size='lifetime_value',
        hover_data=['member_id', 'risk_level'],
        title="Usage vs Tenure by Segment"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Segment overview table
    st.markdown("### 📊 Segment Overview")
    
    segment_summary = df.groupby('segment').agg({
        'member_id': 'count',
        'tenure_days': 'mean',
        'virtual_care_visits': 'mean',
        'lifetime_value': 'mean',
        'risk_score': 'mean'
    }).round(2)
    
    segment_summary.columns = ['Size', 'Avg. Tenure', 'Avg. Visits', 'Avg. LTV', 'Churn Rate']
    segment_summary['Avg. LTV'] = '$' + segment_summary['Avg. LTV'].astype(str)
    segment_summary['Churn Rate'] = (segment_summary['Churn Rate'] * 100).astype(str) + '%'
    
    st.dataframe(segment_summary, use_container_width=True)

# ============================================================================
# PLACEHOLDER PAGES - TO BE IMPLEMENTED
# ============================================================================

def show_member_details():
    """Placeholder for member details page"""
    st.title("👤 Member Details")
    st.info("Member details page - To be implemented")
    
    # Add your member details implementation here

def show_executive_reporting():
    """Placeholder for executive reporting page"""
    st.title("📊 Executive Reporting")
    st.info("Executive reporting page - To be implemented")
    
    # Add your executive reporting implementation here

def show_settings():
    """Placeholder for settings page"""
    st.title("⚙️ Settings")
    st.info("Settings page - To be implemented")
    
    # Add your settings implementation here

# ============================================================================
# MAIN DASHBOARD NAVIGATION
# ============================================================================

def show_dashboard():
    """Display main dashboard with navigation"""
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🎯 Simlane Analytics")
        
        page = st.radio(
            "Navigation",
            ["Churn Predictions", "Customer Segments", "Member Details", "Executive Reporting", "Settings"],
            label_visibility="collapsed"
        )
        
        if st.button("Logout"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
    
    # Ensure data exists
    if st.session_state.member_data is None:
        st.session_state.member_data = generate_demo_data()
    
    # Route to appropriate page
    if page == "Churn Predictions":
        show_churn_predictions()
    elif page == "Customer Segments":
        show_customer_segments()
    elif page == "Member Details":
        show_member_details()
    elif page == "Executive Reporting":
        show_executive_reporting()
    elif page == "Settings":
        show_settings()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    init_session_state()
    
    if not st.session_state.logged_in:
        show_login()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()

# ============================================================================
# ADD NEW PAGES BELOW THIS LINE
# ============================================================================
# To add a new page:
# 1. Create a new function: def show_your_page_name():
# 2. Add the page to the navigation radio button list in show_dashboard()
# 3. Add the routing logic in show_dashboard()
