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
        """)

def create_risk_dashboard(data):
    """Create risk analysis dashboard."""
    
    # Risk distribution
    risk_counts = data['risk_category'].value_counts()
    fig_risk = px.bar(
        x=risk_counts.index,
        y=risk_counts.values,
        title="Member Risk Distribution",
        labels={'x': 'Risk Category', 'y': 'Number of Members'},
        color=risk_counts.index,
        color_discrete_map={
            'IMMEDIATE': '#FF6B35',
            'HIGH': '#F59E0B', 
            'MEDIUM': '#0066CC',
            'LOW': '#00CC88'
        }
    )
    fig_risk.update_layout(height=400)
    
    # Timeline distribution
    fig_timeline = px.histogram(
        data[data['status'] == 'active'], 
        x='estimated_days_to_churn',
        nbins=30,
        title="Time to Predicted Churn Distribution",
        color_discrete_sequence=['#0066CC']
    )
    fig_timeline.update_layout(height=400)
    
    return fig_risk, fig_timeline

def show_churn_predictions(data):
    """Churn predictions page."""
    create_professional_header(
        "Churn Predictions", 
        "AI-powered member retention insights and risk analysis"
    )
    
    # Risk metrics
    col1, col2, col3, col4 = st.columns(4)
    
    immediate_risk = len(data[data['risk_category'] == 'IMMEDIATE'])
    high_risk = len(data[data['risk_category'] == 'HIGH'])
    medium_risk = len(data[data['risk_category'] == 'MEDIUM'])
    low_risk = len(data[data['risk_category'] == 'LOW'])
    
    with col1:
        st.markdown(create_metric_card(
            "Immediate Risk", 
            f"{immediate_risk}", 
            "Next 30 days",
            "🚨"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "High Risk", 
            f"{high_risk}", 
            "30-90 days",
            "⚠️"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Medium Risk", 
            f"{medium_risk}", 
            "90-180 days",
            "📊"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Low Risk", 
            f"{low_risk}", 
            ">180 days",
            "✅"
        ), unsafe_allow_html=True)
    
    # Risk visualization
    fig_risk, fig_timeline = create_risk_dashboard(data)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_risk, use_container_width=True)
    with col2:
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # High-risk members table
    st.subheader("🎯 High-Priority Members")
    
    high_risk_members = data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])].sort_values('estimated_days_to_churn')
    
    display_columns = ['member_id', 'group_id', 'risk_category', 'estimated_days_to_churn', 
                      'tenure_days', 'virtual_care_visits', 'lifetime_value']
    
    st.dataframe(
        high_risk_members[display_columns].head(20),
        use_container_width=True,
        height=400
    )
    
    # Download option
    csv = high_risk_members.to_csv(index=False)
    st.download_button(
        label="📥 Download High-Risk Members List",
        data=csv,
        file_name=f"high_risk_members_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )

def show_customer_segments(data, cluster_summary):
    """Customer segments analysis page."""
    create_professional_header(
        "Customer Segments", 
        "Deep dive into customer segmentation and behavioral patterns"
    )
    
    # Segment insights (moved to top)
    st.subheader("🔍 Segment Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        highest_value_cluster = cluster_summary['Avg_LTV'].idxmax()
        st.markdown(create_alert_box(
            f"Cluster {highest_value_cluster} has the highest average lifetime value at ${cluster_summary.loc[highest_value_cluster, 'Avg_LTV']:,.0f}",
            "success"
        ), unsafe_allow_html=True)
    
    with col2:
        highest_churn_cluster = cluster_summary['Churn_Rate'].idxmax()
        st.markdown(create_alert_box(
            f"Cluster {highest_churn_cluster} has the highest churn rate at {cluster_summary.loc[highest_churn_cluster, 'Churn_Rate']*100:.1f}%",
            "warning"
        ), unsafe_allow_html=True)
    
    # Member engagement patterns (scatter plot only)
    st.subheader("📈 Member Engagement Patterns")
    
    fig_scatter = px.scatter(
        data, 
        x='tenure_days', 
        y='virtual_care_visits',
        color='cluster',
        size='lifetime_value',
        hover_data=['member_id', 'risk_category'],
        title="Usage vs Tenure by Segment",
        labels={'tenure_days': 'Tenure (Days)', 'virtual_care_visits': 'Virtual Care Visits'},
        color_discrete_sequence=['#0066CC', '#00B8A3', '#FF6B35', '#00CC88']
    )
    fig_scatter.update_layout(height=500)
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Segment overview table (moved to bottom)
    st.subheader("📊 Segment Overview")
    
    # Format the summary for display
    display_summary = cluster_summary.copy()
    display_summary['Churn_Rate'] = (display_summary['Churn_Rate'] * 100).round(1).astype(str) + '%'
    display_summary['Avg_Premium'] = '$' + display_summary['Avg_Premium'].round(0).astype(str)
    display_summary['Avg_LTV'] = '$' + display_summary['Avg_LTV'].round(0).astype(str)
    
    st.dataframe(display_summary, use_container_width=True)

def show_settings():
    """Settings page."""
    create_professional_header(
        "Settings", 
        "Configure your dashboard preferences and account settings"
    )
    
    st.subheader("👤 User Profile")
    st.info(f"""
    **Username:** {st.session_state.username}  
    **Role:** {st.session_state.user['role'].title()}  
    **Name:** {st.session_state.user['name']}
    """)
    
    st.subheader("🎨 Dashboard Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.selectbox("Color Theme", ["Default Blue", "Dark Mode", "Light Mode"])
        date_format = st.selectbox("Date Format", ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])
    
    with col2:
        currency = st.selectbox("Currency", ["USD ($)", "EUR (€)", "GBP (£)"])
        timezone = st.selectbox("Timezone", ["EST", "PST", "CST", "UTC"])
    
    st.subheader("📊 Data Settings")
    
    auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
    if auto_refresh:
        refresh_interval = st.slider("Refresh Interval (minutes)", 5, 60, 15)
    
    export_format = st.radio("Default Export Format", ["CSV", "Excel", "JSON"])
    
    st.subheader("🔔 Notifications")
    
    email_alerts = st.checkbox("Email Alerts", value=True)
    sms_alerts = st.checkbox("SMS Alerts", value=False)
    
    if email_alerts:
        alert_threshold = st.select_slider(
            "Alert when churn risk exceeds:",
            options=["LOW", "MEDIUM", "HIGH", "IMMEDIATE"],
            value="HIGH"
        )
    
    # Save button
    if st.button("💾 Save Settings", type="primary", use_container_width=True):
        st.success("✅ Settings saved successfully!")
        time.sleep(1)
        st.rerun()

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
                "⚠️ Churn Predictions",
                "👥 Customer Segments",
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
    
    # Main content area
    if page == "⚠️ Churn Predictions":
        show_churn_predictions(data)
    elif page == "👥 Customer Segments":
        show_customer_segments(data, cluster_summary)
    elif page == "⚙️ Settings":
        show_settings()
    
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
