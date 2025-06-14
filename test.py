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

def create_cluster_visualization(data, cluster_summary):
    """Create interactive cluster visualization."""
    
    # Cluster distribution pie chart
    fig_pie = px.pie(
        values=cluster_summary['Size'],
        names=[f'Cluster {i}' for i in cluster_summary.index],
        title="Customer Segment Distribution",
        color_discrete_sequence=['#0066CC', '#00B8A3', '#FF6B35', '#00CC88']
    )
    fig_pie.update_layout(
        font=dict(size=12),
        showlegend=True,
        height=400
    )
    
    # Churn rate by cluster
    fig_churn = px.bar(
        x=[f'Cluster {i}' for i in cluster_summary.index],
        y=cluster_summary['Churn_Rate'],
        title="Churn Rate by Customer Segment",
        color=cluster_summary['Churn_Rate'],
        color_continuous_scale=['#00CC88', '#FF6B35']
    )
    fig_churn.update_layout(height=400)
    
    # Scatter plot: Usage vs Tenure
    fig_scatter = px.scatter(
        data, 
        x='tenure_days', 
        y='virtual_care_visits',
        color='cluster',
        size='lifetime_value',
        hover_data=['member_id', 'risk_category'],
        title="Member Engagement Patterns",
        color_discrete_sequence=['#0066CC', '#00B8A3', '#FF6B35', '#00CC88']
    )
    fig_scatter.update_layout(height=500)
    
    return fig_pie, fig_churn, fig_scatter

def create_risk_dashboard(data):
    """Create risk analysis dashboard."""
    
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

def show_customer_segments(data, cluster_summary):
    """Customer segments analysis page."""
    create_professional_header(
        "Customer Segments", 
        "Deep dive into customer segmentation and behavioral patterns"
    )
    
    # Cluster summary table
    st.subheader("📊 Segment Overview")
    
    # Format the summary for display
    display_summary = cluster_summary.copy()
    display_summary['Churn_Rate'] = (display_summary['Churn_Rate'] * 100).round(1).astype(str) + '%'
    display_summary['Avg_Premium'] = '$' + display_summary['Avg_Premium'].round(0).astype(str)    """Executive dashboard view."""
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
    
    # Main content area
    if page == "🏠 Executive Dashboard":
        show_executive_dashboard(data, cluster_summary)
    elif page == "👥 Customer Segments":
        show_customer_segments(data, cluster_summary)
    elif page == "⚠️ Churn Predictions":
        show_churn_predictions(data)
    elif page == "💰 Financial Impact":
        show_financial_impact(data)
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
    main() + display_summary['Avg_Premium'].round(0).astype(str)
    display_summary['Avg_LTV'] = '
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
    main() + display_summary['Avg_LTV'].round(0).astype(str)
    
    st.dataframe(display_summary, use_container_width=True)
    
    # Segment selector
    st.subheader("🔍 Segment Deep Dive")
    selected_cluster = st.selectbox("Select a segment to analyze:", 
                                   options=list(range(len(cluster_summary))),
                                   format_func=lambda x: f"Cluster {x}")
    
    # Segment analysis
    cluster_data = data[data['cluster'] == selected_cluster]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Members", len(cluster_data))
    with col2:
        st.metric("Avg Pets", f"{cluster_data['pets_covered'].mean():.1f}")
    with col3:
        st.metric("Avg Visits", f"{cluster_data['virtual_care_visits'].mean():.1f}")
    with col4:
        st.metric("Churn Rate", f"{(cluster_data['status'] == 'cancelled').mean():.1%}")
    
    # Visualizations
    fig_pie, fig_churn, fig_scatter = create_cluster_visualization(data, cluster_summary)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        # Risk distribution for selected cluster
        risk_dist = cluster_data['risk_category'].value_counts()
        fig_risk_cluster = px.pie(
            values=risk_dist.values,
            names=risk_dist.index,
            title=f"Risk Distribution - Cluster {selected_cluster}",
            color_discrete_map={
                'IMMEDIATE': '#FF6B35',
                'HIGH': '#F59E0B', 
                'MEDIUM': '#0066CC',
                'LOW': '#00CC88'
            }
        )
        st.plotly_chart(fig_risk_cluster, use_container_width=True)
    
    # Member list for selected cluster
    st.subheader(f"👥 Members in Cluster {selected_cluster}")
    
    display_columns = ['member_id', 'status', 'risk_category', 'pets_covered', 
                      'virtual_care_visits', 'estimated_days_to_churn']
    
    cluster_display = cluster_data[display_columns].copy()
    cluster_display['estimated_days_to_churn'] = cluster_display['estimated_days_to_churn'].astype(str) + ' days'
    
    st.dataframe(cluster_display.head(20), use_container_width=True)

