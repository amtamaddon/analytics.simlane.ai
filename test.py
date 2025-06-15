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

# Custom CSS for styling
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
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    .risk-immediate {
        background-color: #FF4B4B;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
    }
    .risk-high {
        background-color: #FF8C00;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
    }
    .risk-medium {
        background-color: #4A7BFF;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
    }
    .risk-low {
        background-color: #28A745;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
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

# Generate demo data
def generate_demo_data():
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
    
    return df

# Login page
def show_login():
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
                        st.rerun()
            
            with col2:
                if st.button("Use Demo Data", use_container_width=True, type="secondary"):
                    st.session_state.logged_in = True
                    st.session_state.demo_mode = True
                    st.session_state.member_data = generate_demo_data()
                    st.session_state.setup_complete = True
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

# Setup wizard
def show_setup_wizard():
    progress = st.session_state.current_step / 4
    st.progress(progress)
    
    if st.session_state.current_step == 1:
        show_upload_step()
    elif st.session_state.current_step == 2:
        show_field_mapping()
    elif st.session_state.current_step == 3:
        show_quick_tour()
    elif st.session_state.current_step == 4:
        st.session_state.setup_complete = True
        st.rerun()

def show_upload_step():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 3rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 2rem;'>
        <h1>🎯 Welcome to Simlane.ai</h1>
        <p style='font-size: 1.2rem;'>Let's get your analytics platform set up in just 4 steps</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## Step 1: Upload Your Member Data")
    st.markdown("Start by uploading your member data file. We support CSV and Excel formats.")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Limit 200MB per file • CSV, XLSX, XLS"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Successfully loaded {len(df)} rows and {len(df.columns)} columns")
            
            st.markdown("### Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            st.session_state.member_data = df
            
            if st.button("Continue to Field Mapping", type="primary"):
                st.session_state.current_step = 2
                st.rerun()
                
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    else:
        st.info("👆 Upload a file to continue, or use the demo data option from the login page")

def show_field_mapping():
    st.markdown("## Step 2: Map Your Data Fields")
    st.markdown("Help us understand your data by mapping your columns to our system fields.")
    
    if st.session_state.member_data is not None:
        df = st.session_state.member_data
        columns = df.columns.tolist()
        
        st.markdown("### 🔴 Required Fields")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("member_id", columns, index=0 if 'member_id' in columns else None)
            st.selectbox("enrollment_date", columns, index=columns.index('enrollment_date') if 'enrollment_date' in columns else None)
        
        with col2:
            st.selectbox("group_id", columns, index=columns.index('group_id') if 'group_id' in columns else None)
            st.selectbox("estimated_days_to_churn", columns, index=columns.index('estimated_days_to_churn') if 'estimated_days_to_churn' in columns else None)
        
        with st.expander("🔵 Optional Fields"):
            st.multiselect("Select optional fields to include", columns)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        with col2:
            if st.button("Continue", type="primary", use_container_width=True):
                st.session_state.current_step = 3
                st.rerun()

def show_quick_tour():
    st.markdown("## Quick Tour")
    st.markdown("Here's what you can do with Simlane.ai:")
    
    features = [
        ("🎯", "Churn Predictions", "See which members are at risk and when they might leave"),
        ("👥", "Customer Segments", "Understand your member base with AI-powered segmentation"),
        ("📈", "Risk Analysis", "Deep dive into factors driving member churn"),
        ("📊", "Reporting", "Generate executive reports with one click"),
        ("🔔", "Smart Alerts", "Get notified before it's too late to save at-risk members")
    ]
    
    for icon, title, desc in features:
        st.markdown(f"""
        <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
            <h4>{icon} {title}:</h4>
            <p style='margin: 0; color: #666;'>{desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
    with col2:
        if st.button("🚀 Start Using Simlane.ai", type="primary", use_container_width=True):
            st.session_state.current_step = 4
            st.rerun()

# Main dashboard
def show_dashboard():
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
    
    # Main content based on selected page
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

def show_churn_predictions():
    st.title("🎯 Churn Predictions")
    st.markdown("AI-powered member retention insights and risk analysis")
    
    if st.session_state.member_data is None:
        st.session_state.member_data = generate_demo_data()
    
    df = st.session_state.member_data
    
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
    
    # Create display dataframe
    display_df = pd.DataFrame({
        'Member ID': high_risk['member_id'],
        'Group': high_risk['group_id'],
        'Risk': high_risk['risk_level'],
        'Days to Churn': high_risk['estimated_days_to_churn'],
        'Tenure': high_risk['tenure_days'].astype(str) + ' days',
        'Visits': high_risk['virtual_care_visits'] + high_risk['in_person_visits'],
        'Value': '$' + high_risk['lifetime_value'].round(2).astype(str),
        'Actions': ['View Details'] * len(high_risk)
    })
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def show_customer_segments():
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
    
    # Risk distribution by segment
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Risk Distribution")
        segment_risk = pd.crosstab(df['segment'], df['risk_level'], normalize='index') * 100
        fig = px.bar(
            segment_risk.T,
            barmode='group',
            title="Risk Levels by Segment (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Churn by Cluster")
        churn_by_segment = df.groupby('segment')['risk_score'].mean() * 100
        fig = px.bar(
            x=churn_by_segment.index,
            y=churn_by_segment.values,
            title="Average Churn Risk by Segment",
            color=churn_by_segment.index
        )
        fig.update_layout(showlegend=False, yaxis_title="Churn Rate (%)")
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

def show_member_details():
    st.title("👤 Member Details Drilldown")
    
    df = st.session_state.member_data
    
    # Member selector
    selected_member = st.selectbox(
        "Select a member to view details",
        df['member_id'].tolist(),
        index=0
    )
    
    member = df[df['member_id'] == selected_member].iloc[0]
    
    # Member profile header
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 12px; color: white; margin-bottom: 2rem;'>
        <h2>🎯 Member Profile: {selected_member}</h2>
        <p>Detailed insights and engagement history</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk alert
    if member['risk_level'] in ['Immediate', 'High']:
        st.error(f"⚠️ High Priority Alert: This member is at {member['risk_level']} risk of churning within {member['estimated_days_to_churn']} days. Immediate action recommended.")
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Risk Level", member['risk_level'], 
                  f"{member['estimated_days_to_churn']} days to churn")
    with col2:
        st.metric("Lifetime Value", f"${member['lifetime_value']:.2f}", "Top 66%")
    with col3:
        st.metric("Tenure", f"{member['tenure_days']} days", 
                  f"Since {member['enrollment_date'].strftime('%b %Y') if pd.notna(member['enrollment_date']) else 'N/A'}")
    with col4:
        st.metric("Total Visits", 
                  member['virtual_care_visits'] + member['in_person_visits'],
                  f"{member['virtual_care_visits']} virtual, {member['in_person_visits']} in-person")
    with col5:
        st.metric("Segment", member['segment'])
    
    # Action buttons
    st.markdown("### 🎯 Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.button("📧 Send Email", use_container_width=True)
    with col2:
        st.button("💬 Send SMS", use_container_width=True)
    with col3:
        st.button("📝 Add Note", use_container_width=True)
    with col4:
        st.button("✅ Create Task", use_container_width=True)
    
    # Engagement Timeline
    st.markdown("### 📈 Engagement Timeline")
    
    # Generate sample timeline data
    dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
    timeline_data = pd.DataFrame({
        'date': dates,
        'virtual_visits': np.random.poisson(2, 12),
        'in_person_visits': np.random.poisson(1, 12)
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timeline_data['date'],
        y=timeline_data['virtual_visits'],
        mode='lines+markers',
        name='Virtual Visits',
        line=dict(color='#4A7BFF')
    ))
    fig.add_trace(go.Scatter(
        x=timeline_data['date'],
        y=timeline_data['in_person_visits'],
        mode='lines+markers',
        name='In-Person Visits',
        line=dict(color='#28A745')
    ))
    fig.update_layout(
        title="Monthly Visit History",
        xaxis_title="Month",
        yaxis_title="Number of Visits",
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Member Information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Member Information")
        st.markdown(f"""
        - **Member ID:** {member['member_id']}
        - **Group:** {member['group_id']}
        - **Segment:** {member['segment']}
        - **Enrollment Date:** {member['enrollment_date'].strftime('%B %d, %Y') if pd.notna(member['enrollment_date']) else 'N/A'}
        - **Risk Score:** {member['risk_score']:.2f}
        """)
    
    with col2:
        st.markdown("### 📝 Recent Notes")
        st.info("2024-01-15: Called member about low engagement")
        st.info("2024-01-10: Sent welcome package")
        st.info("2024-01-05: New enrollment processed")

def show_executive_reporting():
    st.title("📊 Executive Reporting")
    st.markdown("Generate and download comprehensive analytics reports")
    
    # Report configuration
    st.markdown("### 📋 Configure Your Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Report Type",
            ["Executive Summary", "Detailed Analytics", "Risk Assessment", "Segment Analysis"]
        )
        
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
    
    with col2:
        st.markdown("### Include in Report:")
        include_visuals = st.checkbox("Include Visualizations", value=True)
        include_recommendations = st.checkbox("Include AI Recommendations", value=True)
        
        export_format = st.radio(
            "Export Format",
            ["PDF", "Excel", "PowerPoint"],
            horizontal=True
        )
    
    # Report preview
    st.markdown("### 📄 Report Preview")
    
    with st.container():
        st.markdown("""
        <div style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            <h2>Simlane.ai Member Analytics Report</h2>
            <p><strong>Report Date:</strong> June 15, 2025</p>
            
            <h3>Key Metrics</h3>
            <ul>
                <li><strong>Total Members:</strong> 500</li>
                <li><strong>At-Risk Members:</strong> 210</li>
                <li><strong>Average Lifetime Value:</strong> $3,494</li>
                <li><strong>Churn Risk Rate:</strong> 42.0%</li>
            </ul>
            
            <h3>Top Insights</h3>
            <ol>
                <li>Immediate Action Required: 109 members at immediate risk</li>
                <li>Revenue Impact: $730,003 at risk in next 90 days</li>
                <li>Engagement Crisis: 32 members with zero engagement</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🚀 Generate Full Report", type="primary", use_container_width=True):
        with st.spinner("Generating report..."):
            time.sleep(2)
        st.success("✅ Report generated successfully!")
        st.download_button(
            label=f"📥 Download {export_format} Report",
            data=b"Sample report data",
            file_name=f"simlane_report_{datetime.now().strftime('%Y%m%d')}.{export_format.lower()}",
            mime="application/octet-stream"
        )

def show_settings():
    st.title("⚙️ Settings & Configuration")
    st.markdown("System settings, data management, and user preferences")
    
    tabs = st.tabs(["📊 Data Management", "👤 User Settings", "🔔 Notification Preferences"])
    
    with tabs[0]:
        st.markdown("### Data Management")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            with st.spinner("Refreshing data..."):
                st.session_state.member_data = generate_demo_data()
                time.sleep(1)
            st.success("Data refreshed successfully!")
        
        if st.button("📥 Import New Data", use_container_width=True):
            st.info("Upload functionality would go here")
        
        if st.button("📤 Export Current Data", use_container_width=True):
            st.download_button(
                label="Download CSV",
                data=st.session_state.member_data.to_csv(index=False),
                file_name="member_data_export.csv",
                mime="text/csv"
            )
    
    with tabs[1]:
        st.markdown("### User Profile")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("First Name", value="Admin")
            st.text_input("Email", value="admin@simlane.ai")
            st.text_input("Phone Number", value="+1 (555) 123-4567")
        
        with col2:
            st.text_input("Last Name", value="User")
            st.selectbox("Role", ["Admin", "Manager", "Analyst"])
            st.selectbox("Timezone", ["EST", "CST", "MST", "PST"])
        
        if st.button("Save Profile", type="primary"):
            st.success("Profile updated successfully!")
    
    with tabs[2]:
        st.markdown("### Notification Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📧 Email Alerts")
            st.checkbox("Daily Summary", value=True)
            st.checkbox("High Risk Alerts", value=True)
            st.checkbox("Weekly Reports", value=False)
        
        with col2:
            st.markdown("#### 💬 SMS Alerts")
            st.checkbox("Immediate Risk Only", value=True)
            st.checkbox("Daily Summary", value=False)
            st.slider("SMS Alert Threshold", 0, 100, 80, help="Only send SMS for members with risk score above this threshold")
        
        st.markdown("### 🎯 Risk Thresholds")
        st.markdown("Adjust thresholds to see how many members fall into each category:")
        
        immediate_threshold = st.slider("Immediate Risk (days)", 0, 90, 30)
        high_threshold = st.slider("High Risk (days)", 30, 180, 90)
        medium_threshold = st.slider("Medium Risk (days)", 90, 365, 180)
        
        if st.button("Apply Configuration", type="primary", use_container_width=True):
            st.success("Configuration saved successfully!")

# Main app logic
def main():
    if not st.session_state.logged_in:
        show_login()
    elif not st.session_state.setup_complete and not st.session_state.demo_mode:
        show_setup_wizard()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
