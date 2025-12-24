import pandas as pd
import os

# Configuration
gomotion_file = 'clean_swim_data.xlsx'
high_school_file = 'high_school_swims.csv'
output_file = 'clean_swim_data.xlsx'

def merge_swim_data():
    print("🏊 MERGING SWIM DATA")
    print("=" * 60)
    
    # 1. Load GoMotion data
    if os.path.exists(gomotion_file):
        gomotion_df = pd.read_excel(gomotion_file)
        print(f"✅ Loaded {len(gomotion_df)} GoMotion swims")
    else:
        print(f"⚠️  No GoMotion data found ({gomotion_file})")
        gomotion_df = pd.DataFrame()
    
    # 2. Load high school data (if exists)
    if os.path.exists(high_school_file):
        hs_df = pd.read_csv(high_school_file)
        print(f"\n📋 Found {len(hs_df)} rows in {high_school_file}")
        
        # Show what we're reading
        print("\n🔍 High School Swim Details:")
        for idx, row in hs_df.iterrows():
            # Check if row has required data
            has_date = not pd.isna(row.get('Date'))
            has_time = not pd.isna(row.get('Time_Seconds'))
            has_distance = not pd.isna(row.get('Distance'))
            has_stroke = not pd.isna(row.get('Stroke'))
            
            if has_date and has_time and has_distance and has_stroke:
                print(f"  ✅ Row {idx+1}: {row.get('Distance')} {row.get('Stroke')} - {row.get('Finals')} ({row.get('Meet', 'No meet name')})")
            else:
                missing = []
                if not has_date: missing.append("Date")
                if not has_time: missing.append("Time_Seconds")
                if not has_distance: missing.append("Distance")
                if not has_stroke: missing.append("Stroke")
                print(f"  ❌ Row {idx+1}: SKIPPED - Missing: {', '.join(missing)}")
        
        # Convert date to datetime
        hs_df['Date'] = pd.to_datetime(hs_df['Date'], errors='coerce')
        
        # Drop rows with missing critical data
        initial_count = len(hs_df)
        hs_df = hs_df.dropna(subset=['Date', 'Time_Seconds', 'Distance', 'Stroke'])
        final_count = len(hs_df)
        
        if initial_count > final_count:
            print(f"\n⚠️  Dropped {initial_count - final_count} incomplete rows")
        
        print(f"\n✅ Loaded {len(hs_df)} valid high school swims")
    else:
        print(f"ℹ️  No high school data found ({high_school_file}) - creating template")
        hs_df = pd.DataFrame(columns=['Date', 'Age', 'Distance', 'Stroke', 'Round', 'Course', 'Finals', 'Time_Seconds', 'Meet'])
        hs_df.to_csv(high_school_file, index=False)
        print(f"   Created empty template: {high_school_file}")
    
    # 3. Combine the data
    if len(gomotion_df) > 0 and len(hs_df) > 0:
        combined_df = pd.concat([gomotion_df, hs_df], ignore_index=True)
    elif len(gomotion_df) > 0:
        combined_df = gomotion_df
    elif len(hs_df) > 0:
        combined_df = hs_df
    else:
        print("❌ No data to merge!")
        return
    
    # 4. Sort by date
    combined_df = combined_df.sort_values('Date').reset_index(drop=True)
    
    # 5. Save combined data
    combined_df.to_excel(output_file, index=False)
    
    print("\n" + "=" * 60)
    print(f"✅ SUCCESS! Combined data saved to: {output_file}")
    print(f"   Total swims: {len(combined_df)}")
    print(f"   - GoMotion: {len(gomotion_df)}")
    print(f"   - High School: {len(hs_df)}")
    print("\n💡 Next step: Run 'python grader.py' to grade all swims")
    print("=" * 60)

if __name__ == "__main__":
    merge_swim_data()