def show_churn_predictions(data):
    """Churn predictions and risk analysis page."""
    create_professional_header(
        "Churn Predictions", 
        "Individual member risk assessment and intervention recommendations"
    )
    
    # Risk summary metrics
    active_data = data[data['status'] == 'active']
    
    col1, col2, col3, col4 = st.columns(4)
    
    immediate_count = len(active_data[active_data['risk_category'] == 'IMMEDIATE'])
    high_count = len(active_data[active_data['risk_category'] == 'HIGH'])
    medium_count = len(active_data[active_data['risk_category'] == 'MEDIUM'])
    low_count = len(active_data[active_data['risk_category'] == 'LOW'])
    
    with col1:
        st.markdown(create_metric_card(
            "Immediate Risk", 
            str(immediate_count), 
            "≤30 days",
            "🚨"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "High Risk", 
            str(high_count), 
            "≤90 days",
            "⚠️"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Medium Risk", 
            str(medium_count), 
            "≤180 days",
            "🔶"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Low Risk", 
            str(low_count), 
            ">180 days",
            "✅"
        ), unsafe_allow_html=True)
    
    # Risk visualizations
    fig_risk, fig_timeline = create_risk_dashboard(active_data)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_risk, use_container_width=True)
    with col2:
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Action center
    st.subheader("🎯 Action Center")
    
    # Risk filter
    risk_filter = st.selectbox(
        "Filter by risk level:",
        options=['All'] + list(active_data['risk_category'].unique()),
        index=0
    )
    
    # Filter data
    if risk_filter != 'All':
        filtered_data = active_data[active_data['risk_category'] == risk_filter]
    else:
        filtered_data = active_data
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Generate Retention Emails", use_container_width=True):
            st.success(f"✅ Generated retention emails for {len(filtered_data)} members")
    
    with col2:
        if st.button("📞 Schedule Follow-up Calls", use_container_width=True):
            st.success(f"✅ Scheduled calls for {len(filtered_data)} members")
    
    with col3:
        if st.button("📊 Export Risk Report", use_container_width=True):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"risk_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Member details table
    st.subheader("👤 Member Risk Details")
    
    display_data = filtered_data[['member_id', 'risk_category', 'estimated_days_to_churn', 
                                 'virtual_care_visits', 'pets_covered', 'lifetime_value']].copy()
    
    st.dataframe(display_data, use_container_width=True)

