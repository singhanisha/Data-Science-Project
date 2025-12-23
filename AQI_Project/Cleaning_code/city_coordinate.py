import os
import pandas as pd
from geopy.geocoders import Nominatim
import time

input_path = "E:/Mini_Project/citydata"
output_path = "E:/Mini_Project/city_coordinates.py"

geolocator = Nominatim(user_agent="city_locator")

city_coords = {}

# Loop through each state folder
for state in os.listdir(input_path):
    state_folder = os.path.join(input_path, state)
    if not os.path.isdir(state_folder):
        continue  # skip non-folders
    
    for file in os.listdir(state_folder):
        if file.endswith(".csv"):
            city_name = os.path.splitext(file)[0]  # remove .csv extension
            try:
                location = geolocator.geocode(f"{city_name}, {state}, India", timeout=10)
                if location:
                    city_coords[city_name] = {
                        "state": state,
                        "latitude": location.latitude,
                        "longitude": location.longitude
                    }
                    print(f"✅ {city_name}, {state}: ({location.latitude}, {location.longitude})")
                else:
                    print(f"⚠️ Could not find coordinates for {city_name}, {state}")
            except Exception as e:
                print(f"⚠️ Error fetching {city_name}, {state}: {e}")
            time.sleep(1)  # prevent rate limit issues

# Save coordinates to Python file
with open(output_path, "w", encoding="utf-8") as f:
    f.write("city_coordinates = ")
    f.write(repr(city_coords))

print(f"\n🎯 Saved {len(city_coords)} city coordinates to {output_path}")
