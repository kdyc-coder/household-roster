import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Household Chore Roster", layout="wide")

st.title("🏠 Fortnightly Chore Roster")
st.write("J and L are home this week. Breakfast is 'Self'. No lunch dishes on weekdays.")

# 1. User Input: Is J working?
st.sidebar.header("Settings")
j_working_days = st.sidebar.multiselect(
    "Select days J is working late (Exempt from Dinner):",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
)

# 2. Logic to build the roster
def generate_data():
    anchor_date = datetime(2026, 1, 25)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    names = ["K", "J", "L"]
    
    roster_list = []
    
    for i, day_name in enumerate(days):
        current_date = anchor_date + timedelta(days=i)
        
        # Lunch logic (Weekends only)
        lunch = names[i % 3] if day_name in ["Saturday", "Sunday"] else "-"
        
        # Dinner logic (Rotate, but skip J if working)
        dinner_candidate = names[i % 3]
        if dinner_candidate == "J" and day_name in j_working_days:
            # If J is working, give it to the next person in rotation (L or K)
            dinner_assigned = names[(i + 1) % 3]
            note = " (J Working)"
        else:
            dinner_assigned = dinner_candidate
            note = ""

        # Cleaning logic
        task = "-"
        if day_name == "Saturday":
            task = "🧼 CLEAN TOILET"
        elif day_name == "Sunday":
            task = "🧹 VACUUM"
            # Mopping once a month - checking if it's the 4th week of the month
            if current_date.day > 21:
                task += " & ✨ MOP"

        roster_list.append({
            "Day": day_name,
            "Date": current_date.strftime("%d/%m"),
            "Lunch": lunch,
            "Dinner": f"{dinner_assigned}{note}",
            "Weekly Task": task
        })
    
    return pd.DataFrame(roster_list)

# Display the table
df = generate_data()
st.table(df)

st.info("💡 Reminder: J and L are with me every 2nd week from Sunday PM to Sunday PM.")