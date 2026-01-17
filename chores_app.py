import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Household Chore Roster", layout="wide")

st.title("🏠 Smart Household Roster (With Swaps)")
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

# --- SIDEBAR: EXEMPTIONS ---
st.sidebar.header("Roster Settings")
selected_start_str = st.sidebar.selectbox("Select Roster Start Date:", start_dates)
selected_start = datetime.strptime(selected_start_str, "%d/%m/%Y")
fortnight_count = (selected_start - anchor_date).days // 14

st.sidebar.markdown("---")
st.sidebar.header("🚫 Availability / Exemptions")
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# J Exemptions
j_work = st.sidebar.multiselect("Days J Works (Late):", days_of_week)
j_footy = st.sidebar.multiselect("Days J has Footy Training:", days_of_week)
# L Exemptions
l_footy = st.sidebar.multiselect("Days L has Footy Training:", days_of_week)

# Combine exemptions for easier logic
j_busy_days = set(j_work + j_footy)
l_busy_days = set(l_footy)

# --- 2. SMART SWAP LOGIC ---
def get_busy_status(person, day_name):
    """Check if a specific person is busy on a specific day."""
    if person == "J" and day_name in j_busy_days:
        return True
    if person == "L" and day_name in l_busy_days:
        return True
    return False

def generate_roster_with_swaps(start_date, f_index):
    names = ["K", "J", "L"]
    
    # 1. Define all meal slots for the 8 days
    # We flatten the schedule first to handle swaps easily
    meal_slots = []
    
    for i in range(8):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime("%A")
        
        # Determine valid meals for this day
        meals_today = []
        
        # Lunch Rules: Only Saturday and Sunday (Week 2)
        if i == 6 or i == 7: 
            meals_today.append({"type": "Lunch", "day": day_name, "date_idx": i})
        
        # Dinner Rules: Every night except final Sunday (Departure)
        if i < 7:
            meals_today.append({"type": "Dinner", "day": day_name, "date_idx": i})
            
        for meal in meals_today:
            meal_slots.append(meal)

    # 2. Initial Assignment (Fair Rotation)
    # We assign purely on rotation first (0, 1, 2...) ignoring exemptions
    for idx, slot in enumerate(meal_slots):
        # We start the rotation offset based on the day index to mix it up
        assignee = names[(idx + f_index) % 3] 
        slot['assigned'] = assignee
        slot['note'] = ""

    # 3. Swap Logic (The "Smart" Part)
    # Check for conflicts and swap with future slots
    for i in range(len(meal_slots)):
        current_slot = meal_slots[i]
        current_person = current_slot['assigned']
        current_day = current_slot['day']
        
        # If the assigned person is busy/exempt
        if get_busy_status(current_person, current_day):
            
            swap_found = False
            
            # Look ahead for a swap candidate
            for j in range(i + 1, len(meal_slots)):
                target_slot = meal_slots[j]
                target_person = target_slot['assigned']
                target_day = target_slot['day']
                
                # Logic: 
                # 1. Target person must be free NOW (at index i)
                # 2. Current person must be free LATER (at index j)
                if (not get_busy_status(target_person, current_day) and 
                    not get_busy_status(current_person, target_day)):
                    
                    # PERFORM SWAP
                    meal_slots[i]['assigned'] = target_person
                    meal_slots[i]['note'] = f"(Covering {current_person})"
                    
                    meal_slots[j]['assigned'] = current_person
                    meal_slots[j]['note'] = f"(Swapped from {current_day})"
                    
                    swap_found = True
                    break
            
            # If no swap found (e.g., end of week), assign to K (Fallback)
            if not swap_found:
                 # Default fallback is usually K if J/L are busy and can't swap
                 if current_person != "K":
                     meal_slots[i]['assigned'] = "K"
                     meal_slots[i]['note'] = f"(Covering {current_person})"

    # 4. Cleaning Tasks (Fixed Rotation)
    toilet_cleaner = names[f_index % 3]
    vacuum_cleaner = names[(f_index + 1) % 3]
    mop_cleaner = names[(f_index + 2) % 3]

    # 5. Build Final Table
    roster_rows = []
    
    # We iterate 0-7 days again and pull data from our swapped meal_slots
    for i in range(8):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime("%A")
        date_str = current_date.strftime("%d/%m")
        
        # Retrieve meals for this day from our processed list
        lunch_str = "-"
        dinner_str = "-"
        
        # Filter slots for this specific day index
        days_slots = [s for s in meal_slots if s['date_idx'] == i]
        
        for slot in days_slots:
            val = f"{slot['assigned']} {slot['note']}"
            if slot['type'] == "Lunch":
                lunch_str = val
            elif slot['type'] == "Dinner":
                dinner_str = val
        
        # Formatting N/A for visual clarity
        if i == 0: 
            lunch_str = "N/A" # 1st Sunday start
        if i == 7: 
            dinner_str = "N/A (Departed)"

        # Tasks Logic
        task_list = []
        
        # Room Checks
        if day_name in ["Wednesday", "Saturday"]:
            task_list.append("🛏️ Room Check (J & L)")

        # Shared Cleaning
        if day_name == "Saturday":
            task_list.append(f"🧼 CLEAN TOILET ({toilet_cleaner})")
        elif day_name == "Sunday" and i == 7:
            if current_date.day > 21:
                 task_list.append(f"🧹 VACUUM ({vacuum_cleaner}) & ✨ MOP ({mop_cleaner})")
            else:
                 task_list.append(f"🧹 VACUUM ({vacuum_cleaner})")

        full_task_str = " + ".join(task_list) if task_list else "-"

        roster_rows.append({
            "Date": date_str,
            "Day": day_name,
            "Dishes: Lunch": lunch_str,
            "L_Done": False,
            "Dishes: Dinner": dinner_str,
            "D_Done": False,
            "Cleaning & Rooms": full_task_str,
            "C_Done": False
        })
        
    return pd.DataFrame(roster_rows)

df = generate_roster_with_swaps(selected_start, fortnight_count)

# --- 3. DISPLAY ---
st.markdown("### 📋 Fortnightly Schedule")

edited_df = st.data_editor(
    df,
    column_config={
        "Date": st.column_config.TextColumn("Date", width="small", disabled=True),
        "Day": st.column_config.TextColumn("Day", width="small", disabled=True),
        "Dishes: Lunch": st.column_config.TextColumn("Dishes: Lunch", width="small", disabled=True),
        "Dishes: Dinner": st.column_config.TextColumn("Dishes: Dinner", width="medium", disabled=True),
        "Cleaning & Rooms": st.column_config.TextColumn("Cleaning & Rooms", width="large", disabled=True),
        "L_Done": st.column_config.CheckboxColumn("Done?", width="small"),
        "D_Done": st.column_config.CheckboxColumn("Done?", width="small"),
        "C_Done": st.column_config.CheckboxColumn("Done?", width="small"),
    },
    hide_index=True,
    use_container_width=True
)

# --- 4. FOOTNOTES & PENALTIES ---
st.info("ℹ️ **Auto-Swap Active:** If J or L are exempt (Work/Footy), the roster automatically swaps their shift with a future meal.")

st.error("""
**⚠️ PENALTY NOTICE:**
Unclean rooms (Wed & Sat) will result in the immediate **loss of electronic equipment** (including Xbox and Switch), 
and any other penalty Dad chooses.
""")

# --- 5. PRINT BUTTON ---
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
