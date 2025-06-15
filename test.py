# Working version of Simlane.ai - Start with this and add features back

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import bcrypt
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Simlane.ai Analytics Platform",
    page_icon="🎯",
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Simple authentication
def login_page():
    st.title("🎯 Simlane.ai")
    st.subheader("Advanced Member Analytics Platform")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                if username == "admin" and password == "admin123":
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user = {'name': 'Admin User', 'role': 'admin'}
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.info("Demo credentials: admin/admin123")

# Generate sample data
@st.cache_data
def load_sample_data():
    np.random.seed(42)
    n = 500
    
    # Generate data
    data = pd.DataFrame({
        'member_id': [f'M{i:04d}' for i in range(n)],
        'group_id': np.random.choice([f'G{i}' for i in range(1, 21)], n),
        'risk_category': np.random.choice(['IMMEDIATE', 'HIGH', 'MEDIUM', 'LOW'], n, p=[0.1, 0.2, 0.3, 0.4]),
        'estimated_days_to_churn': np.random.randint(1, 365, n),
        'lifetime_value': np.abs(np.random.normal(1000, 300, n)),
        'virtual_care_visits': np.random.poisson(3, n),
        'tenure_days': np.random.randint(30, 1095, n),
        'segment': np.random.choice(['Premium', 'Standard', 'Emerging', 'New'], n)
    })
    
    return data

# Main app
def main_app():
    st.title("🎯 Simlane.ai Analytics Platform")
    
    # Load data
    data = load_sample_data()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.username}!")
        
        page = st.radio(
            "Navigation",
            ["Dashboard", "Churn Predictions", "Settings"]
        )
        
        st.markdown("---")
        
        # Quick stats
        st.metric("Total Members", f"{len(data):,}")
        at_risk = len(data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])])
        st.metric("At Risk", f"{at_risk:,}")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    # Page routing
    if page == "Dashboard":
        st.header("Executive Dashboard")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            at_risk = len(data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])])
            st.metric("Members at Risk", f"{at_risk:,}", f"{at_risk/len(data)*100:.1f}%")
        
        with col2:
            revenue_at_risk = data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])]['lifetime_value'].sum()
            st.metric("Revenue at Risk", f"${revenue_at_risk/1000:.0f}K")
        
        with col3:
            avg_ltv = data['lifetime_value'].mean()
            st.metric("Avg Member Value", f"${avg_ltv:,.0f}")
        
        with col4:
            engagement = data['virtual_care_visits'].mean()
            st.metric("Engagement Score", f"{engagement:.1f}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Risk Distribution")
            risk_counts = data['risk_category'].value_counts()
            fig = px.bar(x=risk_counts.index, y=risk_counts.values, 
                        color=risk_counts.index,
                        color_discrete_map={
                            'IMMEDIATE': '#D92D20',
                            'HIGH': '#F97316',
                            'MEDIUM': '#3B82F6',
                            'LOW': '#16A34A'
                        })
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Segments")
            segment_counts = data['segment'].value_counts()
            fig = px.pie(values=segment_counts.values, names=segment_counts.index, hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
    
    elif page == "Churn Predictions":
        st.header("Churn Predictions")
        
        # Filter
        risk_filter = st.selectbox("Filter by risk", ['All', 'IMMEDIATE', 'HIGH', 'MEDIUM', 'LOW'])
        
        if risk_filter != 'All':
            filtered_data = data[data['risk_category'] == risk_filter]
        else:
            filtered_data = data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])]
        
        st.write(f"Showing {len(filtered_data)} members")
        
        # Display data
        display_cols = ['member_id', 'group_id', 'risk_category', 'estimated_days_to_churn', 
                       'lifetime_value', 'virtual_care_visits']
        st.dataframe(
            filtered_data[display_cols].sort_values('estimated_days_to_churn'),
            use_container_width=True
        )
        
        # Download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            f"churn_predictions_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )
    
    elif page == "Settings":
        st.header("Settings")
        st.info("Configure your preferences here")
        
        with st.expander("Notification Settings"):
            st.checkbox("Email Alerts", value=True)
            st.checkbox("SMS Alerts", value=False)
            st.selectbox("Alert Threshold", ["IMMEDIATE", "HIGH", "MEDIUM"])
        
        with st.expander("Data Settings"):
            if st.button("Upload New Data"):
                st.info("File upload functionality would go here")

# Main execution
if not st.session_state.authenticated:
    login_page()
else:
    main_app()
