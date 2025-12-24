import pandas as pd
import json

# --- CONFIGURATION ---
input_file = 'clean_swim_data.xlsx'
output_file = 'graded_swim_data.xlsx'
standards_file = 'standards.json'

def parse_time_standard(time_val):
    """Converts standard string (e.g. '1:56.29') to seconds"""
    if isinstance(time_val, (int, float)): return time_val
    try:
        if ':' in str(time_val):
            parts = str(time_val).split(':')
            return (float(parts[0]) * 60) + float(parts[1])
        return float(time_val)
    except:
        return 99999.0 # Return a huge time if parsing fails

def get_standard_rating(row, standards_data):
    # 0. Safety Check
    swim_time = row['Time_Seconds']
    if pd.isna(swim_time) or swim_time == 0: return "No Time"

    # 1. Determine Era
    swim_date = row['Date']
    if swim_date < pd.Timestamp("2024-09-01"):
        era = "2021-2024"
    else:
        era = "2024-2028"

    # 2. Determine Age Group
    age = row['Age']
    if age <= 10: age_group = "10&U"
    elif 11 <= age <= 12: age_group = "11-12"
    elif 13 <= age <= 14: age_group = "13-14"
    elif 15 <= age <= 16: age_group = "15-16"
    elif 17 <= age <= 18: age_group = "17-18"
    else: return "Old" 
    
    # 3. Attributes
    gender = "Male"
    # IMPORTANT: Maps 'Yards' -> 'SCY' and 'LCM' -> 'LCM'
    course = "SCY" if row['Course'] == 'Yards' else "LCM"
    
    # 4. Match Event Key
    # In Yards, we say "500 Free". In Meters, that same distance is "400 Free".
    # This logic maps the long distance events correctly.
    dist = int(row['Distance'])
    stroke = row['Stroke']
    
    if course == "LCM":
        # Map Yards Distances to Meter Equivalents if needed
        if dist == 500: dist = 400
        if dist == 1000: dist = 800
        if dist == 1650: dist = 1500
        
    event_key = f"{dist} {stroke}"
    
    # 5. Lookup Logic
    try:
        if era not in standards_data: return f"Unrated ({era})"
        event_standards = standards_data[era][age_group][gender][course][event_key]
    except KeyError:
        return "Unrated" 

    # 6. Compare Time
    for std in ['AAAA', 'AAA', 'AA', 'A', 'BB', 'B']:
        std_string = event_standards.get(std)
        if std_string:
            std_time = parse_time_standard(std_string)
            if swim_time <= std_time:
                return std

    return "<B"

def run_grader():
    print("🎓 Loading data and standards...")
    df = pd.read_excel(input_file)
    
    with open(standards_file, 'r') as f:
        standards_data = json.load(f)

    print(f"   -> Grading {len(df)} swims...")
    df['Standard'] = df.apply(lambda row: get_standard_rating(row, standards_data), axis=1)

    df.to_excel(output_file, index=False)
    print(f"✅ Success! Graded data saved to {output_file}")
    print("   Open it to see if he has any 'AAAA' or 'AA' tags!")

if __name__ == "__main__":
    run_grader()