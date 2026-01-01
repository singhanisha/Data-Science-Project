import os
import json

# CHANGE THIS PATH to your actual cleaned_city_data folder
base = r"E:\Mini_Project\Map-react-app\my-map-app\public\data\cleaned_city_data"

state_city_map = {}

for state in os.listdir(base):
    state_path = os.path.join(base, state)

    if not os.path.isdir(state_path):
        continue

    # get all csv files of that state
    csv_files = [f for f in os.listdir(state_path) if f.lower().endswith(".csv")]

    state_city_map[state] = csv_files

# save JSON inside same folder
output_path = os.path.join(base, "states_city_list.json")

with open(output_path, "w") as f:
    json.dump(state_city_map, f, indent=4)

print("Saved:", output_path)
