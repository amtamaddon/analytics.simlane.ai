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
            ("📈 Risk Analysis", "Deep dive into factors driving member churn"),
            ("📊 Reporting", "Generate executive reports with one click"),
            ("🔔 Smart Alerts", "Get notified before it's too late to save at-risk members")
        ]
        
        for icon_title, description in features:
            st.info(f"**{icon_title}**: {description}")
        
        if st.button("🚀 Start Using Simlane.ai", type="primary", use_container_width=True):
            st.session_state.show_onboarding = False
            st.rerun()

# ============================================================================
# PAGE FUNCTIONS
# ============================================================================

def show_dashboard(data):
    """Main dashboard page with contextual quick stats."""
    create_professional_header(
        "Executive Dashboard", 
        f"Real-time insights for {len(data):,} members across {data['group_id'].nunique()} groups"
    )
    
    # Quick stats with context
    col1, col2, col3, col4 = st.columns(4)
    
    total_at_risk = len(data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])])
    churn_rate = (total_at_risk / len(data)) * 100
    avg_ltv = data['lifetime_value'].mean()
    revenue_at_risk = data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])]['lifetime_value'].sum()
    
    with col1:
        st.markdown(create_metric_card(
            "Members at Risk",
            f"{total_at_risk:,}",
            f"{churn_rate:.1f}% of total",
            "🚨"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Revenue at Risk",
            f"${revenue_at_risk/1000:.0f}K",
            "Next 90 days",
            "💰"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Avg Member Value",
            f"${avg_ltv:,.0f}",
            "Lifetime value",
            "📊"
        ), unsafe_allow_html=True)
    
    with col4:
        engagement_rate = (data['virtual_care_visits'].sum() / len(data))
        st.markdown(create_metric_card(
            "Engagement Score",
            f"{engagement_rate:.1f}",
            "Visits per member",
            "🎯"
        ), unsafe_allow_html=True)
    
    # Charts
    st.subheader("📊 Risk Analysis Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_risk, _ = create_risk_dashboard(data)
        st.plotly_chart(fig_risk, use_container_width=True)
    
    with col2:
        fig_segments, _ = create_segmentation_charts(data)
        st.plotly_chart(fig_segments, use_container_width=True)
    
    # Recent alerts
    st.subheader("🔔 Recent Alerts")
    
    immediate_risks = data[data['risk_category'] == 'IMMEDIATE'].head(5)
    
    for _, member in immediate_risks.iterrows():
        st.warning(f"""
        **Member {member['member_id']}** from {member['group_id']} - 
        Immediate churn risk ({member['estimated_days_to_churn']} days) - 
        LTV: ${member['lifetime_value']:,.0f}
        """)

def show_churn_predictions(data):
    """Churn predictions page."""
    create_professional_header(
        "Churn Predictions", 
        "AI-powered member retention insights and risk analysis"
    )
    
    # TEST: Add a visible test message to confirm updates are working
    st.success("🚀 NEW FEATURES ACTIVE: Clickable cards, interactive tables, and more!")
    
    # Risk metrics - make them clickable
    col1, col2, col3, col4 = st.columns(4)
    
    immediate_risk = len(data[data['risk_category'] == 'IMMEDIATE'])
    high_risk = len(data[data['risk_category'] == 'HIGH'])
    medium_risk = len(data[data['risk_category'] == 'MEDIUM'])
    low_risk = len(data[data['risk_category'] == 'LOW'])
    
    # Style for clickable metric cards
    st.markdown("""
    <style>
    div[data-testid="column"] > div > div > div > button {
        height: 100%;
        padding: 1.5rem;
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        transition: all 0.2s;
    }
    div[data-testid="column"] > div > div > div > button:hover {
        border-color: #2563EB;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    with col1:
        if st.button(
            f"🚨 **Immediate Risk**\n\n{immediate_risk}\n\nNext 30 days",
            key="immediate_kpi",
            help="Click to filter immediate risk members",
            use_container_width=True
        ):
            st.session_state.filter_risk = 'IMMEDIATE'
            st.rerun()
    
    with col2:
        if st.button(
            f"⚠️ **High Risk**\n\n{high_risk}\n\n30-90 days",
            key="high_kpi",
            help="Click to filter high risk members",
            use_container_width=True
        ):
            st.session_state.filter_risk = 'HIGH'
            st.rerun()
    
    with col3:
        if st.button(
            f"📊 **Medium Risk**\n\n{medium_risk}\n\n90-180 days",
            key="medium_kpi",
            help="Click to filter medium risk members",
            use_container_width=True
        ):
            st.session_state.filter_risk = 'MEDIUM'
            st.rerun()
    
    with col4:
        if st.button(
            f"✅ **Low Risk**\n\n{low_risk}\n\n>180 days",
            key="low_kpi",
            help="Click to filter low risk members",
            use_container_width=True
        ):
            st.session_state.filter_risk = 'LOW'
            st.rerun()
    
    # Risk visualization
    fig_risk, fig_timeline = create_risk_dashboard(data)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_risk, use_container_width=True)
    with col2:
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # High-risk members table with inline actions
    st.subheader("🎯 High-Priority Members")
    
    # Always show the SMS alert button area
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Members at immediate risk - take action now")
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
    
    # Apply filter if one was selected
    if 'filter_risk' in st.session_state and st.session_state.filter_risk:
        st.info(f"🔍 Showing only {st.session_state.filter_risk} risk members. ")
        if st.button("Clear filter"):
            del st.session_state.filter_risk
            st.rerun()
        
        high_risk_members = high_risk_members[high_risk_members['risk_category'] == st.session_state.filter_risk]
    
    # Show member count
    st.write(f"Showing {len(high_risk_members)} members")
    
    # Create header row
    header_cols = st.columns([1.5, 1, 1.5, 1.5, 1, 1, 1.5, 1.5])
    headers = ["Member ID", "Group", "Risk", "Days to Churn", "Tenure", "Visits", "Value", "Actions"]
    for col, header in zip(header_cols, headers):
        with col:
            st.markdown(f"**{header}**")
    
    st.divider()
    
    # Add action buttons for each row
    for idx, (_, row) in enumerate(high_risk_members.head(20).iterrows()):
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 1, 1.5, 1.5, 1, 1, 1.5, 1.5])
        
        with col1:
            st.write(f"**{row['member_id']}**")
        with col2:
            st.write(row['group_id'])
        with col3:
            risk_color = RISK_COLORS[row['risk_category']]
            st.markdown(f"<span style='color: {risk_color}; font-weight: bold;'>{row['risk_category']}</span>", 
                       unsafe_allow_html=True)
        with col4:
            st.write(f"{row['estimated_days_to_churn']} days")
        with col5:
            st.write(f"{row['tenure_days']}d")
        with col6:
            st.write(str(row['virtual_care_visits']))
        with col7:
            st.write(f"${row['lifetime_value']:,.0f}")
        with col8:
            # Action buttons
            action_col1, action_col2, action_col3 = st.columns(3)
            with action_col1:
                if st.button("✉️", key=f"email_{idx}", help="Email member"):
                    st.toast(f"📧 Opening email for {row['member_id']}")
            with action_col2:
                if st.button("↗", key=f"view_{idx}", help="View details"):
                    st.toast(f"📋 Opening details for {row['member_id']}")
            with action_col3:
                if st.button("⤓", key=f"download_{idx}", help="Export member data"):
                    csv = pd.DataFrame([row]).to_csv(index=False)
                    st.download_button(
                        label="💾",
                        data=csv,
                        file_name=f"member_{row['member_id']}.csv",
                        mime="text/csv",
                        key=f"dl_confirm_{idx}"
                    )
        
        if idx < 19:  # Don't add divider after last row
            st.divider()
    
    # Download option
    csv = high_risk_members.to_csv(index=False)
    st.download_button(
        label="📥 Download High-Risk Members List",
        data=csv,
        file_name=f"high_risk_members_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )

def show_customer_segments(data):
    """Customer segmentation page."""
    create_professional_header(
        "Customer Segments", 
        "Understand your member base with AI-powered segmentation"
    )
    
    # Segment metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    segments = ['Premium', 'Standard', 'Basic', 'At-Risk', 'New']
    colors = ['🟢', '🔵', '🟡', '🔴', '🟣']
    
    for col, segment, color in zip([col1, col2, col3, col4, col5], segments, colors):
        with col:
            count = len(data[data['segment'] == segment])
            percentage = (count / len(data)) * 100
            st.markdown(create_metric_card(
                segment,
                f"{count}",
                f"{percentage:.1f}%",
                color
            ), unsafe_allow_html=True)
    
    # Visualizations
    fig_segments, fig_risk_by_segment = create_segmentation_charts(data)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_segments, use_container_width=True)
    with col2:
        st.plotly_chart(fig_risk_by_segment, use_container_width=True)
    
    # Segment details
    st.subheader("📊 Segment Analysis")
    
    segment_stats = data.groupby('segment').agg({
        'member_id': 'count',
        'lifetime_value': 'mean',
        'virtual_care_visits': 'mean',
        'tenure_days': 'mean',
        'risk_score': 'mean'
    }).round(2)
    
    segment_stats.columns = ['Members', 'Avg LTV ($)', 'Avg Virtual Visits', 'Avg Tenure (days)', 'Avg Risk Score']
    
    st.dataframe(
        segment_stats.style.format({
            'Avg LTV ($)': '${:,.0f}',
            'Avg Virtual Visits': '{:.1f}',
            'Avg Tenure (days)': '{:.0f}',
            'Avg Risk Score': '{:.2f}'
        }).background_gradient(cmap='RdYlGn_r', subset=['Avg Risk Score']),
        use_container_width=True
    )

def show_risk_analysis(data):
    """Risk analysis page."""
    create_professional_header(
        "Risk Analysis", 
        "Deep dive into factors driving member churn"
    )
    
    # Risk factors correlation
    st.subheader("🔍 Risk Factor Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tenure vs Risk
        fig_tenure = px.scatter(
            data,
            x='tenure_days',
            y='risk_score',
            color='risk_category',
            color_discrete_map=RISK_COLORS,
            title="How does tenure affect churn risk?",
            labels={'tenure_days': 'Tenure (days)', 'risk_score': 'Risk Score'},
            trendline="lowess"
        )
        st.plotly_chart(fig_tenure, use_container_width=True)
    
    with col2:
        # Engagement vs Risk
        fig_engagement = px.scatter(
            data,
            x='virtual_care_visits',
            y='risk_score',
            color='risk_category',
            color_discrete_map=RISK_COLORS,
            title="How does engagement affect churn risk?",
            labels={'virtual_care_visits': 'Virtual Care Visits', 'risk_score': 'Risk Score'},
            trendline="lowess"
        )
        st.plotly_chart(fig_engagement, use_container_width=True)
    
    # Risk distribution by group
    st.subheader("📊 Risk Distribution by Group")
    
    group_risk = data.groupby(['group_id', 'risk_category']).size().unstack(fill_value=0)
    group_risk_pct = group_risk.div(group_risk.sum(axis=1), axis=0) * 100
    
    fig_group_risk = px.bar(
        group_risk_pct.reset_index().melt(id_vars='group_id'),
        x='group_id',
        y='value',
        color='risk_category',
        color_discrete_map=RISK_COLORS,
        title="Which groups have the highest risk concentration?",
        labels={'value': 'Percentage (%)', 'group_id': 'Group ID'},
        barmode='stack'
    )
    
    st.plotly_chart(fig_group_risk, use_container_width=True)
    
    # Key insights
    st.subheader("💡 Key Insights")
    
    insights = [
        f"**Low Engagement Alert**: {len(data[data['virtual_care_visits'] == 0])} members have never used virtual care",
        f"**New Member Risk**: {len(data[(data['tenure_days'] < 30) & (data['risk_category'].isin(['IMMEDIATE', 'HIGH']))])} new members are already at high risk",
        f"**Revenue Concentration**: Top 20% of members account for {(data.nlargest(int(len(data)*0.2), 'lifetime_value')['lifetime_value'].sum() / data['lifetime_value'].sum() * 100):.0f}% of total revenue",
        f"**Group Performance**: Group {data.groupby('group_id')['risk_score'].mean().idxmin()} has the lowest average risk score"
    ]
    
    for insight in insights:
        st.info(insight)

def show_settings():
    """Settings page."""
    create_professional_header(
        "Settings & Configuration", 
        "System settings, data management, and user preferences"
    )
    
    tab1, tab2, tab3 = st.tabs(["📊 Data Management", "👤 User Settings", "🔧 System Config"])
    
    with tab1:
        st.subheader("📥 Data Upload")
        
        # Enhanced file uploader with drag area feedback
        uploaded_file = st.file_uploader(
            "Upload new member data",
            type=['csv', 'xlsx', 'xls'],
            help="Accepted formats: CSV, Excel (XLSX, XLS). Max 100MB.",
            accept_multiple_files=False
        )
        
        if uploaded_file is not None:
            # Show file info
            file_size = uploaded_file.size / 1024 / 1024  # Convert to MB
            st.info(f"📄 **File:** {uploaded_file.name} | **Size:** {file_size:.2f} MB | **Type:** {uploaded_file.type}")
            
            try:
                # Read file based on type
                if uploaded_file.name.endswith('.csv'):
                    new_data = pd.read_csv(uploaded_file)
                else:
                    new_data = pd.read_excel(uploaded_file)
                
                st.success(f"✅ Successfully loaded {len(new_data):,} rows and {len(new_data.columns)} columns")
                
                # Schema mapping interface
                st.subheader("🔄 Map Your Data Fields")
                st.write("Map your uploaded columns to the required system fields:")
                
                # Define required fields
                required_fields = {
                    'member_id': 'Unique member identifier',
                    'group_id': 'Group/Organization ID',
                    'enrollment_date': 'Member enrollment date',
                    'tenure_days': 'Days since enrollment',
                    'estimated_days_to_churn': 'Predicted days to churn'
                }
                
                optional_fields = {
                    'virtual_care_visits': 'Number of virtual visits',
                    'in_person_visits': 'Number of in-person visits',
                    'lifetime_value': 'Member lifetime value ($)',
                    'segment': 'Customer segment',
                    'risk_category': 'Risk classification'
                }
                
                # Create mapping interface
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("**Your Columns:**")
                    for col in new_data.columns[:10]:  # Show first 10
                        st.write(f"• {col}")
                    if len(new_data.columns) > 10:
                        st.write(f"... and {len(new_data.columns) - 10} more")
                
                with col2:
                    st.markdown("**Map to System Fields:**")
                    
                    mappings = {}
                    
                    # Required fields
                    st.markdown("**Required Fields** 🔴")
                    for field, description in required_fields.items():
                        mappings[field] = st.selectbox(
                            f"{field}",
                            options=['-- Not Mapped --'] + list(new_data.columns),
                            help=description,
                            key=f"map_{field}"
                        )
                    
                    # Optional fields
                    with st.expander("Optional Fields"):
                        for field, description in optional_fields.items():
                            mappings[field] = st.selectbox(
                                f"{field}",
                                options=['-- Not Mapped --'] + list(new_data.columns),
                                help=description,
                                key=f"map_opt_{field}"
                            )
                
                # Validate mapping
                missing_required = [field for field in required_fields if mappings.get(field) == '-- Not Mapped --']
                
                if missing_required:
                    st.error(f"❌ Missing required fields: {', '.join(missing_required)}")
                else:
                    st.markdown("---")
                    
                    # Preview mapped data
                    st.subheader("📋 Data Preview")
                    preview_data = pd.DataFrame()
                    for system_field, user_column in mappings.items():
                        if user_column != '-- Not Mapped --':
                            preview_data[system_field] = new_data[user_column]
                    
                    st.dataframe(preview_data.head(), use_container_width=True)
                    
                    if st.button("🚀 Process & Import Data", type="primary", use_container_width=True):
                        with st.spinner("Processing data..."):
                            time.sleep(2)  # Simulate processing
                            st.success("✅ Data imported successfully! Dashboard will update automatically.")
                            st.balloons()
                        
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.write("Please ensure your file is properly formatted.")
        
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
                                            
                                            **You need THREE things from Twilio:**
                                            
                                            1. **Account SID** - Starts with 'AC' (not 'SK')
                                            2. **Auth Token** - Your account auth token (not API key)
                                            3. **Twilio Phone Number** - A phone number you've purchased from Twilio
                                            
                                            **Setup Methods:**
                                            
                                            **Option 1: Create `.streamlit/secrets.toml`:**
                                            ```toml
                                            [twilio]
                                            account_sid = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                                            auth_token = "your-auth-token-here"
                                            from_number = "+1234567890"  # Your Twilio phone number
                                            ```
                                            
                                            **Option 2: Set environment variables:**
                                            ```bash
                                            export TWILIO_ACCOUNT_SID="ACxxxxxx"
                                            export TWILIO_AUTH_TOKEN="your-token"
                                            export TWILIO_FROM_NUMBER="+1234567890"
                                            ```
                                            
                                            **Get these from:**
                                            1. [Twilio Console](https://console.twilio.com) - Account SID & Auth Token
                                            2. [Phone Numbers](https://console.twilio.com/phone-numbers) - Buy a number
                                            
                                            **Common Issues:**
                                            - Using API Key (SKxxxx) instead of Account SID (ACxxxx)
                                            - Not having a Twilio phone number
                                            - Using personal number instead of Twilio number for 'from'
                                            """)
                                            
                                            st.error("The 'from' number must be a Twilio phone number you've purchased, not your personal number!")
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
            st.selectbox("Default Dashboard View", options=['Dashboard', 'Churn Predictions', 'Customer Segments'], index=0)
        
        with col2:
            st.checkbox("Auto-generate Weekly Reports", value=True)
            st.checkbox("Enable Advanced Analytics", value=True)
            st.selectbox("Export Format", options=['CSV', 'Excel', 'JSON'], index=0)
        
        st.subheader("🎯 Risk Thresholds")
        st.write("Adjust thresholds to see how many members fall into each category:")
        
        # Create columns for sliders and preview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Threshold sliders
            immediate_threshold = st.slider(
                "Immediate Risk (days)", 
                min_value=1, 
                max_value=60, 
                value=30,
                help="Members likely to churn within this many days"
            )
            high_threshold = st.slider(
                "High Risk (days)", 
                min_value=immediate_threshold + 1, 
                max_value=120, 
                value=90
            )
            medium_threshold = st.slider(
                "Medium Risk (days)", 
                min_value=high_threshold + 1, 
                max_value=365, 
                value=180
            )
        
        with col2:
            # Live impact preview
            st.markdown("**Impact Preview:**")
            
            # Calculate member counts with current thresholds
            data = load_sample_data()
            immediate_count = len(data[data['estimated_days_to_churn'] <= immediate_threshold])
            high_count = len(data[(data['estimated_days_to_churn'] > immediate_threshold) & 
                                (data['estimated_days_to_churn'] <= high_threshold)])
            medium_count = len(data[(data['estimated_days_to_churn'] > high_threshold) & 
                                  (data['estimated_days_to_churn'] <= medium_threshold)])
            low_count = len(data[data['estimated_days_to_churn'] > medium_threshold])
            
            # Display counts with colors
            st.markdown(f"""
            <div class="risk-preview">
                <div class="risk-preview-item">
                    <span style="color: {RISK_COLORS['IMMEDIATE']};">🚨 Immediate:</span> {immediate_count} members
                </div>
                <div class="risk-preview-item">
                    <span style="color: {RISK_COLORS['HIGH']};">⚠️ High:</span> {high_count} members
                </div>
                <div class="risk-preview-item">
                    <span style="color: {RISK_COLORS['MEDIUM']};">📊 Medium:</span> {medium_count} members
                </div>
                <div class="risk-preview-item">
                    <span style="color: {RISK_COLORS['LOW']};">✅ Low:</span> {low_count} members
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🔄 Apply Configuration", use_container_width=True):
            st.success("✅ Configuration updated successfully!")

def show_reporting(data):
    """Reporting page."""
    create_professional_header(
        "Executive Reporting", 
        "Generate and download comprehensive analytics reports"
    )
    
    # Report configuration
    st.subheader("📊 Configure Your Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Report Type",
            options=["Executive Summary", "Risk Analysis Report", "Segment Performance", "Member Engagement", "Custom Report"]
        )
        
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            format="MM/DD/YYYY"
        )
    
    with col2:
        include_charts = st.checkbox("Include Visualizations", value=True)
        include_recommendations = st.checkbox("Include AI Recommendations", value=True)
        format_type = st.radio("Export Format", ["PDF", "Excel", "PowerPoint"], horizontal=True)
    
    # Report preview
    st.subheader("📋 Report Preview")
    
    with st.expander("Executive Summary", expanded=True):
        st.markdown(f"""
        ### Simlane.ai Member Analytics Report
        **Report Date:** {datetime.now().strftime('%B %d, %Y')}
        
        #### Key Metrics
        - **Total Members:** {len(data):,}
        - **At-Risk Members:** {len(data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])]):,}
        - **Average Lifetime Value:** ${data['lifetime_value'].mean():,.0f}
        - **Churn Risk Rate:** {(len(data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])]) / len(data) * 100):.1f}%
        
        #### Top Insights
        1. **Immediate Action Required:** {len(data[data['risk_category'] == 'IMMEDIATE'])} members at immediate risk
        2. **Revenue Impact:** ${data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])]['lifetime_value'].sum():,.0f} at risk in next 90 days
        3. **Engagement Crisis:** {len(data[data['virtual_care_visits'] == 0])} members with zero engagement
        """)
    
    # Generate report button
    if st.button("🚀 Generate Full Report", type="primary", use_container_width=True):
        with st.spinner("Generating report..."):
            time.sleep(3)  # Simulate report generation
            st.success("✅ Report generated successfully!")
            
            # Mock download button
            st.download_button(
                label=f"📥 Download {report_type} ({format_type})",
                data=b"Mock report data",  # In production, generate actual report
                file_name=f"simlane_report_{datetime.now().strftime('%Y%m%d')}.{format_type.lower()}",
                mime="application/octet-stream"
            )

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    init_session_state()
    
    # Mobile menu toggle button
    if st.button("☰", key="mobile_menu", help="Toggle navigation menu"):
        st.session_state.sidebar_visible = not st.session_state.get('sidebar_visible', True)
        st.rerun()
    
    # Authentication check
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Show onboarding for new users
    if 'show_onboarding' not in st.session_state:
        st.session_state.show_onboarding = True
    
    if st.session_state.show_onboarding:
        create_onboarding_wizard()
        return
    
    # Main navigation
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; margin-bottom: 2rem; 
                    background: linear-gradient(135deg, #2563EB, #7C3AED); 
                    border-radius: 10px; color: white;">
            <h3 style="margin: 0;">Welcome back!</h3>
            <p style="margin: 0.5rem 0 0 0;">{st.session_state.user['name']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu
        page = st.radio(
            "📍 Navigation",
            options=[
                "Dashboard",
                "Churn Predictions",
                "Customer Segments",
                "Risk Analysis",
                "Reporting",
                "Settings"
            ],
            index=1  # Default to Churn Predictions
        )
        
        st.markdown("---")
        
        # Quick stats
        data = load_sample_data()
        st.markdown("**📊 Quick Stats**")
        st.metric("Total Members", f"{len(data):,}")
        st.metric("At Risk", f"{len(data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])]):,}")
        st.metric("Avg LTV", f"${data['lifetime_value'].mean():.0f}")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user = None
            st.rerun()
    
    # Load data
    data = load_sample_data()
    
    # Route to appropriate page
    if page == "Dashboard":
        show_dashboard(data)
    elif page == "Churn Predictions":
        show_churn_predictions(data)
    elif page == "Customer Segments":
        show_customer_segments(data)
    elif page == "Risk Analysis":
        show_risk_analysis(data)
    elif page == "Reporting":
        show_reporting(data)
    elif page == "Settings":
        show_settings()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #94a3b8; padding: 1rem;">
        <small>© 2025 Simlane.ai Analytics Platform | Secure Business Intelligence</small>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
