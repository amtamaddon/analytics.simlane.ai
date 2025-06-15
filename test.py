import streamlit as st

st.set_page_config(page_title="Test App", layout="wide")

st.title("🎯 Simlane.ai Test")
st.write("If you can see this, Streamlit is working!")

# Test session state
if 'counter' not in st.session_state:
    st.session_state.counter = 0

if st.button("Click me"):
    st.session_state.counter += 1
    st.write(f"Button clicked {st.session_state.counter} times")

st.info("Now testing the main app...")

# Simple login test
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.subheader("Login")
    username = st.text_input("Username", value="admin")
    password = st.text_input("Password", type="password", value="admin123")
    
    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.authenticated = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")
else:
    st.success("✅ You are logged in!")
    st.write("The authentication system is working.")
    
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
