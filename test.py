# ============================================================================
# SIMLANE.AI ANALYTICS PLATFORM - STREAMLIT APP
# Complete white-labeled, professional business intelligence platform
# 
# Requirements:
# pip install streamlit pandas numpy plotly bcrypt PyJWT twilio
# 
# Note: statsmodels is optional (for trendlines) but not included to reduce dependencies
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

# Semantic color palette for risk categories - WCAG AA compliant
RISK_COLORS = {
    'IMMEDIATE': '#D92D20',  # Red - 5.4:1 contrast
    'HIGH': '#F97316',       # Orange - clear progression
    'MEDIUM': '#3B82F6',     # Blue - familiar standard
    'LOW': '#16A34A'         # Green - passes contrast
}

# Risk icons for accessibility
RISK_ICONS = {
    'IMMEDIATE': '🚨',
    'HIGH': '⚠️',
    'MEDIUM': '📊',
    'LOW': '✅'
}

# Chart color sequences
RISK_COLOR_SEQUENCE = ['#D92D20', '#F97316', '#3B82F6', '#16A34A']
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
    
    /* Auto-collapse sidebar at wide screens */
    @media (min-width: 1600px) {
        section[data-testid="stSidebar"] {
            width: 5rem !important;
            transition: width 0.3s ease;
        }
        
        section[data-testid="stSidebar"]:hover {
            width: 21rem !important;
        }
        
        section[data-testid="stSidebar"] .css-1cypcdb {
            font-size: 20px !important;
        }
    }
    
    /* Larger navigation icons */
    section[data-testid="stSidebar"] .css-1cypcdb {
        font-size: 20px;
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
    
    /* Numbered steps styling */
    .step-indicator {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
        gap: 2rem;
    }
    
    .step-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .step-number {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 14px;
        transition: all 0.3s ease;
    }
    
    .step-number.active {
        background: #2563EB;
        color: white;
    }
    
    .step-number.completed {
        background: #16A34A;
        color: white;
    }
    
    .step-number.inactive {
        background: #e5e7eb;
        color: #9ca3af;
    }
    
    .step-label {
        font-size: 0.875rem;
        color: #64748b;
    }
    
    .step-label.active {
        color: #2563EB;
        font-weight: 600;
    }
    
    /* Skeleton loader */
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: 4px;
        height: 20px;
        margin: 0.5rem 0;
    }
    
    @keyframes loading {
        0% {
            background-position: 200% 0;
        }
        100% {
            background-position: -200% 0;
        }
    }
    
    /* Member row actions */
    .member-actions {
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    
    .member-row:hover .member-actions {
        opacity: 1;
    }
    
    /* Security badge */
    .security-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #16A34A;
        font-size: 0.875rem;
        margin-top: 1rem;
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
                if hasattr(st, 'secrets') and 'twilio' in st.secrets:
                    account_sid = st.secrets['twilio']['account_sid']
                    auth_token = st.secrets['twilio']['auth_token']
                    self.from_number = st.secrets['twilio'].get('from_number', self.from_number)
                # Check environment variables as fallback
                elif all(k in os.environ for k in ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN']):
                    account_sid = os.environ['TWILIO_ACCOUNT_SID']
                    auth_token = os.environ['TWILIO_AUTH_TOKEN']
                    self.from_number = os.environ.get('TWILIO_FROM_NUMBER', self.from_number)
                
                # Only initialize if we have real credentials
                if account_sid != "AC..." and auth_token != "...":
                    self.client = TwilioClient(account_sid, auth_token)
                    
            except Exception as e:
                # Silently fail - SMS features will be disabled
                pass
    
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

# Create SMS manager instance - wrapped in try/except to prevent blocking
try:
    sms_manager = SMSManager()
except Exception as e:
    print(f"SMS Manager initialization error: {e}")
    sms_manager = None

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
    if 'last_login' not in st.session_state:
        st.session_state.last_login = None

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
                    st.session_state.last_login = datetime.now()
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        # Security badge
        st.markdown("""
        <div class="security-badge">
            <span>🔒</span>
            <span>Bank-grade encryption protects your data</span>
        </div>
        """, unsafe_allow_html=True)
        
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
    segments = ['Premium', 'Standard', 'Emerging', 'New']  # Removed 'Basic', renamed 'At-Risk' to 'Emerging'
    segment = []
    for i in range(n_members):
        if lifetime_value[i] > 1500 and virtual_care_visits[i] > 5:
            segment.append('Premium')
        elif risk_category[i] in ['IMMEDIATE', 'HIGH']:
            segment.append('Emerging')  # Renamed from 'At-Risk'
        elif tenure_days[i] < 30:
            segment.append('New')
        else:
            segment.append('Standard')  # Absorbs old 'Basic' segment
    
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
# UTILITY FUNCTIONS
# ============================================================================

def show_skeleton_loader(height=300):
    """Show skeleton loader for lazy loading."""
    st.markdown(f"""
    <div style="padding: 1rem; background: white; border-radius: 8px; height: {height}px;">
        <div class="skeleton" style="width: 60%; height: 24px;"></div>
        <div class="skeleton" style="width: 40%; height: 16px; margin-top: 1rem;"></div>
        <div class="skeleton" style="width: 100%; height: {height-80}px; margin-top: 1rem;"></div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# VISUALIZATION HELPERS
# ============================================================================

def create_professional_header(title, subtitle):
    """Create a professional header with improved accessibility."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0B3E8E 0%, #0EA5E9 100%); 
                color: white; 
                padding: 2.5rem 2rem; 
                border-radius: 12px; 
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
        <h1 style="margin: 0; 
                   font-size: 2.5rem; 
                   font-weight: 700;
                   text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
            🎯 {title}
        </h1>
        <p style="margin: 0.5rem 0 0 0; 
                  font-size: 1.125rem; 
                  opacity: 0.95;
                  font-weight: 500;
                  text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
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
    
    # Create stacked bar chart for better visualization
    fig_risk_by_segment = go.Figure()
    
    for risk in risk_order:
        fig_risk_by_segment.add_trace(go.Bar(
            name=risk,
            x=segment_risk.index,
            y=segment_risk[risk],
            marker_color=RISK_COLORS[risk]
        ))
    
    fig_risk_by_segment.update_layout(
        barmode='stack',
        title="Which segments have the highest risk?",
        xaxis_title="Segment",
        yaxis_title="Number of Members",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=16,
        title_font_weight='bold',
        showlegend=True,
        legend_title="Risk Category"
    )
    
    return fig_segments, fig_risk_by_segment

# ============================================================================
# ONBOARDING WIZARD
# ============================================================================

def create_step_indicator(current_step, total_steps=4):
    """Create numbered step indicator with accessibility."""
    steps = ["Upload Data", "Map Fields", "Configure Alerts", "Tour"]
    
    html = '<div class="step-indicator" role="progressbar" aria-valuenow="' + str(current_step) + '" aria-valuemin="1" aria-valuemax="' + str(total_steps) + '">'
    
    for i, step_name in enumerate(steps, 1):
        if i < current_step:
            status = "completed"
        elif i == current_step:
            status = "active"
        else:
            status = "inactive"
        
        html += f'''
        <div class="step-item">
            <div class="step-number {status}" aria-label="Step {i} of {total_steps}: {step_name} - {status}">
                {"✓" if status == "completed" else i}
            </div>
            <span class="step-label {status}">{step_name}</span>
        </div>
        '''
    
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)

def create_onboarding_wizard():
    """Create an onboarding wizard for new users."""
    st.markdown("""
    <div class="onboarding-header">
        <h1 style="font-size: 3rem; margin-bottom: 1rem;">🎯 Welcome to Simlane.ai</h1>
        <p style="font-size: 1.25rem; opacity: 0.95;">
            Let's get your analytics platform set up in just 4 steps
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress indicator
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 1
    
    # Numbered steps instead of progress bar
    create_step_indicator(st.session_state.onboarding_step)
    
    # Save & Finish Later link
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("💾 Save & Finish Later", help="Your progress will be saved"):
            st.session_state.show_onboarding = False
            st.info("Progress saved! You can continue setup from Settings.")
            time.sleep(2)
            st.rerun()
    
    # Step 1: Upload Data
    if st.session_state.onboarding_step == 1:
        st.header("Step 1: Choose Your Data Source")
        st.write("Start with your own data or explore with our demo dataset.")
        
        # Option buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Load Demo Data", type="primary", use_container_width=True,
                        help="Instantly explore the platform with sample data"):
                st.session_state.demo_mode = True
                st.session_state.data_uploaded = True
                st.session_state.onboarding_step = 3  # Skip to alerts
                with st.spinner("Loading demo data..."):
                    time.sleep(1)
                st.warning("📊 Not live data → Connect real data in Settings")
                time.sleep(2)
                st.rerun()
        
        with col2:
            st.markdown("**or upload your own data**")
        
        st.markdown("---")
        
        uploaded_file = st.file_uploader(
            "Upload a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Your data is secure and never leaves your browser"
        )
        
        if uploaded_file:
            try:
                # Read file based on type
                if uploaded_file.name.endswith('.csv'):
                    st.session_state.uploaded_data = pd.read_csv(uploaded_file)
                else:
                    st.session_state.uploaded_data = pd.read_excel(uploaded_file)
                
                st.success(f"✅ Successfully loaded {len(st.session_state.uploaded_data):,} rows and {len(st.session_state.uploaded_data.columns)} columns")
                
                # Show preview
                st.subheader("Data Preview")
                st.dataframe(st.session_state.uploaded_data.head(), use_container_width=True)
                
                if st.button("Continue to Field Mapping", type="primary"):
                    st.session_state.onboarding_step = 2
                    st.rerun()
                    
            except Exception as e:
                # Enhanced error message with missing columns
                st.error(f"❌ Upload failed: {str(e)}")
                
                # List expected columns
                expected_cols = ['member_id', 'group_id', 'enrollment_date', 'estimated_days_to_churn']
                st.warning(f"**Missing required columns:** {', '.join(expected_cols)}")
                
                # Download template link
                template_data = pd.DataFrame({
                    'member_id': ['M0001', 'M0002'],
                    'group_id': ['G1', 'G1'],
                    'enrollment_date': ['2024-01-01', '2024-01-15'],
                    'estimated_days_to_churn': [30, 90],
                    'virtual_care_visits': [5, 2],
                    'lifetime_value': [1500, 800]
                })
                
                csv = template_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download Template",
                    data=csv,
                    file_name="simlane_template.csv",
                    mime="text/csv"
                )
    
    # Step 2: Map Fields
    elif st.session_state.onboarding_step == 2:
        st.header("Step 2: Map Your Data Fields")
        st.write("Help us understand your data by mapping your columns to our system fields.")
        
        if 'uploaded_data' not in st.session_state:
            st.warning("No data found. Please go back to Step 1.")
            if st.button("← Back to Upload"):
                st.session_state.onboarding_step = 1
                st.rerun()
            return
        
        uploaded_data = st.session_state.uploaded_data
        
        # Define required fields
        required_fields = {
            'member_id': 'Unique member identifier',
            'group_id': 'Group/Organization ID',
            'enrollment_date': 'Member enrollment date',
            'estimated_days_to_churn': 'Predicted days until churn'
        }
        
        optional_fields = {
            'tenure_days': 'Days since enrollment',
            'virtual_care_visits': 'Number of virtual visits',
            'in_person_visits': 'Number of in-person visits',
            'lifetime_value': 'Member lifetime value ($)',
            'risk_category': 'Risk classification (IMMEDIATE/HIGH/MEDIUM/LOW)'
        }
        
        # Create mapping interface
        st.subheader("🔴 Required Fields")
        
        if 'field_mappings' not in st.session_state:
            st.session_state.field_mappings = {}
        
        all_columns = ['-- Not Mapped --'] + list(uploaded_data.columns)
        
        for field, description in required_fields.items():
            # Try to auto-detect similar column names
            default_value = '-- Not Mapped --'
            for col in uploaded_data.columns:
                if field.lower() in col.lower() or col.lower() in field.lower():
                    default_value = col
                    break
            
            st.session_state.field_mappings[field] = st.selectbox(
                f"{field}",
                options=all_columns,
                index=all_columns.index(default_value) if default_value in all_columns else 0,
                help=description,
                key=f"onboard_map_{field}"
            )
        
        # Optional fields
        with st.expander("🔵 Optional Fields"):
            for field, description in optional_fields.items():
                # Try to auto-detect
                default_value = '-- Not Mapped --'
                for col in uploaded_data.columns:
                    if field.lower() in col.lower() or col.lower() in field.lower():
                        default_value = col
                        break
                
                st.session_state.field_mappings[field] = st.selectbox(
                    f"{field}",
                    options=all_columns,
                    index=all_columns.index(default_value) if default_value in all_columns else 0,
                    help=description,
                    key=f"onboard_map_opt_{field}"
                )
        
        # Validate mapping
        missing_required = [field for field in required_fields 
                          if st.session_state.field_mappings.get(field) == '-- Not Mapped --']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 1
                st.rerun()
        
        with col2:
            if missing_required:
                st.error(f"Please map these required fields: {', '.join(missing_required)}")
            else:
                if st.button("Continue to Configuration", type="primary", use_container_width=True):
                    # Process the mapped data
                    st.session_state.data_mapped = True
                    st.session_state.onboarding_step = 3
                    st.rerun()
    
    # Step 3: Configure Alerts
    elif st.session_state.onboarding_step == 3:
        st.header("Step 3: Set Up Your Alerts")
        st.write("Choose how you want to be notified about at-risk members.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email_alerts = st.checkbox("📧 Email Alerts", value=True)
            if email_alerts:
                st.text_input("Email Address", value="alerts@simlane.ai", key="onboard_email")
        
        with col2:
            sms_alerts = st.checkbox("📱 SMS Alerts", value=False)
            if sms_alerts:
                st.text_input("Phone Number", placeholder="+1 (555) 123-4567", key="onboard_phone")
        
        st.selectbox(
            "Alert me when risk level is:",
            options=["IMMEDIATE", "HIGH", "MEDIUM"],
            help="You'll only receive alerts for members at or above this risk level",
            key="onboard_alert_threshold"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()
        
        with col2:
            if st.button("Continue to Dashboard", type="primary", use_container_width=True):
                st.session_state.onboarding_step = 4
                st.session_state.onboarding_complete = True
                st.rerun()
    
    # Step 4: Tour
    elif st.session_state.onboarding_step == 4:
        st.header("Step 4: Quick Tour")
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 3
                st.rerun()
        
        with col2:
            if st.button("🚀 Start Using Simlane.ai", type="primary", use_container_width=True):
                st.session_state.show_onboarding = False
                st.session_state.data_uploaded = True  # Mark that we have data
                st.rerun()

# ============================================================================
# PAGE FUNCTIONS
# ============================================================================

def show_empty_state():
    """Show empty state with guided setup wizard."""
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h1 style="color: #2563EB; font-size: 3rem; margin-bottom: 1rem;">
            🎯 Welcome to Simlane.ai
        </h1>
        <p style="color: #64748b; font-size: 1.25rem; margin-bottom: 2rem;">
            Let's get started with your member analytics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col2:
        if st.button("📊 Load Demo Data", type="primary", use_container_width=True, 
                    help="Instantly see the platform in action with sample data"):
            st.session_state.demo_mode = True
            st.session_state.show_onboarding = False
            with st.spinner("Loading demo data..."):
                time.sleep(2)
            st.warning("📊 Not live data → Connect real data in Settings")
            st.balloons()
            time.sleep(1)
            st.rerun()
        
        st.markdown("or")
        
        if st.button("📤 Upload Your Data", use_container_width=True,
                    help="Start the guided setup wizard"):
            st.session_state.show_upload_wizard = True
            st.rerun()

def create_breadcrumbs(items):
    """Create breadcrumb navigation."""
    breadcrumb_html = " › ".join([f"<span style='color: #64748b;'>{item}</span>" for item in items[:-1]])
    if len(items) > 1:
        breadcrumb_html += f" › <span style='color: #2563EB; font-weight: 600;'>{items[-1]}</span>"
    else:
        breadcrumb_html = f"<span style='color: #2563EB; font-weight: 600;'>{items[0]}</span>"
    
    st.markdown(f"""
    <div style="padding: 0.5rem 0; font-size: 0.875rem;">
        {breadcrumb_html}
    </div>
    """, unsafe_allow_html=True)

def show_member_details(member_id, data):
    """Show detailed member information page."""
    # Breadcrumbs
    create_breadcrumbs(["Members", f"Member {member_id}"])
    
    # Get member data
    member = data[data['member_id'] == member_id].iloc[0]
    
    create_professional_header(
        f"Member Profile: {member_id}",
        f"Detailed insights and engagement history"
    )
    
    # Risk Alert Banner
    if member['risk_category'] in ['IMMEDIATE', 'HIGH']:
        st.error(f"""
        🚨 **High Priority Alert**: This member is at {member['risk_category']} risk of churning 
        within {member['estimated_days_to_churn']} days. Immediate action recommended.
        """)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_color = RISK_COLORS[member['risk_category']]
        risk_icon = RISK_ICONS[member['risk_category']]
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-label">Risk Level</p>
            <h2 class="metric-value" style="color: {risk_color};">
                <span aria-label="{member['risk_category']} risk">{risk_icon} {member['risk_category']}</span>
            </h2>
            <p class="metric-delta">{member['estimated_days_to_churn']} days to churn</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Lifetime Value",
            f"${member['lifetime_value']:,.0f}",
            f"Top {int((1 - data[data['lifetime_value'] > member['lifetime_value']].shape[0] / len(data)) * 100)}%",
            "💰"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Tenure",
            f"{member['tenure_days']} days",
            f"Since {member['enrollment_date'].strftime('%b %Y')}",
            "📅"
        ), unsafe_allow_html=True)
    
    with col4:
        total_visits = member['virtual_care_visits'] + member['in_person_visits']
        st.markdown(create_metric_card(
            "Total Visits",
            f"{total_visits}",
            f"{member['virtual_care_visits']} virtual, {member['in_person_visits']} in-person",
            "🏥"
        ), unsafe_allow_html=True)
    
    # Action Buttons
    st.subheader("🎯 Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📧 Send Email", type="primary", use_container_width=True):
            st.session_state.show_email_composer = True
            st.session_state.email_member_id = member_id
    
    with col2:
        if st.button("📱 Send SMS", use_container_width=True):
            if 'sms_alerts_enabled' in st.session_state and st.session_state.sms_alerts_enabled:
                # You would get the member's phone from your database
                success, msg = sms_manager.send_risk_alert(
                    st.session_state.alert_phone,  # In production, use member's phone
                    member_id,
                    member['risk_category'],
                    member['estimated_days_to_churn']
                )
                if success:
                    st.success("SMS sent successfully!")
                else:
                    st.error(msg)
            else:
                st.warning("Please configure SMS in Settings first")
    
    with col3:
        if st.button("📝 Add Note", use_container_width=True):
            st.session_state.show_note_form = True
    
    with col4:
        if st.button("🎯 Create Task", use_container_width=True):
            st.session_state.show_task_form = True
    
    # Email Composer
    if st.session_state.get('show_email_composer', False):
        with st.expander("📧 Compose Email", expanded=True):
            email_to = st.text_input("To:", value=f"{member_id}@example.com")
            email_subject = st.text_input("Subject:", 
                value=f"Important: Your membership needs attention")
            
            # Email templates
            template = st.selectbox("Use Template:", 
                ["Custom", "Risk Alert", "Engagement Campaign", "Win-back Offer"])
            
            if template == "Risk Alert":
                email_body = f"""Dear Member {member_id},

We've noticed you haven't been using your benefits recently. We're here to help!

Your wellness matters to us, and we want to ensure you're getting the most from your membership.

Would you like to schedule a quick call to discuss how we can better serve you?

Best regards,
The Simlane Team"""
            else:
                email_body = ""
            
            email_content = st.text_area("Message:", value=email_body, height=200)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Send Email", type="primary"):
                    st.success(f"📧 Email sent successfully to {email_to}!")
                    st.info("💡 In production, this would send a real email via your configured email service.")
                    st.session_state.show_email_composer = False
                    time.sleep(2)
                    st.rerun()
            with col2:
                if st.button("Cancel"):
                    st.session_state.show_email_composer = False
                    st.rerun()
    
    # Engagement Timeline with lazy loading
    st.subheader("📊 Engagement Timeline")
    
    with st.spinner("Loading engagement data..."):
        show_skeleton_loader(300)
        time.sleep(0.5)  # Simulate loading
        
        # Generate sample engagement data
        dates = pd.date_range(
            start=member['enrollment_date'], 
            end=datetime.now(), 
            freq='M'
        )
        
        engagement_data = pd.DataFrame({
            'date': dates,
            'virtual_visits': np.random.poisson(0.3, len(dates)),
            'in_person_visits': np.random.poisson(0.2, len(dates))
        })
        
        fig_timeline = px.line(
            engagement_data,
            x='date',
            y=['virtual_visits', 'in_person_visits'],
            title="Monthly Visit History",
            labels={'value': 'Number of Visits', 'date': 'Month'},
            color_discrete_map={'virtual_visits': BRAND_COLORS[0], 'in_person_visits': BRAND_COLORS[1]}
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Member Information
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Member Information")
        st.write(f"**Member ID:** {member['member_id']}")
        st.write(f"**Group:** {member['group_id']}")
        st.write(f"**Segment:** {member['segment']}")
        st.write(f"**Enrollment Date:** {member['enrollment_date'].strftime('%B %d, %Y')}")
        st.write(f"**Risk Score:** {member['risk_score']:.2f}")
    
    with col2:
        st.subheader("📝 Recent Notes")
        # In production, these would come from a database
        notes = [
            {"date": "2024-01-15", "note": "Called member about low engagement"},
            {"date": "2024-01-10", "note": "Sent welcome package"},
            {"date": "2024-01-05", "note": "New enrollment processed"}
        ]
        
        for note in notes:
            st.info(f"**{note['date']}**: {note['note']}")
    
    # Back button
    if st.button("← Back to Churn Predictions"):
        if 'selected_member' in st.session_state:
            del st.session_state['selected_member']
        if 'show_member_details' in st.session_state:
            del st.session_state['show_member_details']
        st.session_state.current_page = 'Churn Predictions'
        st.rerun()

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
    
    # Charts with lazy loading
    st.subheader("📊 Risk Analysis Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.spinner("Loading risk distribution..."):
            show_skeleton_loader(300)
            time.sleep(0.5)
            fig_risk, _ = create_risk_dashboard(data)
            st.plotly_chart(fig_risk, use_container_width=True)
    
    with col2:
        with st.spinner("Loading segments..."):
            show_skeleton_loader(300)
            time.sleep(0.5)
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
    # Breadcrumbs
    create_breadcrumbs(["Insights", "Churn Predictions"])
    
    create_professional_header(
        "Churn Predictions", 
        "AI-powered member retention insights and risk analysis"
    )
    
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
    
    # Risk visualization with clickable elements
    fig_risk, fig_timeline = create_risk_dashboard(data)
    
    # Get risk counts for click handling
    risk_counts = data['risk_category'].value_counts()
    risk_order = ['IMMEDIATE', 'HIGH', 'MEDIUM', 'LOW']
    risk_counts = risk_counts.reindex(risk_order, fill_value=0)
    
    # Add click event data to risk chart
    fig_risk.update_traces(
        customdata=risk_counts.index,
        hovertemplate='<b>%{x}</b><br>Members: %{y}<br>Click to filter<extra></extra>'
    )
    
    col1, col2 = st.columns(2)
    with col1:
        # Clickable risk distribution
        selected_risk = st.plotly_chart(
            fig_risk, 
            use_container_width=True,
            on_select="rerun",
            selection_mode="points"
        )
        
        # Handle click events
        if selected_risk and selected_risk.selection.points:
            clicked_risk = risk_counts.index[selected_risk.selection.points[0]['point_index']]
            st.session_state.filter_risk = clicked_risk
            st.rerun()
    
    with col2:
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # High-risk members table with enhanced header
    st.subheader("🎯 High-Priority Members")
    
    # Clear, actionable subtitle
    high_risk_members = data[data['risk_category'].isin(['IMMEDIATE', 'HIGH'])].sort_values('estimated_days_to_churn')
    immediate_count = len(high_risk_members[high_risk_members['risk_category'] == 'IMMEDIATE'])
    high_count = len(high_risk_members[high_risk_members['risk_category'] == 'HIGH'])
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{immediate_count} members** projected to churn <30 days, **{high_count} members** at 30-90 days.")
    with col2:
        # Bulk actions button
        if st.button("📋 Bulk Actions", use_container_width=True, type="primary"):
            st.session_state.show_bulk_actions = True
