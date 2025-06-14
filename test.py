# ============================================================================
# SIMLANE.AI ANALYTICS PLATFORM - STREAMLIT APP
# Complete white-labeled, professional business intelligence platform
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import bcrypt
import jwt
from datetime import datetime, timedelta
import base64
import io
import time
from pathlib import Path

# ============================================================================
# APP CONFIGURATION & STYLING
# ============================================================================

# Page config - remove Streamlit branding
st.set_page_config(
    page_title="Simlane.ai Analytics Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Custom CSS to completely hide Streamlit branding and create professional UI
st.markdown("""
<style>
    /* Hide all Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none;}
    .viewerBadge_link__1S2L9 {display: none;}
    .viewerBadge_text__1JaDK {display: none;}
    
    /* Remove padding from main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #0066CC 0%, #00B8A3 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 102, 204, 0.2);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }
    
    /* Professional metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #0066CC;
        margin: 1rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0066CC;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
        font-weight: 500;
        margin: 0;
    }
    
    .metric-change {
        font-size: 0.85rem;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    .metric-change.positive {
        color: #00CC88;
    }
    
    .metric-change.negative {
        color: #FF6B35;
    }
    
    /* Alert boxes */
    .alert {
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .alert-danger {
        background: #FEF2F2;
        border-color: #FF6B35;
        color: #991B1B;
    }
    
    .alert-warning {
        background: #FFFBEB;
        border-color: #F59E0B;
        color: #92400E;
    }
    
    .alert-success {
        background: #ECFDF5;
        border-color: #00CC88;
        color: #065F46;
    }
    
    .alert-info {
        background: #EFF6FF;
        border-color: #0066CC;
        color: #1E40AF;
    }
    
    /* Login form styling */
    .login-container {
        max-width: 400px;
        margin: 5rem auto;
        padding: 2.5rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid #E2E8F0;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h1 {
        color: #0066CC;
        font-size: 2rem;
        margin: 0;
        font-weight: 700;
    }
    
    .login-header p {
        color: #6B7280;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTHENTICATION SYSTEM
# ============================================================================

class AuthManager:
    def __init__(self):
        self.users = {
            "admin": {
                "password_hash": bcrypt.hashpw("simlane2025".encode(), bcrypt.gensalt()),
                "role": "admin",
                "name": "Admin User"
            },
            "analyst": {
                "password_hash": bcrypt.hashpw("analyst123".encode(), bcrypt.gensalt()), 
                "role": "analyst",
                "name": "Data Analyst"
            },
            "executive": {
                "password_hash": bcrypt.hashpw("executive456".encode(), bcrypt.gensalt()),
                "role": "executive", 
                "name": "Executive User"
            }
        }
    
    def authenticate(self, username, password):
        if username in self.users:
            user = self.users[username]
            if bcrypt.checkpw(password.encode(), user["password_hash"]):
                token = jwt.encode({
                    'username': username,
                    'role': user['role'],
                    'exp': datetime.utcnow() + timedelta(hours=8)
                }, "simlane_secret_key_2025", algorithm='HS256')
                
                st.session_state.auth_token = token
                st.session_state.user = user
                st.session_state.username = username
                st.session_state.authenticated = True
                return True
        return False
    
    def check_auth(self):
        if 'authenticated' not in st.session_state:
            return False
        return st.session_state.authenticated
    
    def logout(self):
        for key in ['auth_token', 'user', 'username', 'authenticated']:
            if key in st.session_state:
                del st.session_state[key]

auth_manager = AuthManager()

# ============================================================================
# DATA LOADING & PROCESSING
# ============================================================================

@st.cache_data
def load_sample_data():
    """Load sample data for the dashboard."""
    np.random.seed(42)
    
    # Generate sample member data
    n_members = 500
    member_ids = [f'M{i:04d}' for i in range(1, n_members + 1)]
    
    data = pd.DataFrame({
        'member_id': member_ids,
        'group_id': [f'G{np.random.randint(1, 21)}' for _ in range(n_members)],
        'status': np.random.choice(['active', 'cancelled'], n_members, p=[0.72, 0.28]),
        'cluster': np.random.choice([0, 1, 2, 3], n_members, p=[0.25, 0.30, 0.20, 0.25]),
        'pets_covered': np.random.choice([1, 2, 3, 4], n_members, p=[0.4, 0.3, 0.2, 0.1]),
        'virtual_care_visits': np.random.poisson(2.5, n_members),
        'tenure_days': np.random.exponential(300, n_members).astype(int),
        'estimated_days_to_churn': np.random.exponential(180, n_members).astype(int),
        'monthly_premium': np.random.normal(85, 20, n_members).round(2),
        'lifetime_value': np.random.normal(1250, 300, n_members).round(2)
    })
    
    # Add risk categories
    def categorize_risk(days):
        if days <= 30:
            return "IMMEDIATE"
        elif days <= 90:
            return "HIGH" 
        elif days <= 180:
            return "MEDIUM"
        else:
            return "LOW"
    
    data['risk_category'] = data['estimated_days_to_churn'].apply(categorize_risk)
    
    # Add industry and location data
    industries = ['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing']
    locations = ['New York', 'California', 'Texas', 'Florida', 'Illinois']
    
    data['industry'] = np.random.choice(industries, n_members)
    data['location'] = np.random.choice(locations, n_members)
    
    return data

@st.cache_data
def get_cluster_summary(data):
    """Generate cluster summary statistics."""
    summary = data.groupby('cluster').agg({
        'member_id': 'count',
        'pets_covered': 'mean',
        'tenure_days': 'mean',
        'virtual_care_visits': 'mean',
        'monthly_premium': 'mean',
        'lifetime_value': 'mean',
        'status': lambda x: (x == 'cancelled').mean()
    }).round(2)
    
    summary.columns = ['Size', 'Avg_Pets', 'Avg_Tenure', 'Avg_Visits', 'Avg_Premium', 'Avg_LTV', 'Churn_Rate']
    return summary

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_professional_header(title, subtitle):
    """Create a professional header section."""
    st.markdown(f"""
    <div class="main-header">
        <h1>🎯 {title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(label, value, change=None, icon="📊"):
    """Create a professional metric card."""
    change_class = ""
    change_text = ""
    
    if change:
        change_class = "positive" if change.startswith("+") or change.startswith("↑") else "negative"
        change_text = f'<p class="metric-change {change_class}">{change}</p>'
    
    return f"""
    <div class="metric-card">
        <p class="metric-label">{icon} {label}</p>
        <h2 class="metric-value">{value}</h2>
        {change_text}
    </div>
    """

def create_alert_box(message, alert_type="info"):
    """Create a professional alert box."""
    icons = {
        "danger": "🚨",
        "warning": "⚠️", 
        "success": "✅",
        "info": "ℹ️"
    }
    
    return f"""
    <div class="alert alert-{alert_type}">
        {icons.get(alert_type, "ℹ️")} {message}
    </div>
    """

def show_login_page():
    """Display the login page."""
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <h1>Simlane.ai</h1>
            <p>Analytics Platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.subheader("🔐 Secure Login")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if submitted:
            if auth_manager.authenticate(username, password):
                st.success("✅ Login successful! Redirecting...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    
    # Updated demo credentials for 2025
    with st.expander("🔑 Demo Credentials"):
        st.info("""
        **Admin User:**
        - Username: `admin`
        - Password: `simlane2025`
        
        **Analyst User:**
        - Username: `analyst` 
        - Password: `analyst123`
        
        **Executive User:**
        - Username: `executive`
        - Password: `executive456`
        """)

def show_executive_dashboard(data, cluster_summary):
    """Executive dashboard view."""
    create_professional_header(
        "Executive Dashboard", 
        "High-level business metrics and key performance indicators"
    )
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    total_members = len(data)
    active_members = len(data[data['status'] == 'active'])
    churn_rate = (data['status'] == 'cancelled').mean()
    revenue_at_risk = data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])]['lifetime_value'].sum()
    
    with col1:
        st.markdown(create_metric_card(
            "Total Members", 
            f"{total_members:,}", 
            "↑ 12% vs last month",
            "👥"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Churn Rate", 
            f"{churn_rate:.1%}", 
            "↓ 2.3% vs last month",
            "📉"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Active Members", 
            f"{active_members:,}", 
            "↑ 8% vs last month",
            "✅"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Revenue at Risk", 
            f"${revenue_at_risk:,.0f}", 
            "↑ $45K vs last month",
            "⚠️"
        ), unsafe_allow_html=True)
    
    # Create some basic visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Cluster distribution
        cluster_counts = data['cluster'].value_counts().sort_index()
        fig_pie = px.pie(
            values=cluster_counts.values,
            names=[f'Cluster {i}' for i in cluster_counts.index],
            title="Customer Segment Distribution",
            color_discrete_sequence=['#0066CC', '#00B8A3', '#FF6B35', '#00CC88']
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Risk distribution
        risk_counts = data['risk_category'].value_counts()
        fig_risk = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            title="Member Risk Distribution",
            color=risk_counts.index,
            color_discrete_map={
                'IMMEDIATE': '#FF6B35',
                'HIGH': '#F59E0B', 
                'MEDIUM': '#0066CC',
                'LOW': '#00CC88'
            }
        )
        st.plotly_chart(fig_risk, use_container_width=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application function."""
    
    # Check authentication
    if not auth_manager.check_auth():
        show_login_page()
        return
    
    # Load data
    data = load_sample_data()
    cluster_summary = get_cluster_summary(data)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; margin-bottom: 2rem; 
                    background: linear-gradient(135deg, #0066CC, #00B8A3); 
                    border-radius: 10px; color: white;">
            <h3 style="margin: 0;">Welcome!</h3>
            <p style="margin: 0.5rem 0 0 0;">{st.session_state.user['name']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu
        page = st.radio(
            "📍 Navigation",
            options=[
                "🏠 Executive Dashboard",
                "👥 Customer Segments", 
                "⚠️ Churn Predictions",
                "💰 Financial Impact",
                "⚙️ Settings"
            ],
            index=0
        )
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("**📊 Quick Stats**")
        total_members = len(data)
        at_risk = len(data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])])
        churn_rate = (data['status'] == 'cancelled').mean()
        
        st.metric("Total Members", f"{total_members:,}")
        st.metric("At Risk", f"{at_risk:,}")
        st.metric("Churn Rate", f"{churn_rate:.1%}")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            auth_manager.logout()
            st.rerun()
    
    # Main content area - simplified for now
    if page == "🏠 Executive Dashboard":
        show_executive_dashboard(data, cluster_summary)
    else:
        st.info(f"📄 {page} - Coming soon! This page is under development.")
    
    # Clean footer - updated for 2025
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; padding: 1rem;">
        <p>© 2025 Simlane.ai Analytics Platform | Secure Business Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
