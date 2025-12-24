import pandas as pd
import os

print("🔍 DIAGNOSING HIGH_SCHOOL_SWIMS.CSV")
print("=" * 60)

if not os.path.exists('high_school_swims.csv'):
    print("❌ ERROR: high_school_swims.csv not found!")
    print("   Make sure the file is in the same folder as this script.")
else:
    print("✅ File found!")
    
    # Read the CSV
    df = pd.read_csv('high_school_swims.csv')
    
    print(f"\n📊 Total rows in file: {len(df)}")
    print(f"📊 Columns found: {list(df.columns)}")
    
    print("\n" + "=" * 60)
    print("ALL ROWS IN FILE:")
    print("=" * 60)
    
    for idx, row in df.iterrows():
        print(f"\nRow {idx + 1}:")
        print(f"  Date: {row.get('Date', 'MISSING')}")
        print(f"  Age: {row.get('Age', 'MISSING')}")
        print(f"  Distance: {row.get('Distance', 'MISSING')}")
        print(f"  Stroke: {row.get('Stroke', 'MISSING')}")
        print(f"  Round: {row.get('Round', 'MISSING')}")
        print(f"  Course: {row.get('Course', 'MISSING')}")
        print(f"  Finals: {row.get('Finals', 'MISSING')}")
        print(f"  Time_Seconds: {row.get('Time_Seconds', 'MISSING')}")
        print(f"  Meet: {row.get('Meet', 'MISSING')}")
        
        # Check for issues
        issues = []
        if pd.isna(row.get('Date')):
            issues.append("Missing Date")
        if pd.isna(row.get('Time_Seconds')):
            issues.append("Missing Time_Seconds")
        if pd.isna(row.get('Distance')):
            issues.append("Missing Distance")
        if pd.isna(row.get('Stroke')):
            issues.append("Missing Stroke")
        
        if issues:
            print(f"  ⚠️  ISSUES: {', '.join(issues)}")
        else:
            print(f"  ✅ Looks good!")
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    # Count valid vs invalid rows
    valid_rows = 0
    for idx, row in df.iterrows():
        if not pd.isna(row.get('Date')) and not pd.isna(row.get('Time_Seconds')):
            valid_rows += 1
    
    print(f"Valid rows: {valid_rows}")
    print(f"Invalid/incomplete rows: {len(df) - valid_rows}")
    
    if valid_rows != len(df):
        print("\n💡 TIP: Check the rows marked with ⚠️ above")
        print("   Make sure all required fields have values:")
        print("   - Date (YYYY-MM-DD)")
        print("   - Age (number)")
        print("   - Distance (number)")
        print("   - Stroke (Free, Back, Breast, Fly, or IM)")
        print("   - Course (Yards or LCM)")
        print("   - Finals (time with Y or L)")
        print("   - Time_Seconds (just the number)")
