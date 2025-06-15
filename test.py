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
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Simlane.ai Analytics Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://simlane.ai/support',
        'Report a bug': 'https://simlane.ai/bug-report',
        'About': '© 2024 Simlane.ai - Advanced Member Analytics Platform'
    }
)

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

# Semantic color palette for risk categories
RISK_COLORS = {
    'IMMEDIATE': '#DC2626',  # Red
    'HIGH': '#EA580C',       # Orange  
    'MEDIUM': '#2563EB',     # Blue
    'LOW': '#16A34A'         # Green
}

# Chart color sequences
RISK_COLOR_SEQUENCE = ['#DC2626', '#EA580C', '#2563EB', '#16A34A']
BRAND_COLORS = ['#2563EB', '#7C3AED', '#DB2777', '#DC2626', '#EA580C']

# ============================================================================
# CUSTOM STYLING
# ============================================================================

st.markdown("""
<style>
    /* Main app styling */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e293b;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        color: #10b981;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 2rem;
        }
        
        /* Hide non-critical columns on mobile */
        .dataframe td:nth-child(n+5),
        .dataframe th:nth-child(n+5) {
            display: none;
        }
    }
    
    /* Mobile menu button */
    .mobile-menu-btn {
        display: none;
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 999;
        background: #2563EB;
        color: white;
        border: none;
        padding: 0.5rem;
        border-radius: 0.5rem;
        cursor: pointer;
    }
    
    @media (max-width: 1024px) {
        .mobile-menu-btn {
            display: block;
        }
    }
    
    /* Onboarding wizard styling */
    .onboarding-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Risk preview box */
    .risk-preview {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    
    .risk-preview-item {
        margin-bottom: 0.5rem;
        font-weight: 600;
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
                # Default credentials - REPLACE THESE WITH YOUR ACTUAL VALUES
                account_sid = "AC..."  # Replace with your Account SID
                auth_token = "..."     # Replace with your Auth Token
                self.from_number = "+1..."  # Replace with your Twilio phone number
                
                # Check for Twilio credentials in Streamlit secrets (preferred method)
                if 'twilio' in st.secrets:
                    account_sid = st.secrets['twilio']['account_sid']
                    auth_token = st.secrets['twilio']['auth_token']
                    self.from_number = st.secrets['twilio'].get('from_number', self.from_number)
                # Check environment variables as fallback
                elif all(k in os.environ for k in ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN']):
                    account_sid = os.environ['TWILIO_ACCOUNT_SID']
                    auth_token = os.environ['TWILIO_AUTH_TOKEN']
                    self.from_number = os.environ.get('TWILIO_FROM_NUMBER', self.from_number)
                
                # Check if using test credentials (for development)
                # Test credentials will simulate SMS without actually sending
                if account_sid == "ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa":
                    st.warning("📋 Using Twilio Test Credentials - SMS will be simulated only")
                    self.test_mode = True
                else:
                    self.test_mode = False
                
                # Initialize the client if we have valid credentials
                if account_sid.startswith("AC") and len(account_sid) == 34 and auth_token != "...":
                    try:
                        self.client = TwilioClient(account_sid, auth_token)
                        # Check if toll-free number
                        if self.from_number and any(self.from_number.startswith(prefix) for prefix in ['+1833', '+1844', '+1855', '+1866', '+1877', '+1888']):
                            st.warning("⚠️ You're using a toll-free number. This requires verification for SMS. Consider getting a regular local number for immediate use.")
                        # Debug info (remove in production)
                        st.info(f"✅ Twilio initialized with Account SID: {account_sid[:6]}...{account_sid[-4:]}")
                    except Exception as e:
                        st.error(f"Twilio initialization error: {str(e)}")
                else:
                    st.warning("⚠️ Twilio credentials not properly configured.")
                    # Debug info (remove in production)
                    if not account_sid.startswith("AC"):
                        st.error(f"Account SID should start with 'AC', got: {account_sid[:4]}...")
                    if len(account_sid) != 34:
                        st.error(f"Account SID should be 34 characters, got: {len(account_sid)}")
                    if auth_token == "...":
                        st.error("Auth token not set")
                
            except Exception as e:
                st.error(f"Failed to initialize Twilio: {str(e)}")
    
    def send_sms(self, to_number, message):
        """Send an SMS message using Twilio."""
        if not self.client:
            return False, "Twilio client not initialized. Please configure credentials."
        
        if not self.from_number or self.from_number == "+1234567890":
            return False, "No valid Twilio phone number configured. Please set up a Twilio phone number."
        
        try:
            # Clean the phone number format
            to_number = to_number.strip()
            if not to_number.startswith('+'):
                # Assume US number if no country code
                to_number = '+1' + to_number.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            
            st.info(f"📞 Sending to: {to_number} from: {self.from_number}")
            
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            return True, f"Message sent successfully! SID: {message_obj.sid}"
        except Exception as e:
            error_msg = str(e)
            if "not a valid phone number" in error_msg:
                return False, f"Invalid phone number format. Please use format: +1234567890"
            elif "From" in error_msg and "is not a Twilio phone number" in error_msg:
                return False, f"Configuration error: {self.from_number} is not a valid Twilio phone number. Please get a phone number from your Twilio console."
            elif "30032" in error_msg or "Toll-Free Number Has Not Been Verified" in error_msg:
                return False, (
                    "❌ Toll-Free Number Not Verified\n\n"
                    "Your toll-free number needs verification before sending SMS.\n\n"
                    "**Quick Fix:** Buy a regular local number instead:\n"
                    "1. Go to: https://console.twilio.com/phone-numbers/search\n"
                    "2. Select 'Local' (not Toll-Free)\n"
                    "3. Ensure 'SMS' is checked\n"
                    "4. Purchase number (~$1.15/month)\n"
                    "5. Update your configuration with the new number"
                )
            else:
                return False, f"Failed to send SMS: {error_msg}"
    
    def send_risk_alert(self, phone_number, member_id, risk_level, days_to_churn):
        """Send a risk alert SMS for a specific member."""
        message = f"🚨 SIMLANE ALERT: Member {member_id} is at {risk_level} risk of churning in {days_to_churn} days. Take action now!"
        return self.send_sms(phone_number, message)
    
    def send_test_message(self, phone_number):
        """Send a test SMS message."""
        # Add timestamp to make message unique (helps with carrier filtering)
        timestamp = datetime.now().strftime("%I:%M %p")
        message = f"🎯 Simlane.ai Test [{timestamp}]: Your SMS notifications are working correctly! Reply STOP to unsubscribe."
        
        # Log the attempt for debugging
        st.info(f"📤 Attempting to send SMS to: {phone_number}")
        
        success, response = self.send_sms(phone_number, message)
        
        if success:
            # Parse the SID from response
            sid = response.split("SID: ")[1] if "SID:" in response else "Unknown"
            st.info(f"📱 Message sent with SID: {sid}")
            st.info(f"🔍 Check status at: https://console.twilio.com/us1/monitor/logs/messages/{sid}")
        
        return success, response

sms_manager = SMSManager()

# ============================================================================
# AUTHENTICATION SYSTEM
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user' not in st.session_state:
        st.session_state.user = None

def hash_password(password):
    """Hash a password for storing."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password, hashed_password):
    """Verify a password against a hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

# Mock user database (in production, use a real database)
USERS_DB = {
    'admin': {
        'password_hash': hash_password('admin123'),
        'role': 'admin',
        'name': 'Admin User'
    },
    'user': {
        'password_hash': hash_password('user123'),
        'role': 'user',
        'name': 'Standard User'
    }
}

def login_page():
    """Display the login page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #2563EB; font-size: 3rem; margin-bottom: 0.5rem;">
                🎯 Simlane.ai
            </h1>
            <p style="color: #64748b; font-size: 1.25rem;">
                Advanced Member Analytics Platform
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                if username in USERS_DB and verify_password(password, USERS_DB[username]['password_hash']):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user = USERS_DB[username]
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: #94a3b8;">
            <small>Demo credentials: admin/admin123 or user/user123</small>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# DATA GENERATION AND LOADING
# ============================================================================

@st.cache_data
def generate_sample_data(n_members=500):
    """Generate realistic sample member data."""
    np.random.seed(42)
    
    # Generate member IDs
    member_ids = [f"M{str(i).zfill(4)}" for i in range(1, n_members + 1)]
    
    # Generate group IDs (organizations)
    n_groups = 20
    groups = [f"G{i}" for i in range(1, n_groups + 1)]
    group_ids = np.random.choice(groups, n_members)
    
    # Generate enrollment dates
    start_date = datetime.now() - timedelta(days=1095)  # 3 years ago
    enrollment_dates = []
    for _ in range(n_members):
        days_ago = np.random.randint(0, 1095)
        enrollment_dates.append(start_date + timedelta(days=days_ago))
    
    # Calculate tenure
    tenure_days = [(datetime.now() - ed).days for ed in enrollment_dates]
    
    # Generate engagement metrics
    virtual_care_visits = np.random.poisson(3, n_members)
    in_person_visits = np.random.poisson(2, n_members)
    
    # Generate lifetime value (correlated with tenure and visits)
    base_ltv = np.random.normal(1000, 300, n_members)
    tenure_factor = np.array(tenure_days) / 365
    visit_factor = (virtual_care_visits + in_person_visits) / 5
    lifetime_value = np.maximum(base_ltv * (1 + tenure_factor + visit_factor), 100)
    
    # Generate churn predictions
    # Higher risk for low engagement and newer members
    risk_score = []
    for i in range(n_members):
        base_risk = np.random.random()
        
        # Factors that increase churn risk
        if virtual_care_visits[i] == 0:
            base_risk += 0.3
        if tenure_days[i] < 90:
            base_risk += 0.2
        if lifetime_value[i] < 500:
            base_risk += 0.1
            
        risk_score.append(min(base_risk, 1.0))
    
    # Convert risk scores to days until churn
    estimated_days_to_churn = []
    for score in risk_score:
        if score > 0.8:
            days = np.random.randint(0, 30)  # Immediate risk
        elif score > 0.6:
            days = np.random.randint(31, 90)  # High risk
        elif score > 0.4:
            days = np.random.randint(91, 180)  # Medium risk
        else:
            days = np.random.randint(181, 365)  # Low risk
        estimated_days_to_churn.append(days)
    
    # Categorize risk levels
    risk_category = []
    for days in estimated_days_to_churn:
        if days <= 30:
            risk_category.append('IMMEDIATE')
        elif days <= 90:
            risk_category.append('HIGH')
        elif days <= 180:
            risk_category.append('MEDIUM')
        else:
            risk_category.append('LOW')
    
    # Generate customer segments
    segments = ['Premium', 'Standard', 'Basic', 'At-Risk', 'New']
    segment = []
    for i in range(n_members):
        if lifetime_value[i] > 1500 and virtual_care_visits[i] > 5:
            segment.append('Premium')
        elif risk_category[i] in ['IMMEDIATE', 'HIGH']:
            segment.append('At-Risk')
        elif tenure_days[i] < 30:
            segment.append('New')
        elif lifetime_value[i] < 500:
            segment.append('Basic')
        else:
            segment.append('Standard')
    
    # Create DataFrame
    df = pd.DataFrame({
        'member_id': member_ids,
        'group_id': group_ids,
        'enrollment_date': enrollment_dates,
        'tenure_days': tenure_days,
        'virtual_care_visits': virtual_care_visits,
        'in_person_visits': in_person_visits,
        'lifetime_value': lifetime_value,
        'estimated_days_to_churn': estimated_days_to_churn,
        'risk_category': risk_category,
        'risk_score': risk_score,
        'segment': segment
    })
    
    return df

@st.cache_data
def load_sample_data():
    """Load sample data for the dashboard."""
    return generate_sample_data()

# ============================================================================
# VISUALIZATION HELPERS
# ============================================================================

def create_professional_header(title, subtitle):
    """Create a professional header with improved accessibility."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2563EB 0%, #0EA5E9 100%); 
                color: white; 
                padding: 2.5rem 2rem; 
                border-radius: 12px; 
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
        <h1 style="margin: 0; 
                   font-size: 2.5rem; 
                   font-weight: 700;
                   text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            🎯 {title}
        </h1>
        <p style="margin: 0.5rem 0 0 0; 
                  font-size: 1.125rem; 
                  opacity: 0.95;
                  font-weight: 500;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(label, value, delta, icon=""):
    """Create a styled metric card."""
    return f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-delta">{delta}</div>
            </div>
            <div style="font-size: 2rem; opacity: 0.8;">{icon}</div>
        </div>
    </div>
    """

def create_risk_dashboard(data):
    """Create risk analysis visualizations with consistent semantic colors."""
    # Risk distribution chart with question-based title
    risk_counts = data['risk_category'].value_counts()
    
    # Ensure consistent ordering
    risk_order = ['IMMEDIATE', 'HIGH', 'MEDIUM', 'LOW']
    risk_counts = risk_counts.reindex(risk_order, fill_value=0)
    
    fig_risk = px.bar(
        x=risk_counts.index,
        y=risk_counts.values,
        title="How many members fall into each risk bucket?",
        labels={'x': 'Risk Category', 'y': 'Number of Members'},
        color=risk_counts.index,
        color_discrete_map=RISK_COLORS
    )
    
    fig_risk.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        title_font_size=16,
        title_font_weight='bold'
    )
    
    # Time distribution chart with question title
    fig_timeline = px.histogram(
        data,
        x='estimated_days_to_churn',
        nbins=20,
        title="When will members likely churn?",
        labels={'estimated_days_to_churn': 'Days Until Churn', 'count': 'Number of Members'},
        color_discrete_sequence=['#2563EB']
    )
    
    fig_timeline.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        bargap=0.1,
        title_font_size=16,
        title_font_weight='bold'
    )
    
    return fig_risk, fig_timeline

