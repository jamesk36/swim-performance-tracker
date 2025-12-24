import pandas as pd
import os
from io import StringIO

# --- CONFIGURATION ---
input_file = 'swim_history.html'
output_file = 'raw_swim_data.csv'

def parse_swim_html():
    print(f"📂 Reading {input_file}...")
    
    # 1. Check if file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: Could not find '{input_file}'.")
        print("   Make sure the file is in the 'swim_project' folder.")
        return

    # 2. Read the HTML file
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 3. Find Tables
    # We use 'flavor=bs4' because it's the most robust engine for messy HTML
    try:
        dfs = pd.read_html(StringIO(html_content), flavor='bs4')
    except ValueError:
        print("❌ Error: Python couldn't find any <table> tags in the file.")
        print("   The page might use 'divs' instead of tables. We may need a different approach.")
        return

    print(f"✅ Success! Found {len(dfs)} tables in the file.")

    # 4. Find the Right Table
    # A web page often has many tables (headers, footers). We want the one with the data.
    swim_df = None
    for index, df in enumerate(dfs):
        # We look for a table that has columns like "Event", "Time", or "Date"
        # We convert column names to string to avoid errors
        cols = str(df.columns).lower()
        if 'event' in cols or 'time' in cols or 'date' in cols:
            print(f"   -> Table {index} looks like the result data!")
            swim_df = df
            break
    
    if swim_df is None:
        print("⚠️ Found tables, but none looked like swim results. Saving the biggest one just in case...")
        # Fallback: Save the table with the most rows
        swim_df = max(dfs, key=len)

    # 5. Save to CSV
    swim_df.to_csv(output_file, index=False)
    print(f"\n💾 Saved raw data to: {output_file}")
    print("   Open this file in Excel to see if we got the right data!")

if __name__ == "__main__":
    parse_swim_html()