import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Household Chore Roster", layout="wide")

st.title("🏠 Household Chore Roster")
st.write("J and L are home Sunday PM to Sunday PM every 2nd week.")

# --- 1. DYNAMIC DATE & ROTATION LOGIC ---
anchor_date = datetime(2026, 1, 25)
today = datetime.now()

# Calculate fortnights passed to rotate weekly tasks fairly over time
weeks_passed = (today - anchor_date).days // 7
current_fortnight_index = weeks_passed // 2

# Dropdown for the next 4 "On-Weeks"
start_dates = []
for i in range(4):
    d = anchor_date + timedelta(weeks=(current_fortnight_index + i) * 2)
    start_dates.append(d.strftime("%d/%m/%Y"))

selected_start_str = st.sidebar.selectbox("Select Roster Start Date:", start_dates)
selected_start = datetime.strptime(selected_start_str, "%d/%m/%Y")

# Calculate rotation offset based on which fortnight we are in
# This ensures K, J, and L take turns with the big weekly cleaning tasks
fortnight_count = (selected_start - anchor_date).days // 14
names = ["K", "J", "L"]

st.sidebar.markdown("---")
j_working_days = st.sidebar.multiselect(
    "Days J is working late (Exempt from Dinner):",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
)

# --- 2. ROSTER GENERATION ---
def generate_roster(start_date, f_index):
    roster_list = []
    
    # Cleaning Task Assignments (Rotating based on the fortnight index)
    # Fortnight 1: K=Toilet, J=Vacuum, L=Mop (if due)
    # Fortnight 2: J=Toilet, L=Vacuum, K=Mop (if due) ... and so on.
    toilet_cleaner = names[f_index % 3]
    vacuum_cleaner = names[(f_index + 1) % 3]
    mop_cleaner = names[(f_index + 2) % 3]

    for i in range(8):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime("%A")
        date_str = current_date.strftime("%d/%m")
        
        breakfast = "Self"
        lunch = "-"
        dinner = "-"
        task = "-"

        # FIRST SUNDAY
        if i == 0:
            breakfast = "N/A"
            lunch = "N/A"
            dinner = names[0] # Static start for dinner
        
        # WEEKDAYS
        elif 1 <= i <= 5:
            dinner_candidate = names[i % 3]
            if dinner_candidate == "J" and day_name in j_working_days:
                dinner = "L (J Working)"
            else:
                dinner = dinner_candidate

        # SATURDAY
        elif i == 6:
            lunch = names[i % 3]
            dinner = names[(i + 1) % 3]
            task = f"🧼 TOILET ({toilet_cleaner})"

        # FINAL SUNDAY
        elif i == 7:
            lunch = names[i % 3]
            dinner = "N/A (Departed)"
            # Monthly mop logic: check if it's the 4th week of the month
            if current_date.day > 21:
                task = f"🧹 VACUUM ({vacuum_cleaner}) & ✨ MOP ({mop_cleaner})"
            else:
                task = f"🧹 VACUUM ({vacuum_cleaner})"

        roster_list.append({
            "Date": date_str,
            "Day": day_name,
            "Breakfast": breakfast,
            "Lunch": lunch,
            "Dinner": dinner,
            "Weekly Task": task
        })
    
    return pd.DataFrame(roster_list)

# --- 3. DISPLAY & PRINT ---
df = generate_roster(selected_start, fortnight_count)

st.dataframe(
    df,
    column_config={
        "Weekly Task": st.column_config.TextColumn("Weekly Task (Assigned)", width="large"),
        "Date": st.column_config.TextColumn("Date", width="small"),
    },
    hide_index=True,
    use_container_width=True
)

# Create a CSV for downloading/printing
csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Download Roster for Printing",
    data=csv,
    file_name=f"chores_roster_{selected_start_str}.csv",
    mime="text/csv",
)

st.info("The cleaning tasks (Toilet/Vacuum/Mop) rotate through K, J, and L every fortnight.")
