import streamlit as st
from src.auth.login import init_auth_state, login_page, logout
from src.models.parking import init_parking_state
from src.dashboard.user_dashboard import render_user_dashboard
from src.dashboard.admin_dashboard import render_admin_dashboard

# Page configuration
st.set_page_config(
    page_title="UZ Smart Parking",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling - Fixed vertical spacing issues
# st.markdown("""
# <style>
#     /* Main container styles */
#     .main {
#         background-color: #f8f9fa;
#         min-height: 100vh;
#     }

#     /* Logo container styles */
#     .logo-container {
#         text-align: center;
#         margin-bottom: 1.5rem;
#         width: 100%;
#         display: flex;
#         justify-content: center;
#         align-items: center;
#         padding-top: 2rem;  /* Reduced from any previous value */
#     }

#     .logo-container img {
#         max-width: 200px;
#         margin: 0 auto;
#     }

#     /* Login container styles */
#     .login-container {
#         background-color: white;
#         padding: 2.5rem;
#         border-radius: 15px;
#         box-shadow: 0 0 20px rgba(0,0,0,0.1);
#         width: 100%;
#         max-width: 400px;
#         margin: 0 auto;
#     }

#     /* Header styles */
#     .header {
#         color: #002366;
#         font-family: 'Arial', sans-serif;
#         text-align: center;
#         margin-bottom: 2rem;
#     }

#     /* Welcome text styles */
#     .welcome-text {
#         color: #002366;
#         font-size: 1.5rem;
#         margin-bottom: 1.5rem;
#         text-align: center;
#         font-weight: 600;
#     }

#     /* Input field styles */
#     .stTextInput>div>div>input {
#         border-radius: 8px;
#         border: 1px solid #dee2e6;
#         padding: 0.75rem;
#         width: 100%;
#         font-size: 1rem;
#         transition: all 0.3s ease;
#     }

#     .stTextInput>div>div>input:focus {
#         border-color: #002366;
#         box-shadow: 0 0 0 0.2rem rgba(0, 35, 102, 0.15);
#         outline: none;
#     }

#     /* Button styles */
#     .stButton>button {
#         background-color: #002366;
#         color: white;
#         font-weight: bold;
#         border-radius: 8px;
#         padding: 0.75rem 1.5rem;
#         width: 100%;
#         margin-top: 1.5rem;
#         border: none;
#         transition: all 0.3s ease;
#     }

#     .stButton>button:hover {
#         background-color: #001a4d;
#         transform: translateY(-1px);
#         box-shadow: 0 4px 8px rgba(0,0,0,0.1);
#     }

#     /* Contact info styles */
#     .contact-info {
#         color: #6c757d;
#         font-size: 0.9rem;
#         margin-top: 1.5rem;
#         text-align: center;
#         padding-top: 1rem;
#         border-top: 1px solid #dee2e6;
#     }

#     /* Responsive adjustments */
#     @media (max-width: 768px) {
#         .login-container {
#             padding: 1.5rem;
#             margin: 1rem;
#         }

#         .logo-container img {
#             max-width: 150px;
#         }

#         .welcome-text {
#             font-size: 1.25rem;
#         }
#     }

#     /* Error message styles */
#     .stAlert {
#         border-radius: 8px;
#         margin-top: 1rem;
#     }
    
#     /* Fix for the top spacing issue */
#     .block-container {
#         padding-top: 1rem !important;
#         padding-bottom: 0rem !important;
#     }
    
#     /* Hide default Streamlit elements causing extra space */
#     .stApp header {
#         display: none !important;
#     }
    
#     /* Login page centering adjustment */
#     .login-page-wrapper {
#         display: flex;
#         justify-content: center;
#         align-items: center;
#         padding-top: 1rem;
#         min-height: calc(100vh - 80px); /* Adjusted to account for any remaining margins */
#     }
# </style>
# """, unsafe_allow_html=True)

# Initialize session states
init_auth_state()
init_parking_state()

# Main App Logic
def main():
    if not st.session_state.auth["logged_in"]:
        # Use a better centering approach
        st.markdown('<div class="login-page-wrapper">', unsafe_allow_html=True)
        login_page()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Add logout button in the top right corner
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("Logout"):
                logout()
        
        if st.session_state.auth["role"] == "admin":
            render_admin_dashboard()
        else:
            render_user_dashboard()

if __name__ == "__main__":
    main()