def create_segmentation_charts(data):
    """Create customer segmentation visualizations with consistent colors."""
    # Segment distribution with question title
    segment_counts = data['segment'].value_counts()
    
    fig_segments = px.pie(
        values=segment_counts.values,
        names=segment_counts.index,
        title="Which segments are our members in?",
        hole=0.4,
        color_discrete_sequence=BRAND_COLORS
    )
    
    fig_segments.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Members: %{value}<br>Share: %{percent}<extra></extra>'
    )
    
    fig_segments.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=16,
        title_font_weight='bold'
    )
    
    # Segment risk analysis with consistent colors
    segment_risk = pd.crosstab(data['segment'], data['risk_category'])
    
    # Ensure consistent ordering
    risk_order = ['IMMEDIATE', 'HIGH', 'MEDIUM', 'LOW']
    segment_risk = segment_risk.reindex(columns=risk_order, fill_value=0)
    
    fig_risk_by_segment = px.bar(
        segment_risk.T,
        title="Which segments have the highest risk?",
        labels={'index': 'Risk Category', 'value': 'Number of Members'},
        barmode='group',
        color_discrete_map=RISK_COLORS
    )
    
    fig_risk_by_segment.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Segment",
        yaxis_title="Number of Members",
        legend_title="Risk Category",
        title_font_size=16,
        title_font_weight='bold'
    )
    
    return fig_segments, fig_risk_by_segment

