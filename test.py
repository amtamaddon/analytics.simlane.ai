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

# Import Twilio (optional - will work without it)
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

# Import os for environment variables
import os

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
# SMS NOTIFICATION SYSTEM
# ============================================================================

class SMSManager:
    def __init__(self):
        self.client = None
        self.from_number = None
        
        # Try to initialize Twilio client if credentials are available
        if TWILIO_AVAILABLE:
            try:
                # Check for Twilio credentials in Streamlit secrets
                if 'twilio' in st.secrets:
                    account_sid = st.secrets['twilio']['account_sid']
                    auth_token = st.secrets['twilio']['auth_token']
                    self.from_number = st.secrets['twilio'].get('from_number', '+1234567890')
                    self.client = TwilioClient(account_sid, auth_token)
                # Check environment variables as fallback
                elif all(k in os.environ for k in ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN']):
                    import os
                    account_sid = os.environ['TWILIO_ACCOUNT_SID']
                    auth_token = os.environ['TWILIO_AUTH_TOKEN']
                    self.from_number = os.environ.get('TWILIO_FROM_NUMBER', '+1234567890')
                    self.client = TwilioClient(account_sid, auth_token)
            except Exception as e:
                st.error(f"Failed to initialize Twilio: {str(e)}")
    
    def send_sms(self, to_number, message):
        """Send an SMS message using Twilio."""
        if not self.client:
            return False, "Twilio client not initialized. Please configure credentials."
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            return True, f"Message sent successfully! SID: {message.sid}"
        except Exception as e:
            return False, f"Failed to send SMS: {str(e)}"
    
    def send_risk_alert(self, phone_number, member_id, risk_level, days_to_churn):
        """Send a risk alert SMS for a specific member."""
        message = f"🚨 SIMLANE ALERT: Member {member_id} is at {risk_level} risk of churning in {days_to_churn} days. Take action now!"
        return self.send_sms(phone_number, message)
    
    def send_test_message(self, phone_number):
        """Send a test SMS message."""
        message = "🎯 Simlane.ai Test Message: Your SMS notifications are working correctly!"
        return self.send_sms(phone_number, message)

sms_manager = SMSManager()

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
    
    # High-risk members table with SMS alert option
    st.subheader("🎯 High-Priority Members")
    
    # Always show the SMS alert button area
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Members at immediate risk")
    with col2:
        # Check if SMS is configured in settings
        if st.button("📱 Send Bulk Alerts", use_container_width=True, type="primary"):
            if 'sms_alerts_enabled' in st.session_state and st.session_state.sms_alerts_enabled and 'alert_phone' in st.session_state:
                high_risk_members = data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])].sort_values('estimated_days_to_churn')
                immediate_members = high_risk_members[high_risk_members['risk_category'] == 'IMMEDIATE'].head(5)
                
                if len(immediate_members) > 0:
                    with st.spinner("Sending SMS alerts..."):
                        success_count = 0
                        for _, member in immediate_members.iterrows():
                            success, msg = sms_manager.send_risk_alert(
                                st.session_state.alert_phone,
                                member['member_id'],
                                member['risk_category'],
                                member['estimated_days_to_churn']
                            )
                            if success:
                                success_count += 1
                        
                        if success_count > 0:
                            st.success(f"✅ Sent {success_count} SMS alerts successfully!")
                        else:
                            st.error("Failed to send alerts. Check your Twilio configuration in Settings.")
                else:
                    st.warning("No immediate risk members to alert.")
            else:
                st.warning("⚠️ Please enable and configure SMS alerts in Settings first.")
    
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
            st.text_input("Full Name", value=st.session_state.user['name'])
            st.text_input("Email", value="user@simlane.ai", help="Primary contact email")
            st.text_input("Phone Number", value="+1 (555) 123-4567", help="For SMS notifications")
        
        with col2:
            st.selectbox("Role", options=['Admin', 'Analyst', 'Executive'], 
                        index=0 if st.session_state.user['role'] == 'admin' else 1)
            st.selectbox("Timezone", options=['EST', 'PST', 'CST', 'UTC'], index=0)
            st.selectbox("Date Format", options=['MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD'], index=0)
        
        st.subheader("🔔 Notification Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email_alerts = st.checkbox("Email Alerts", value=True)
            if email_alerts:
                alert_email = st.text_input("Alert Email", value="alerts@simlane.ai", 
                                          help="Where to send email alerts")
                email_frequency = st.selectbox("Email Frequency", 
                                             options=["Immediate", "Daily Digest", "Weekly Summary"])
        
        with col2:
            sms_alerts = st.checkbox("SMS Alerts", value=False)
            if sms_alerts:
                alert_phone = st.text_input("Alert Phone", value="+1 (555) 987-6543",
                                          help="Where to send SMS alerts")
                sms_threshold = st.select_slider(
                    "SMS Alert Threshold",
                    options=["LOW", "MEDIUM", "HIGH", "IMMEDIATE"],
                    value="HIGH",
                    help="Only send SMS for risks at or above this level"
                )
                
                # Store SMS settings in session state
                st.session_state.sms_alerts_enabled = True
                st.session_state.alert_phone = alert_phone
                
                # Add some spacing
                st.markdown("---")
                
                # Test SMS button - make it more prominent
                st.markdown("**📱 Test SMS Configuration**")
                col_test1, col_test2 = st.columns([2, 1])
                with col_test1:
                    st.info("Send a test message to verify SMS setup")
                with col_test2:
                    if st.button("Send Test SMS", type="primary", use_container_width=True):
                        if alert_phone:
                            with st.spinner("Sending test message..."):
                                success, message = sms_manager.send_test_message(alert_phone)
                                if success:
                                    st.success(message)
                                else:
                                    st.error(message)
                                    if not TWILIO_AVAILABLE:
                                        st.warning("💡 To enable SMS, install Twilio: `pip install twilio`")
                                    else:
                                        with st.expander("🔧 Twilio Configuration Help"):
                                            st.markdown("""
                                            **To configure Twilio:**
                                            
                                            1. Create a `.streamlit/secrets.toml` file:
                                            ```toml
                                            [twilio]
                                            account_sid = "your-account-sid"
                                            auth_token = "your-auth-token"
                                            from_number = "+1234567890"
                                            ```
                                            
                                            2. Or set environment variables:
                                            ```bash
                                            export TWILIO_ACCOUNT_SID="your-sid"
                                            export TWILIO_AUTH_TOKEN="your-token"
                                            export TWILIO_FROM_NUMBER="+1234567890"
                                            ```
                                            
                                            3. Get your credentials from [Twilio Console](https://console.twilio.com)
                                            """)
                        else:
                            st.warning("Please enter a phone number first.")
            else:
                st.session_state.sms_alerts_enabled = False
        
        if email_alerts or sms_alerts:
            st.multiselect(
                "Alert Types",
                options=["New High Risk Members", "Churn Rate Changes", "Segment Shifts", "System Issues"],
                default=["New High Risk Members", "Churn Rate Changes"]
            )
        
        if st.button("💾 Save User Settings", use_container_width=True):
            st.success("✅ Settings saved successfully!")
    
    with tab3:
        st.subheader("⚙️ System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("Data Refresh Interval (hours)", value=24, min_value=1)
            st.number_input("High Risk Alert Threshold (days)", value=30, min_value=1, max_value=90)
            st.selectbox("Default Dashboard View", options=['Churn Predictions', 'Customer Segments'], index=0)
        
        with col2:
            st.checkbox("Auto-generate Weekly Reports", value=True)
            st.checkbox("Enable Advanced Analytics", value=True)
            st.selectbox("Export Format", options=['CSV', 'Excel', 'JSON'], index=0)
        
        st.subheader("🎯 Risk Thresholds")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.number_input("Immediate Risk (days)", value=30, min_value=1, max_value=60)
        with col2:
            st.number_input("High Risk (days)", value=90, min_value=31, max_value=120)
        with col3:
            st.number_input("Medium Risk (days)", value=180, min_value=91, max_value=365)
        with col4:
            st.number_input("Low Risk (days)", value=365, min_value=181)
        
        if st.button("🔄 Apply Configuration", use_container_width=True):
            st.success("✅ Configuration updated successfully!")

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
