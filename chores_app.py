import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Household Chore Roster", layout="wide")

st.title("🏠 Fortnightly Household Roster")
st.write("J and L are home Sunday PM to Sunday PM every 2nd week.")

# --- 1. SETTINGS & DATES ---
anchor_date = datetime(2026, 1, 25)
today = datetime.now()

# Calculate fortnights for rotation
weeks_passed = (today - anchor_date).days // 7
current_fortnight_index = weeks_passed // 2

# Generate next 4 start dates
start_dates = []
for i in range(4):
    d = anchor_date + timedelta(weeks=(current_fortnight_index + i) * 2)
    start_dates.append(d.strftime("%d/%m/%Y"))

# Sidebar controls
st.sidebar.header("Settings")
selected_start_str = st.sidebar.selectbox("Select Roster Start Date:", start_dates)
selected_start = datetime.strptime(selected_start_str, "%d/%m/%Y")
fortnight_count = (selected_start - anchor_date).days // 14

st.sidebar.markdown("---")
j_working_days = st.sidebar.multiselect(
    "Days J is working late (Exempt from Dinner):",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
)

# --- 2. ROSTER LOGIC ---
def generate_roster(start_date, f_index):
    names = ["K", "J", "L"]
    roster_list = []
    
    # Rotation logic for cleaning tasks
    toilet_cleaner = names[f_index % 3]
    vacuum_cleaner = names[(f_index + 1) % 3]
    mop_cleaner = names[(f_index + 2) % 3]

    for i in range(8):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime("%A")
        date_str = current_date.strftime("%d/%m")
        
        # Defaults
        lunch = "-"
        dinner = "-"
        task_list = []

        # --- MEALS (DISHES) ---
        # 1st Sunday
        if i == 0:
            dinner = names[0] # K starts
            lunch = "N/A"
        # Weekdays
        elif 1 <= i <= 5:
            dinner_candidate = names[i % 3]
            if dinner_candidate == "J" and day_name in j_working_days:
                dinner = "L (J Working)"
            else:
                dinner = dinner_candidate
        # Saturday
        elif i == 6:
            lunch = names[i % 3]
            dinner = names[(i + 1) % 3]
        # Final Sunday
        elif i == 7:
            lunch = names[i % 3]
            dinner = "N/A (Departed)"

        # --- TASKS ---
        # 1. Room Cleaning (Wed & Sat)
        if day_name in ["Wednesday", "Saturday"]:
            task_list.append("🛏️ Clean/Vacuum Own Room (J & L)")

        # 2. Shared Cleaning (Sat & Sun)
        if day_name == "Saturday":
            task_list.append(f"🧼 CLEAN TOILET ({toilet_cleaner})")
        elif day_name == "Sunday" and i == 7: # Only the full Sunday
            if current_date.day > 21:
                 task_list.append(f"🧹 VACUUM ({vacuum_cleaner}) & ✨ MOP ({mop_cleaner})")
            else:
                 task_list.append(f"🧹 VACUUM ({vacuum_cleaner})")

        # Combine tasks into string
        full_task_str = " + ".join(task_list) if task_list else "-"

        roster_list.append({
            "Date": date_str,
            "Day": day_name,
            "Dishes: Lunch": lunch,
            "L_Done": False, # Checkbox column
            "Dishes: Dinner": dinner,
            "D_Done": False, # Checkbox column
            "Cleaning & Rooms": full_task_str,
            "C_Done": False  # Checkbox column
        })
    
    return pd.DataFrame(roster_list)

df = generate_roster(selected_start, fortnight_count)

# --- 3. DISPLAY WITH TICK BOXES ---
st.markdown("### 📋 Fortnightly Schedule")

# We use data_editor to make the checkboxes clickable
edited_df = st.data_editor(
    df,
    column_config={
        "Date": st.column_config.TextColumn("Date", width="small", disabled=True),
        "Day": st.column_config.TextColumn("Day", width="small", disabled=True),
        "Dishes: Lunch": st.column_config.TextColumn("Dishes: Lunch", width="small", disabled=True),
        "Dishes: Dinner": st.column_config.TextColumn("Dishes: Dinner", width="small", disabled=True),
        "Cleaning & Rooms": st.column_config.TextColumn("Cleaning & Rooms", width="large", disabled=True),
        
        # Configuration for the Checkboxes
        "L_Done": st.column_config.CheckboxColumn("Done?", width="small"),
        "D_Done": st.column_config.CheckboxColumn("Done?", width="small"),
        "C_Done": st.column_config.CheckboxColumn("Done?", width="small"),
    },
    hide_index=True,
    use_container_width=True
)

# --- 4. PENALTY NOTICE ---
st.error("""
**⚠️ PENALTY NOTICE:**
Unclean rooms will result in the immediate **loss of electronic equipment** (including Xbox and Switch), 
and any other penalty Dad chooses.
""")

# --- 5. PRINT BUTTON ---
# For printing, we replace False/True with empty brackets [ ] for the paper version
print_df = df.copy()
print_df["L_Done"] = "[ ]"
print_df["D_Done"] = "[ ]"
print_df["C_Done"] = "[ ]"

csv = print_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Printable Roster (CSV)",
    data=csv,
    file_name=f"chores_roster_{selected_start_str.replace('/','-')}.csv",
    mime="text/csv",
)
