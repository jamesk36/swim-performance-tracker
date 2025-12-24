import pandas as pd

try:
    df = pd.read_csv('raw_swim_data.csv')
    print("✅ CSV Loaded Successfully.")
    print(f"📊 Total Rows: {len(df)}")
    print("\n--- EXACT COLUMN NAMES ---")
    for col in df.columns:
        print(f"[{col}]")  # Brackets help us see hidden spaces!
except Exception as e:
    print(f"❌ Error: {e}")