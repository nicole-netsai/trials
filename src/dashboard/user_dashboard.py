import streamlit as st
import pandas as pd
import plotly.express as px
from src.config.credentials import PURPOSE_OF_VISIT
from src.models.parking import reserve_spot, get_parking_stats
import time
import random
from datetime import datetime, timedelta

def create_slot_card(slot_num, is_reserved, reservation_info=None):
    """Create a styled card for a parking slot"""
    if is_reserved:
        st.markdown(f"""
            <div style="
                background-color: #ffebee;
                border: 2px solid #ef5350;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin: 5px;
            ">
                <h3 style="color: #c62828;">Slot {slot_num}</h3>
                <p style="color: #c62828;">Reserved</p>
                {f'<p style="color: #c62828;">Until: {reservation_info["end_time"]}</p>' if reservation_info else ''}
                {f'<p style="color: #c62828;">By: {reservation_info["user"]}</p>' if reservation_info and "user" in reservation_info else ''}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="
                background-color: #e8f5e9;
                border: 2px solid #66bb6a;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin: 5px;
            ">
                <h3 style="color: #2e7d32;">Slot {slot_num}</h3>
                <p style="color: #2e7d32;">Available</p>
            </div>
        """, unsafe_allow_html=True)

def simulate_random_changes():
    """Simulate random changes in parking status"""
    if 'last_change' not in st.session_state:
        st.session_state.last_change = time.time()
    
    # Only make changes every 5 seconds
    if time.time() - st.session_state.last_change > 5:
        st.session_state.last_change = time.time()
        lot = st.session_state.parking_lots[0]
        # Randomly free up some spots (10% chance for each reserved spot)
        for res in lot["reserved"][:]:  # Create a copy to avoid modification during iteration
            if random.random() < 0.1:  # 10% chance
                lot["reserved"].remove(res)
        # Randomly reserve some spots (5% chance for each available spot)
        available_slots = set(range(1, lot["capacity"] + 1)) - {res["slot_number"] for res in lot["reserved"]}
        for slot in list(available_slots):
            if random.random() < 0.05:  # 5% chance
                duration = random.randint(60, 240)  # 1-4 hours
                lot["reserved"].append({
                    "user_id": f"user_{random.randint(1000, 9999)}",
                    "start_time": datetime.now(),
                    "duration": duration,
                    "purpose": random.choice(PURPOSE_OF_VISIT),
                    "department": random.choice(["Mathematics", "Physics", "Computer Science", "Engineering"]),
                    "paid": True,
                    "slot_number": slot,
                    "cost": (duration / 60) * 1
                })

def render_user_dashboard():
    """Render the user dashboard"""
    st.title("🏛️ UZ Smart Parking")
    st.subheader(f"Welcome {st.session_state.auth['role'].title()} from {st.session_state.auth['department']}")

    # Auto-refresh every 5 seconds
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    if time.time() - st.session_state.last_refresh > 5:
        st.session_state.last_refresh = time.time()
        st.rerun()

    # Simulate random changes
    simulate_random_changes()

    col1, col2 = st.columns([3, 1])

    with col1:
        st.header("Available Parking Slots")
        lot = st.session_state.parking_lots[0]
        # Create a grid of parking slots
        slots_per_row = 4
        slots = []
        for i in range(lot["capacity"]):
            slots.append(i + 1)
        # Display slots in a grid
        for i in range(0, len(slots), slots_per_row):
            cols = st.columns(slots_per_row)
            for j, col in enumerate(cols):
                if i + j < len(slots):
                    slot_num = slots[i + j]
                    with col:
                        # Check if slot is reserved
                        reservation = next((res for res in lot["reserved"] if res["slot_number"] == slot_num), None)
                        is_reserved = reservation is not None
                        # Create reservation info if slot is reserved
                        reservation_info = None
                        if reservation:
                            end_time = (reservation["start_time"] + pd.Timedelta(minutes=reservation["duration"])).strftime("%H:%M")
                            reservation_info = {
                                "end_time": end_time,
                                "user": reservation["user_id"]
                            }
                        # Display slot card
                        create_slot_card(slot_num, is_reserved, reservation_info)
                        # Reservation form for available slots
                        if not is_reserved:
                            with st.expander(f"Reserve Slot {slot_num}", expanded=False):
                                purpose = st.selectbox("Purpose of Visit", PURPOSE_OF_VISIT, key=f"purpose_{slot_num}")
                                hours = st.number_input("Duration (hours)", 
                                                      min_value=1, 
                                                      max_value=24, 
                                                      value=1,
                                                      key=f"hours_{slot_num}")
                                total_cost = hours * 1  # $1 per hour
                                st.markdown(f"""
                                    <div style="
                                        background-color: #e3f2fd;
                                        border-radius: 5px;
                                        padding: 10px;
                                        margin: 10px 0;
                                    ">
                                        <p style="margin: 0;">Total cost: <strong>${total_cost}</strong></p>
                                    </div>
                                """, unsafe_allow_html=True)
                                if st.button(f"Reserve Slot {slot_num}", key=f"res_{slot_num}"):
                                    if reserve_spot(lot["id"], st.session_state.auth["username"], hours * 60, purpose, slot_num):
                                        st.success(f"Reservation confirmed for {purpose}!")
                                    else:
                                        st.error("Slot is no longer available. Please try another slot.")
                                    st.rerun()

    with col2:
        st.header("Quick Stats")
        stats = get_parking_stats()
        # Styled metrics
        st.markdown(f"""
            <div style="
                background-color: #e3f2fd;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
            ">
                <h4 style="margin: 0 0 10px 0;">Parking Status</h4>
                <p style="margin: 5px 0;">Total Slots: <strong>{stats['total_capacity']}</strong></p>
                <p style="margin: 5px 0;">Available: <strong>{stats['available_spaces']}</strong></p>
                <p style="margin: 5px 0;">Occupied: <strong>{stats['total_occupied']}</strong></p>
            </div>
        """, unsafe_allow_html=True)
        # Pie chart of purposes
        purposes = [res["purpose"] for lot in st.session_state.parking_lots for res in lot["reserved"]]
        if purposes:
            purpose_df = pd.DataFrame({"Purpose": purposes})
            fig = px.pie(purpose_df, names="Purpose", title="Parking Purposes")
            st.plotly_chart(fig, use_container_width=True) 