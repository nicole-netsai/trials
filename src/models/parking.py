import streamlit as st
from datetime import datetime, timedelta
from src.config.credentials import INITIAL_PARKING_LOTS, PURPOSE_OF_VISIT, ZIMBABWEAN_NAMES
import random

def init_parking_state():
    """Initialize parking lots state with some random reservations"""
    if "parking_lots" not in st.session_state:
        # Start with the initial configuration
        st.session_state.parking_lots = INITIAL_PARKING_LOTS
        
        # Get the main lot
        lot = st.session_state.parking_lots[0]
        
        # Randomly reserve some spots (between 3-7 spots)
        num_reserved = random.randint(3, 7)
        available_slots = list(range(1, lot["capacity"] + 1))
        
        for _ in range(num_reserved):
            if not available_slots:
                break
                
            # Pick a random slot
            slot_num = random.choice(available_slots)
            available_slots.remove(slot_num)
            
            # Create a random start time within the last 2 hours
            start_time = datetime.now() - timedelta(minutes=random.randint(0, 120))
            
            # Random duration between 1-4 hours
            duration = random.randint(60, 240)
            
            # Add the reservation
            lot["reserved"].append({
                "user_id": random.choice(ZIMBABWEAN_NAMES),
                "start_time": start_time,
                "duration": duration,
                "purpose": random.choice(PURPOSE_OF_VISIT),
                "department": random.choice(["Mathematics", "Physics", "Computer Science", "Engineering"]),
                "paid": True,
                "slot_number": slot_num,
                "cost": (duration / 60) * 1  # $1 per hour
            })

def reserve_spot(lot_id, user_id, duration_minutes, purpose, slot_number):
    """Reserve a specific parking slot"""
    lot = next(lot for lot in st.session_state.parking_lots if lot["id"] == lot_id)
    
    # Check if slot is already reserved
    if any(res["slot_number"] == slot_number for res in lot["reserved"]):
        return False
        
    lot["reserved"].append({
        "user_id": user_id,
        "start_time": datetime.now(),
        "duration": duration_minutes,
        "purpose": purpose,
        "department": st.session_state.auth["department"],
        "paid": False,
        "slot_number": slot_number,
        "cost": (duration_minutes / 60) * 1  # $1 per hour
    })
    return True

def get_parking_stats():
    """Get parking statistics"""
    total_capacity = sum(lot["capacity"] for lot in st.session_state.parking_lots)
    total_occupied = sum(len(lot["reserved"]) for lot in st.session_state.parking_lots)
    return {
        "total_capacity": total_capacity,
        "total_occupied": total_occupied,
        "available_spaces": total_capacity - total_occupied
    }

def get_reservation_data():
    """Get all reservation data"""
    reservation_data = []
    for lot in st.session_state.parking_lots:
        for res in lot["reserved"]:
            reservation_data.append({
                "Lot": lot["name"],
                "Slot": res["slot_number"],
                "User": res["user_id"],
                "Department": res["department"],
                "Purpose": res["purpose"],
                "Duration": f"{res['duration']//60} hours",
                "Cost": f"${res['cost']:.2f}",
                "Time": res["start_time"].strftime("%Y-%m-%d %H:%M")
            })
    return reservation_data 