# ============================================================================
# ONBOARDING WIZARD
# ============================================================================

def create_onboarding_wizard():
    """Create an onboarding wizard for new users."""
    st.markdown("""
    <div class="onboarding-header">
        <h1 style="font-size: 3rem; margin-bottom: 1rem;">🎯 Welcome to Simlane.ai</h1>
        <p style="font-size: 1.25rem; opacity: 0.95;">
            Let's get your analytics platform set up in just 3 steps
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress indicator
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 1
    
    progress = st.session_state.onboarding_step / 3
    st.progress(progress)
    
    # Step 1: Upload Data
    if st.session_state.onboarding_step == 1:
        st.header("Step 1: Upload Your Member Data")
        st.write("We'll help you map your data to our system fields.")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Your data is secure and never leaves your browser"
        )
        
        if uploaded_file:
            st.success("✅ File uploaded successfully!")
            if st.button("Continue to Mapping", type="primary"):
                st.session_state.onboarding_step = 2
                st.rerun()
    
    # Step 2: Configure Alerts
    elif st.session_state.onboarding_step == 2:
        st.header("Step 2: Set Up Your Alerts")
        st.write("Choose how you want to be notified about at-risk members.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email_alerts = st.checkbox("📧 Email Alerts", value=True)
            if email_alerts:
                st.text_input("Email Address", value="alerts@simlane.ai")
        
        with col2:
            sms_alerts = st.checkbox("📱 SMS Alerts", value=False)
            if sms_alerts:
                st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
        
        st.selectbox(
            "Alert me when risk level is:",
            options=["IMMEDIATE", "HIGH", "MEDIUM"],
            help="You'll only receive alerts for members at or above this risk level"
        )
        
        if st.button("Continue to Dashboard", type="primary"):
            st.session_state.onboarding_step = 3
            st.session_state.onboarding_complete = True
            st.rerun()
    
    # Step 3: Tour
    elif st.session_state.onboarding_step == 3:
        st.header("Step 3: Quick Tour")
        st.write("Here's what you can do with Simlane.ai:")
        
        features = [
            ("🎯 Churn Predictions", "See which members are at risk and when they might leave"),
            ("👥 Customer Segments", "Understand your member base with AI-powered segmentation"),
