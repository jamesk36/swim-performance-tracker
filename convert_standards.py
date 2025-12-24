import json

# Read the comprehensive standards file
with open('standards_bad_format.json', 'r') as f:
    comprehensive = json.load(f)

# Create new structure that grader.py expects
converted = {}

# Map age group names
age_group_mapping = {
    '10_and_under': '10&U',
    '11-12': '11-12',
    '13-14': '13-14', 
    '15-16': '15-16',
    '17-18': '17-18'
}

# Map event names (the comprehensive file uses underscores, grader expects spaces)
def convert_event_name(event_key):
    """Convert event names like '50_free' to '50 Free'"""
    # Split by underscore
    parts = event_key.split('_')
    
    # Handle distance
    distance = parts[0]
    
    # Handle stroke - capitalize properly
    if len(parts) > 1:
        stroke = parts[1].capitalize()
        if stroke == 'Im':
            stroke = 'IM'
        elif stroke == 'Fly':
            stroke = 'Fly'
        return f"{distance} {stroke}"
    
    return event_key

# Convert the structure
for era, era_data in comprehensive['periods'].items():
    converted[era] = {}
    
    age_groups = era_data.get('age_groups', {})
    
    for old_ag_name, ag_data in age_groups.items():
        # Map to grader's expected age group name
        new_ag_name = age_group_mapping.get(old_ag_name, old_ag_name)
        converted[era][new_ag_name] = {}
        converted[era][new_ag_name]['Male'] = {}
        
        # Process each course type
        for course, events in ag_data.items():
            converted[era][new_ag_name]['Male'][course] = {}
            
            # Convert each event
            for event_key, standards in events.items():
                new_event_key = convert_event_name(event_key)
                converted[era][new_ag_name]['Male'][course][new_event_key] = standards

# Save the converted standards
with open('standards.json', 'w') as f:
    json.dump(converted, f, indent=2)

print("✅ Conversion Complete!")
print("\n📊 New standards.json structure:")
for era in converted:
    print(f"\n{era}:")
    for ag in converted[era]:
        courses = list(converted[era][ag]['Male'].keys())
        events_sample = {}
        for course in courses[:2]:  # Show first 2 courses
            event_count = len(converted[era][ag]['Male'][course])
            events_sample[course] = event_count
        print(f"  {ag}: {courses} - Events per course: {events_sample}")
