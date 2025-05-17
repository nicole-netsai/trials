import streamlit as st
import pandas as pd
import plotly.express as px
from src.models.video_processor import analyze_video_feed
from src.models.parking import get_reservation_data

def render_admin_dashboard():
    """Render the admin dashboard"""
    st.title("🛠️ UZ Parking Administration")
    
    tab1, tab2, tab3 = st.tabs(["📹 Live Monitoring", "📋 Reservations", "📊 Analytics"])

    with tab1:
        st.header("CCTV Parking Monitoring")
        uploaded_video = st.file_uploader(
            "Upload CCTV footage", 
            type=["mp4", "mov"],
            key="unique_video_uploader"
        )
        
        if uploaded_video and st.button("Analyze Parking", key="analyze_button"):
            with st.spinner("Processing video..."):
                analyze_video_feed(uploaded_video)

    with tab2:
        st.header("Current Reservations")
        reservation_data = get_reservation_data()
        
        if reservation_data:
            st.dataframe(pd.DataFrame(reservation_data), 
                        use_container_width=True,
                        hide_index=True)
        else:
            st.info("No current reservations")

    with tab3:
        st.header("Parking Analytics")
        
        # Capacity utilization
        utilization_data = []
        for lot in st.session_state.parking_lots:
            utilization = (lot["occupied"] + len(lot["reserved"])) / lot["capacity"] * 100
            utilization_data.append({
                "Lot": lot["name"],
                "Capacity": lot["capacity"],
                "Occupied": lot["occupied"] + len(lot["reserved"]),
                "Utilization": utilization
            })
        
        df = pd.DataFrame(utilization_data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Lot Utilization")
            fig = px.bar(df, x="Lot", y="Utilization", color="Lot",
                        title="Parking Lot Utilization (%)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Purpose Distribution")
            purposes = [res["purpose"] for lot in st.session_state.parking_lots for res in lot["reserved"]]
            if purposes:
                purpose_df = pd.DataFrame({"Purpose": purposes})
                fig = px.pie(purpose_df, names="Purpose", 
                            title="Purpose of Visits")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No reservation data available") 