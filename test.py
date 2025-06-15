import streamlit as st

st.set_page_config(page_title="Simlane Debug", layout="wide")
st.title("🔍 Debugging Simlane.ai")

# Test imports one by one
st.subheader("1. Testing Imports...")

try:
    import pandas as pd
    st.success("✅ pandas imported successfully")
except Exception as e:
    st.error(f"❌ pandas import failed: {e}")

try:
    import numpy as np
    st.success("✅ numpy imported successfully")
except Exception as e:
    st.error(f"❌ numpy import failed: {e}")

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    st.success("✅ plotly imported successfully")
except Exception as e:
    st.error(f"❌ plotly import failed: {e}")

try:
    import bcrypt
    st.success("✅ bcrypt imported successfully")
except Exception as e:
    st.error(f"❌ bcrypt import failed: {e}")

try:
    import jwt
    st.success("✅ PyJWT imported successfully")
except Exception as e:
    st.error(f"❌ PyJWT import failed: {e}")

try:
    from datetime import datetime, timedelta
    st.success("✅ datetime imported successfully")
except Exception as e:
    st.error(f"❌ datetime import failed: {e}")

# Test bcrypt functionality
st.subheader("2. Testing bcrypt...")
try:
    test_password = "test123"
    hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
    verified = bcrypt.checkpw(test_password.encode('utf-8'), hashed)
    st.success(f"✅ bcrypt working: password hashed and verified = {verified}")
except Exception as e:
    st.error(f"❌ bcrypt functionality failed: {e}")

# Test session state
st.subheader("3. Testing Session State...")
if 'test_counter' not in st.session_state:
    st.session_state.test_counter = 0

if st.button("Test Session State"):
    st.session_state.test_counter += 1
    st.write(f"Counter: {st.session_state.test_counter}")

# Test authentication flow
st.subheader("4. Testing Authentication...")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    username = st.text_input("Username", value="admin")
    password = st.text_input("Password", type="password", value="admin123")
    
    if st.button("Test Login"):
        try:
            # Mock user database
            USERS_DB = {
                'admin': {
                    'password_hash': bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()),
                    'role': 'admin',
                    'name': 'Admin User'
                }
            }
            
            if username in USERS_DB and bcrypt.checkpw(password.encode('utf-8'), USERS_DB[username]['password_hash']):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user = USERS_DB[username]
                st.success("✅ Authentication successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")
        except Exception as e:
            st.error(f"❌ Authentication error: {e}")
            st.exception(e)
else:
    st.success(f"✅ Logged in as {st.session_state.username}")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# Test data generation
st.subheader("5. Testing Data Generation...")
try:
    @st.cache_data
    def generate_test_data():
        np.random.seed(42)
        n = 50
        return pd.DataFrame({
            'member_id': [f'M{i:04d}' for i in range(n)],
            'risk_category': np.random.choice(['IMMEDIATE', 'HIGH', 'MEDIUM', 'LOW'], n),
            'lifetime_value': np.random.normal(1000, 300, n)
        })
    
    data = generate_test_data()
    st.success(f"✅ Generated {len(data)} rows of test data")
    st.dataframe(data.head())
except Exception as e:
    st.error(f"❌ Data generation failed: {e}")
    st.exception(e)

# Test plotly chart
st.subheader("6. Testing Plotly Charts...")
try:
    if 'data' in locals():
        fig = px.bar(data['risk_category'].value_counts(), title="Risk Distribution")
        st.plotly_chart(fig)
        st.success("✅ Plotly chart rendered successfully")
except Exception as e:
    st.error(f"❌ Plotly chart failed: {e}")
    st.exception(e)

st.divider()
st.info("If all tests pass, the issue might be in the main app's initialization flow or CSS styling.")
