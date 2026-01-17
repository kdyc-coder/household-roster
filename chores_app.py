import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Fortnightly Chore Roster", layout="wide")

st.title("🏠 Household Chore Roster")
st.write("J and L are home every 2nd week (Sunday PM to Sunday PM).")

# --- 1. DYNAMIC DATE LOGIC ---
anchor_date = datetime(2026, 1, 25)
today = datetime.now()

# Calculate how many fortnights have passed since anchor to keep the list rolling
weeks_passed = (today - anchor_date).days // 7
current_fortnight_index = weeks_passed // 2

# Generate the next 4 available start dates (2-week intervals)
start_dates = []
for i in range(4):
    d = anchor_date + timedelta(weeks=(current_fortnight_index + i) * 2)
    start_dates.append(d.strftime("%d/%m/%Y"))

selected_start_str = st.sidebar.selectbox("Select Roster Start Date (Sunday):", start_dates)
selected_start = datetime.strptime(selected_start_str, "%d/%m/%Y")

# Sidebar for J's work schedule
st.sidebar.markdown("---")
j_working_days = st.sidebar.multiselect(
    "Days J is working late (Skip Dinner):",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
)

# --- 2. ROSTER GENERATION ---
def generate_roster(start_date):
    names = ["K", "J", "L"]
    roster_list = []
    
    # Range is 0 to 7 (8 days total: Sun to Sun)
    for i in range(8):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime("%A")
        date_str = current_date.strftime("%d/%m")
        
        # Default values
        breakfast = "Self"
        lunch = "-"
        dinner = "-"
        task = "-"

        # FIRST SUNDAY (Start of roster)
        if i == 0:
            breakfast = "N/A"
            lunch = "N/A"
            dinner = names[0] # Starts with K
        
        # WEEKDAYS (Mon - Fri)
        elif 1 <= i <= 5:
            lunch = "-" # No lunch dishes on weekdays
            # Dinner rotation logic (skipping J if working)
            dinner_candidate = names[i % 3]
            if dinner_candidate == "J" and day_name in j_working_days:
                dinner = "L (J Working)"
            else:
                dinner = dinner_candidate

        # SATURDAY
        elif i == 6:
            lunch = names[i % 3]
            dinner = names[(i + 1) % 3]
            task = "🧼 CLEAN TOILET"

        # FINAL SUNDAY (End of roster)
        elif i == 7:
            lunch = names[i % 3]
            dinner = "N/A (Departed)"
            task = "🧹 VACUUM"
            # Mopping once a month (using the 4th week logic)
            if current_date.day > 21:
                task += " & ✨ MOP"

        roster_list.append({
            "Date": date_str,
            "Day": day_name,
            "Breakfast": breakfast,
            "Lunch": lunch,
            "Dinner": dinner,
            "Weekly Task": task
        })
    
    return pd.DataFrame(roster_list)

# --- 3. DISPLAY ---
df = generate_roster(selected_start)

# Using dataframe with column config to ensure "Weekly Task" is wide and visible
st.dataframe(
    df,
    column_config={
        "Weekly Task": st.column_config.TextColumn("Weekly Task", width="large"),
        "Date": st.column_config.TextColumn("Date", width="small"),
    },
    hide_index=True,
    use_container_width=True
)

st.info("The roster automatically rolls forward. Once the current fortnight ends, the next dates will appear in the sidebar.")
