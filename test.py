# ============================================================================
# SIMLANE.AI ANALYTICS PLATFORM - STREAMLIT APP (UPDATED JUNE 2025)
# Implements "MVP" tier of the new UI / UX brief:
#   • Demo‑data toggle
#   • Single‑hue risk palette
#   • Click‑through KPI cards → table filtering
#   • Cleaner colour rules throughout
#   • Upload workflow persists real data in session
# (Email/SMS actions still stubbed; alert engine & report export reserved for next tier)
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import bcrypt, jwt, os, time
from datetime import datetime, timedelta

# Twilio (optional)
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

# -----------------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Simlane.ai Analytics Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# GLOBAL THEME CONSTANTS  ▸  single‑hue palette + shades
# -----------------------------------------------------------------------------
COLOR_MAP = {
    "IMMEDIATE": "#004C99",  # darkest
    "HIGH": "#0066CC",
    "MEDIUM": "#3385D9",
    "LOW": "#66A3E0",       # lightest
}
BRAND_BLUE = "#0066CC"

# -----------------------------------------------------------------------------
# CUSTOM CSS  (unchanged except border‑left now uses BRAND_BLUE only)
# -----------------------------------------------------------------------------
st.markdown(f"""
<style>
    #MainMenu, footer, header, .viewerBadge_container__1QSob, .viewerBadge_link__1S2L9, .viewerBadge_text__1JaDK {{display:none;}}
    .main .block-container {{padding-top:1rem; padding-bottom:1rem;}}
    .main-header {{background:linear-gradient(135deg,{BRAND_BLUE} 0%,#00B8A3 100%);padding:1.5rem 2rem;border-radius:12px;margin-bottom:2rem;box-shadow:0 4px 20px rgba(0,102,204,.2);}}
    .main-header h1 {{color:#fff;font-size:1.8rem;font-weight:600;margin:0}}
    .metric-card {{background:#fff;padding:1.5rem;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.08);border-left:4px solid {BRAND_BLUE};margin:1rem 0;transition:.2s}}
    .metric-card:hover {{transform:translateY(-2px);box-shadow:0 4px 20px rgba(0,0,0,.12);}}
    .metric-value {{font-size:2rem;font-weight:700;color:{BRAND_BLUE};margin:.5rem 0;}}
    .metric-label {{font-size:.9rem;color:#6B7280;font-weight:500;margin:0;}}
    .metric-change {{font-size:.85rem;margin:.5rem 0 0 0;font-weight:500;}}
    .metric-change.positive {{color:#00CC88;}}
    .metric-change.negative {{color:#FF6B35;}}
    .alert {{padding:1rem 1.5rem;border-radius:8px;margin:1rem 0;border-left:4px solid;}}
    .alert-danger {{background:#FEF2F2;border-color:#FF6B35;color:#991B1B;}}
    .alert-warning {{background:#FFFBEB;border-color:#F59E0B;color:#92400E;}}
    .alert-success {{background:#ECFDF5;border-color:#00CC88;color:#065F46;}}
    .alert-info {{background:#EFF6FF;border-color:{BRAND_BLUE};color:#1E40AF;}}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SMS MANAGER (unchanged)
# -----------------------------------------------------------------------------
class SMSManager:
    def __init__(self):
        self.client, self.from_number = None, None
        if TWILIO_AVAILABLE:
            try:
                if 'twilio' in st.secrets:
                    s = st.secrets['twilio']; self.from_number = s.get('from_number','+1234567890')
                    self.client = TwilioClient(s['account_sid'], s['auth_token'])
                elif {'TWILIO_ACCOUNT_SID','TWILIO_AUTH_TOKEN'} <= set(os.environ):
                    self.from_number = os.environ.get('TWILIO_FROM_NUMBER','+1234567890')
                    self.client = TwilioClient(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
            except Exception as e:
                st.error(f"Twilio init failed: {e}")

    def send_risk_alert(self, phone, mem_id, level, days):
        if not self.client:
            return False, "Twilio not configured"
        try:
            m = self.client.messages.create(body=f"🚨 SIMLANE ALERT: Member {mem_id} is {level} risk – churn in {days}d.", from_=self.from_number, to=phone)
            return True, f"Sent (SID {m.sid})"
        except Exception as e:
            return False, str(e)

sms_manager = SMSManager()

# -----------------------------------------------------------------------------
# AUTH  (unchanged)
# -----------------------------------------------------------------------------
import bcrypt, jwt
class AuthManager:
    _USERS = {
        "admin":    ("simlane2025","admin","Admin User"),
        "analyst":  ("analyst123","analyst","Data Analyst"),
        "executive":("executive456","executive","Executive User"),
    }
    def authenticate(self,u,p):
        if u in self._USERS and bcrypt.checkpw(p.encode(),bcrypt.hashpw(self._USERS[u][0].encode(),bcrypt.gensalt())):
            st.session_state.update({
                'auth_token': jwt.encode({'u':u,'r':self._USERS[u][1],'exp':datetime.utcnow()+timedelta(hours=8)},"simlane_secret_key_2025",algorithm='HS256'),
                'user':{'role':self._USERS[u][1],'name':self._USERS[u][2]},'authenticated':True})
            return True
        return False
    def check(self): return st.session_state.get('authenticated',False)
    def logout(self): st.session_state.clear()

auth = AuthManager()

# -----------------------------------------------------------------------------
# DATA  ▸  demo loader + upload persistence
# -----------------------------------------------------------------------------
@st.cache_data
def load_sample_data():
    np.random.seed(42)
    n = 500
    df = pd.DataFrame({
        'member_id':[f'M{i:04d}' for i in range(1,n+1)],
        'group_id':[f'G{np.random.randint(1,21)}' for _ in range(n)],
        'status':np.random.choice(['active','cancelled'],n,p=[0.72,0.28]),
        'cluster':np.random.choice(range(4),n,p=[.25,.3,.2,.25]),
        'pets_covered':np.random.choice([1,2,3,4],n,p=[.4,.3,.2,.1]),
        'virtual_care_visits':np.random.poisson(2.5,n),
        'tenure_days':np.random.exponential(300,n).astype(int),
        'estimated_days_to_churn':np.random.exponential(180,n).astype(int),
        'monthly_premium':np.random.normal(85,20,n).round(2),
        'lifetime_value':np.random.normal(1250,300,n).round(2)
    })
    df['risk_category'] = pd.cut(df['estimated_days_to_churn'],[-1,30,90,180,9e9],labels=["IMMEDIATE","HIGH","MEDIUM","LOW"])
    df['industry'] = np.random.choice(['Tech','Health','Finance','Retail','Mfg'],n)
    df['location'] = np.random.choice(['NY','CA','TX','FL','IL'],n)
    return df

@st.cache_data
def cluster_summary(df):
    s = df.groupby('cluster').agg({'member_id':'count','pets_covered':'mean','tenure_days':'mean',
                                   'virtual_care_visits':'mean','monthly_premium':'mean','lifetime_value':'mean',
                                   'status':lambda x:(x=='cancelled').mean()}).round(2)
    s.columns=['Size','Avg_Pets','Avg_Tenure','Avg_Visits','Avg_Premium','Avg_LTV','Churn_Rate']
    return s

# -----------------------------------------------------------------------------
# UI HELPERS
# -----------------------------------------------------------------------------

def header(title,subtitle):
    st.markdown(f"""<div class='main-header'><h1>🎯 {title}</h1><p>{subtitle}</p></div>""",unsafe_allow_html=True)

def metric_card(label,value,icon="📊"):
    st.markdown(f"""<div class='metric-card'><p class='metric-label'>{icon} {label}</p><h2 class='metric-value'>{value}</h2></div>""",unsafe_allow_html=True)

def alert_box(msg,kind="info"):
    ic = {"danger":"🚨","warning":"⚠️","success":"✅","info":"ℹ️"}.get(kind,"ℹ️")
    st.markdown(f"""<div class='alert alert-{kind}'>{ic} {msg}</div>""",unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# LOGIN PAGE
# -----------------------------------------------------------------------------

def login():
    st.markdown("""<div class='login-container'><div class='login-header'><h1>Simlane.ai</h1><p>Analytics Platform</p></div></div>""",unsafe_allow_html=True)
    with st.form("login"):
        st.subheader("🔐 Secure Login")
        u = st.text_input("Username")
        p = st.text_input("Password",type="password")
        if st.form_submit_button("Sign In",use_container_width=True):
            if auth.authenticate(u,p): st.rerun() 
            else: st.error("Invalid credentials")
    with st.expander("🔑 Demo Credentials"):
        st.info("""admin/simlane2025 • analyst/analyst123 • executive/executive456""")

# -----------------------------------------------------------------------------
# CHURN DASHBOARD
# -----------------------------------------------------------------------------

def churn_dashboard(df):
    header("Churn Predictions","AI‑powered member retention insights")

    # KPI cards ▸ click to filter
    col1,col2,col3,col4 = st.columns(4)
    clicks = [
        col1.button(f"🚨\n{(df['risk_category']=='IMMEDIATE').sum()}\nImmediate",key="im"),
        col2.button(f"⚠️\n{(df['risk_category']=='HIGH').sum()}\nHigh",key="hi"),
        col3.button(f"📊\n{(df['risk_category']=='MEDIUM').sum()}\nMedium",key="med"),
        col4.button(f"✅\n{(df['risk_category']=='LOW').sum()}\nLow",key="low")
    ]
    mapping = {0:"IMMEDIATE",1:"HIGH",2:"MEDIUM",3:"LOW"}
    for i,c in enumerate(clicks):
        if c: st.session_state['risk_filter'] = mapping[i]
    if 'risk_filter' not in st.session_state: st.session_state['risk_filter'] = 'ALL'

    filter_tag = st.session_state['risk_filter']
    if filter_tag!='ALL': alert_box(f"Showing only {filter_tag} risk members – click any other card to change",'info')

    # Charts
    rc = df['risk_category'].value_counts().reindex(list(COLOR_MAP.keys()))
    fig = px.bar(x=rc.index,y=rc.values,labels={'x':'Risk','y':'Members'},color=rc.index,color_discrete_map=COLOR_MAP,height=400)
    fig2 = px.histogram(df[df['status']=='active'],x='estimated_days_to_churn',nbins=30,color_discrete_sequence=[BRAND_BLUE],height=400)
    c1,c2 = st.columns(2); c1.plotly_chart(fig,use_container_width=True); c2.plotly_chart(fig2,use_container_width=True)

    # Table
    view = df if filter_tag=='ALL' else df[df['risk_category']==filter_tag]
    st.subheader("🎯 Focus Members")
    st.dataframe(view.sort_values('estimated_days_to_churn')[['member_id','group_id','risk_category','estimated_days_to_churn','tenure_days','virtual_care_visits','lifetime_value']].head(20),use_container_width=True,height=400)

# -----------------------------------------------------------------------------
# SEGMENT PAGE  (minimal change)
# -----------------------------------------------------------------------------

def segment_page(df,summary):
    header("Customer Segments","Behavioural clusters & value lenses")
    col1,col2 = st.columns(2)
    hv = summary['Avg_LTV'].idxmax(); col1.markdown(alert_box(f"Cluster {hv} tops LTV at ${summary.loc[hv,'Avg_LTV']:,.0f}",'success'),unsafe_allow_html=True)
    hc = summary['Churn_Rate'].idxmax(); col2.markdown(alert_box(f"Cluster {hc} highest churn {summary.loc[hc,'Churn_Rate']*100:.1f}%",'warning'),unsafe_allow_html=True)
    fig = px.scatter(df,x='tenure_days',y='virtual_care_visits',color='cluster',size='lifetime_value',hover_data=['member_id','risk_category'],color_discrete_sequence=list(COLOR_MAP.values()),height=500)
    st.plotly_chart(fig,use_container_width=True)
    st.subheader("📊 Segment Overview")
    disp = summary.copy(); disp['Churn_Rate']=(disp['Churn_Rate']*100).round(1).astype(str)+'%'
    st.dataframe(disp,use_container_width=True)

# -----------------------------------------------------------------------------
# SETTINGS (Upload persists data + demo toggle)
# -----------------------------------------------------------------------------

def settings_page():
    header("Settings & Configuration","Data management and preferences")
    tab1,tab2 = st.tabs(["📊 Data","👤 Profile"])
    with tab1:
        upl = st.file_uploader("Upload member data CSV",type=['csv'])
        if upl is not None:
            try:
                st.session_state['uploaded_data'] = pd.read_csv(upl)
                st.success(f"Loaded {len(st.session_state['uploaded_data'])} rows – uncheck 'Use Demo' to view.")
            except Exception as e:
                st.error(f"Failed: {e}")
        if 'uploaded_data' in st.session_state:
            st.dataframe(st.session_state['uploaded_data'].head(),use_container_width=True)

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

def main():
    if not auth.check():
        login(); return

    # SIDEBAR – welcome + demo toggle
    st.sidebar.markdown(f"""<div style='text-align:center;padding:1rem;background:linear-gradient(135deg,{BRAND_BLUE},#00B8A3);border-radius:10px;color:#fff;'><h3>Welcome!</h3><p>{st.session_state['user']['name']}</p></div>""",unsafe_allow_html=True)
    use_demo = st.sidebar.checkbox("Use Demo Data",value=st.session_state.get('use_demo_data',True))
    st.session_state['use_demo_data'] = use_demo

    if use_demo:
        data = load_sample_data()
    else:
        data = st.session_state.get('uploaded_data',None)
        if data is None:
            st.sidebar.warning("No uploaded data found – falling back to demo.")
            data = load_sample_data()

    page = st.sidebar.radio("Navigation",["⚠️ Churn Predictions","👥 Customer Segments","⚙️ Settings"])
    st.sidebar.markdown("---")
    st.sidebar.metric("Total Members",f"{len(data):,}")
    st.sidebar.metric("At Risk",f"{len(data[data['risk_category'].isin(['IMMEDIATE','HIGH'])]):,}")
    st.sidebar.metric("Churn Rate",f"{(data['status']=='cancelled').mean():.1%}")
    if st.sidebar.button("Logout",use_container_width=True): auth.logout(); st.rerun()

    if page.startswith("⚠️"):
        churn_dashboard(data)
    elif page.startswith("👥"):
        segment_page(data,cluster_summary(data))
    else:
        settings_page()

    st.markdown("---")
    st.markdown("<div style='text-align:center;color:#6B7280;padding:1rem;'>© 2025 Simlane.ai Analytics Platform</div>",unsafe_allow_html=True)

if __name__ == "__main__":
    main()