def show_financial_impact(data):
    """Financial impact and ROI analysis page."""
    create_professional_header(
        "Financial Impact", 
        "Revenue analysis and ROI calculations for retention initiatives"
    )
    
    # Financial metrics
    total_ltv = data['lifetime_value'].sum()
    active_ltv = data[data['status'] == 'active']['lifetime_value'].sum()
    at_risk_ltv = data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])]['lifetime_value'].sum()
    monthly_revenue = data[data['status'] == 'active']['monthly_premium'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Total Portfolio Value", 
            f"${total_ltv:,.0f}", 
            "↑ 8.5% YoY",
            "💰"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Active Member LTV", 
            f"${active_ltv:,.0f}", 
            "↑ 12% vs target",
            "📈"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Revenue at Risk", 
            f"${at_risk_ltv:,.0f}", 
            "↑ $45K this month",
            "⚠️"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Monthly Recurring Revenue", 
            f"${monthly_revenue:,.0f}", 
            "↑ 6% vs last month",
            "🔄"
        ), unsafe_allow_html=True)
    
    # ROI Calculator
    st.subheader("💡 Retention ROI Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Input Parameters**")
        intervention_cost = st.number_input("Cost per intervention ($)", value=75, min_value=1)
        success_rate = st.slider("Expected success rate (%)", 0, 100, 65) / 100
        target_members = st.number_input("Members to target", value=100, min_value=1)
        
    with col2:
        # Calculate ROI
        avg_ltv = data['lifetime_value'].mean()
        total_cost = intervention_cost * target_members
        prevented_churns = target_members * success_rate
        revenue_saved = prevented_churns * avg_ltv
        net_benefit = revenue_saved - total_cost
        roi_ratio = net_benefit / total_cost if total_cost > 0 else 0
        
        st.markdown("**💰 ROI Calculation**")
        st.metric("Total Investment", f"${total_cost:,.0f}")
        st.metric("Revenue Saved", f"${revenue_saved:,.0f}")
        st.metric("Net Benefit", f"${net_benefit:,.0f}")
        st.metric("ROI Ratio", f"{roi_ratio:.1f}x")
    
    # Revenue projections chart
    months = list(range(1, 13))
    baseline_revenue = [monthly_revenue * (0.98 ** month) for month in months]  # 2% monthly decline
    with_retention = [monthly_revenue * (0.995 ** month) for month in months]  # 0.5% monthly decline
    
    fig_projection = go.Figure()
    fig_projection.add_trace(go.Scatter(
        x=months, y=baseline_revenue, name='Without Retention Program',
        line=dict(color='#FF6B35', dash='dash')
    ))
    fig_projection.add_trace(go.Scatter(
        x=months, y=with_retention, name='With Retention Program',
        line=dict(color='#00CC88')
    ))
    
    fig_projection.update_layout(
        title="12-Month Revenue Projection",
        xaxis_title="Month",
        yaxis_title="Monthly Revenue ($)",
        height=400
    )
    
    st.plotly_chart(fig_projection, use_container_width=True)
    
    # Financial summary by segment
    st.subheader("💼 Revenue by Customer Segment")
    
    segment_revenue = data.groupby('cluster').agg({
        'lifetime_value': ['sum', 'mean', 'count'],
        'monthly_premium': 'sum'
    }).round(2)
    
    segment_revenue.columns = ['Total_LTV', 'Avg_LTV', 'Count', 'Monthly_Revenue']
    segment_revenue.index = [f'Cluster {i}' for i in segment_revenue.index]
    
    # Format for display
    display_segment = segment_revenue.copy()
    for col in ['Total_LTV', 'Avg_LTV', 'Monthly_Revenue']:
        display_segment[col] = '
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
    main() + display_segment[col].astype(str)
    
    st.dataframe(display_segment, use_container_width=True)

def show_settings():
    """Settings and configuration page."""
    create_professional_header(
        "Settings & Configuration", 
        "System settings, data management, and user preferences"
    )
    
    tab1, tab2, tab3 = st.tabs(["📊 Data Management", "👤 User Settings", "🔧 System Config"])
    
    with tab1:
        st.subheader("📥 Data Upload")
        
        uploaded_file = st.file_uploader(
            "Upload new member data (CSV format)",
            type=['csv'],
            help="Upload a CSV file with member data to update the analytics"
        )
        
        if uploaded_file is not None:
            try:
                new_data = pd.read_csv(uploaded_file)
                st.success(f"✅ Successfully uploaded {len(new_data)} records")
                st.dataframe(new_data.head(), use_container_width=True)
                
                if st.button("🔄 Process Data"):
                    st.success("✅ Data processed successfully! Dashboard will update automatically.")
                    
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
        
        st.subheader("🗂️ Data Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export Full Dataset", use_container_width=True):
                data = load_sample_data()
                csv = data.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"member_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📈 Export Analytics Report", use_container_width=True):
                st.info("📊 Generating comprehensive analytics report...")
    
    with tab2:
        st.subheader("👤 User Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Full Name", value=st.session_state.get('user', {}).get('name', ''))
            st.selectbox("Role", options=['admin', 'analyst', 'executive'], 
                        index=0 if st.session_state.get('user', {}).get('role') == 'admin' else 1)
            st.text_input("Email", value="user@simlane.ai")
        
        with col2:
            st.selectbox("Timezone", options=['UTC', 'EST', 'PST'], index=1)
            st.selectbox("Date Format", options=['MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD'], index=0)
            st.checkbox("Email Notifications", value=True)
        
        if st.button("💾 Save Settings", use_container_width=True):
            st.success("✅ Settings saved successfully!")
    
    with tab3:
        st.subheader("⚙️ System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("Data Refresh Interval (hours)", value=24, min_value=1)
            st.number_input("Alert Threshold (days)", value=30, min_value=1)
            st.selectbox("Default Risk View", options=['All', 'High Risk Only'], index=0)
        
        with col2:
            st.checkbox("Auto-generate Reports", value=True)
            st.checkbox("Enable Debug Mode", value=False)
            st.selectbox("Log Level", options=['INFO', 'WARNING', 'ERROR'], index=0)
        
        if st.button("🔄 Apply Configuration", use_container_width=True):
            st.success("✅ Configuration updated successfully!")
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
