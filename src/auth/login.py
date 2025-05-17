import streamlit as st
from src.config.credentials import UZ_CREDENTIALS
import os

def init_auth_state():
    """Initialize authentication state if not exists"""
    if "auth" not in st.session_state:
        st.session_state.auth = {
            "logged_in": False,
            "role": None,
            "username": None,
            "department": None
        }

def login_page():
    """Render the login page with modern centered styling"""
   
    st.markdown('<div class="center-wrapper">', unsafe_allow_html=True)
    
    # Logo section
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    logo_path = os.path.join(os.path.dirname(__file__), "uz_logo.png")
    st.image(logo_path, width=200)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Login container
  
    
    # Welcome text
    st.markdown('<div class="welcome-text">Welcome to UZ Smart Parking</div>', unsafe_allow_html=True)
    
    # Input fields
    username = st.text_input("Staff/Student ID", 
                          placeholder="Enter your ID",
                          key="username_input")
    
    password = st.text_input("Password",
                          type="password",
                          placeholder="Enter your password",
                          key="password_input")
    
    # Login button
    if st.button("Login", key="login_button"):
        if username in UZ_CREDENTIALS and UZ_CREDENTIALS[username]["password"] == password:
            st.session_state.auth = {
                "logged_in": True,
                "role": UZ_CREDENTIALS[username]["role"],
                "username": username,
                "department": UZ_CREDENTIALS[username]["department"]
            }
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")
    
    # Contact information
    st.markdown("""
        <div class="contact-info">
            <p>For assistance, contact: <strong>parking@uz.ac.zw</strong></p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close login-container
    st.markdown('</div>', unsafe_allow_html=True)  # Close center-wrapper

def logout():
    """Handle user logout"""
    st.session_state.auth = {"logged_in": False, "role": None, "username": None, "department": None}
    st.rerun()