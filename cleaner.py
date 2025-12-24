import pandas as pd
import re
from datetime import datetime

# --- CONFIGURATION ---
input_file = 'raw_swim_data.csv'
output_file = 'clean_swim_data.xlsx'
BIRTHDAY = "2010-11-17"
VALID_DISTANCES = [1650, 1500, 1000, 800, 500, 400, 200, 100, 50, 25]

def calculate_age(event_date_obj):
    if pd.isna(event_date_obj): return None
    born = datetime.strptime(BIRTHDAY, "%Y-%m-%d")
    return event_date_obj.year - born.year - ((event_date_obj.month, event_date_obj.day) < (born.month, born.day))

def is_valid_time_str(val):
    """Checks if a string looks like a swim time"""
    s = str(val).strip()
    return len(s) > 0 and any(char.isdigit() for char in s) and 'DQ' not in s.upper() and 'NS' not in s.upper()

def convert_time_to_seconds(time_str):
    if not is_valid_time_str(time_str): return None
    try:
        clean_str = str(time_str).upper().replace('Y', '').replace('L', '').replace('S', '').strip()
        if ':' in clean_str:
            parts = clean_str.split(':')
            if len(parts) == 2: return (float(parts[0]) * 60) + float(parts[1])
            elif len(parts) == 3: return (float(parts[0]) * 3600) + (float(parts[1]) * 60) + float(parts[2])
        return float(clean_str)
    except: return None

def get_distance(event_str):
    numbers = re.findall(r'\d+', str(event_str))
    for num in numbers:
        if int(num) in VALID_DISTANCES: return int(num)
    return None

def get_stroke(event_str):
    s = str(event_str).lower()
    if 'free' in s: return 'Free'
    if 'back' in s: return 'Back'
    if 'breast' in s: return 'Breast'
    if 'fly' in s or 'butterfly' in s: return 'Fly'
    if 'im' in s or 'individual' in s: return 'IM'
    return 'Other'

def clean_data():
    print("🚀 RUNNING VERSION 5.0 (PRELIM/FINAL SPLITTER)")
    print(f"🧹 Reading {input_file}...")
    
    try:
        df_raw = pd.read_csv(input_file, header=None)
    except FileNotFoundError:
        print("❌ Error: raw_swim_data.csv not found.")
        return

    # 1. Find Headers
    header_row_index = None
    for i in range(15):
        row_values = df_raw.iloc[i].astype(str).tolist()
        if any("Event" in x for x in row_values) and any("Date" in x for x in row_values):
            header_row_index = i
            break
    
    if header_row_index is None:
        print("❌ Error: Could not find headers.")
        return

    # 2. Load Data
    df = pd.read_csv(input_file, header=header_row_index)
    df.columns = df.columns.str.strip()

    # 3. Identify Key Columns
    date_col = next((c for c in df.columns if 'Date' in c), None)
    finals_col = next((c for c in df.columns if 'Finals' in c), None)
    prelim_col = next((c for c in df.columns if 'Prelim' in c), None)

    if not date_col:
        print("❌ Error: No Date column found.")
        return

    # 4. The Splitting Logic
    print("   -> Splitting Prelims and Finals into separate rows...")
    new_rows = []

    for _, row in df.iterrows():
        # Common data for this swim
        base_data = {
            'Date': row[date_col],
            'Event': row.get('Event', ''),
            'Meet': row.get('Meet', ''),
            'Age': calculate_age(pd.to_datetime(row[date_col], errors='coerce'))
        }
        
        # Check Finals
        if finals_col and is_valid_time_str(row[finals_col]):
            entry = base_data.copy()
            entry['Round'] = 'Finals'
            entry['Time_String'] = row[finals_col]
            new_rows.append(entry)

        # Check Prelims
        if prelim_col and is_valid_time_str(row[prelim_col]):
            entry = base_data.copy()
            entry['Round'] = 'Prelims'
            entry['Time_String'] = row[prelim_col]
            new_rows.append(entry)

    # Create new DataFrame from the split rows
    clean_df = pd.DataFrame(new_rows)

    # 5. Process the New Rows
    clean_df['Date'] = pd.to_datetime(clean_df['Date'])
    clean_df = clean_df.dropna(subset=['Date'])
    
    clean_df['Distance'] = clean_df['Event'].apply(get_distance)
    clean_df['Stroke'] = clean_df['Event'].apply(get_stroke)
    clean_df['Time_Seconds'] = clean_df['Time_String'].apply(convert_time_to_seconds)
    
    clean_df['Course'] = clean_df['Time_String'].astype(str).apply(
        lambda x: 'Yards' if 'Y' in x.upper() else ('LCM' if 'L' in x.upper() else 'SCM')
    )
    
    # Rename for compatibility with Grader
    clean_df['Finals'] = clean_df['Time_String']

    # 6. Save
    final_cols = ['Date', 'Age', 'Distance', 'Stroke', 'Round', 'Course', 'Finals', 'Time_Seconds', 'Meet']
    save_cols = [c for c in final_cols if c in clean_df.columns]
    
    clean_df[save_cols].sort_values(['Date', 'Round']).to_excel(output_file, index=False)
    print(f"✅ Success! Expanded {len(df)} raw rows into {len(clean_df)} individual swims.")
    print(f"   Saved to {output_file}")

if __name__ == "__main__":
    clean_data()