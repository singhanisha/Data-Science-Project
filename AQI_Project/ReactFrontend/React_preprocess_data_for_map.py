import pandas as pd
import os
import json

# Configuration
INPUT_DIR = "D:/MCA MINI PROJECT/cleaned_data"
OUTPUT_FILE = "D:/MCA MINI PROJECT/ReactFrontend/map/src/data/city_aqi_data.json"


def classify_aqi(aqi):
    if pd.isna(aqi): return 'Unknown'
    elif aqi <= 50: return 'Good'
    elif aqi <= 100: return 'Satisfactory'
    elif aqi <= 200: return 'Moderate'
    elif aqi <= 300: return 'Poor'
    elif aqi <= 400: return 'Very Poor'
    else: return 'Severe'


def calculate_city_aqi_averages():
    all_data = {}
    error_files = []

    for state_folder in os.listdir(INPUT_DIR):
        state_path = os.path.join(INPUT_DIR, state_folder)
        if not os.path.isdir(state_path):
            continue

        print(f"📊 Processing {state_folder}...")
        state_data = {}

        for city_file in os.listdir(state_path):
            if not city_file.endswith('.csv'):
                continue

            city_name = city_file.replace('.csv', '').replace('_cleaned', '')
            file_path = os.path.join(state_path, city_file)

            try:
                df = pd.read_csv(file_path)

                required_columns = ['AQI', 'FESTIVAL_SEASON', 'SEASON']
                missing = [c for c in required_columns if c not in df.columns]
                if missing:
                    error_files.append(f"{city_file}: Missing {missing}")
                    continue

                # ---------------- FESTIVAL WISE AQI ----------------
                festival_aqi = {}
                for festival in df['FESTIVAL_SEASON'].dropna().unique():
                    data = df[df['FESTIVAL_SEASON'] == festival]['AQI'].dropna()
                    if not data.empty:
                        avg = data.mean()
                        festival_aqi[festival] = {
                            "avg_aqi": round(avg, 2),
                            "category": classify_aqi(avg),
                            "data_points": int(data.count())
                        }

                # ---------------- SEASON WISE AQI ----------------
                season_aqi = {}
                for season in df['SEASON'].dropna().unique():
                    data = df[df['SEASON'] == season]['AQI'].dropna()
                    if not data.empty:
                        avg = data.mean()
                        season_aqi[season] = {
                            "avg_aqi": round(avg, 2),
                            "category": classify_aqi(avg),
                            "data_points": int(data.count())
                        }

                # ---------------- COORDINATES ----------------
                lat, lng = None, None
                if 'LATITUDE' in df.columns and 'LONGITUDE' in df.columns:
                    coords = df[['LATITUDE', 'LONGITUDE']].dropna()
                    if not coords.empty:
                        lat = float(coords.iloc[0]['LATITUDE'])
                        lng = float(coords.iloc[0]['LONGITUDE'])

                if lat is None or lng is None:
                    error_files.append(f"{city_file}: No coordinates")
                    continue

                if festival_aqi or season_aqi:
                    state_data[city_name] = {
                        "latitude": lat,
                        "longitude": lng,
                        "festival_aqi": festival_aqi,
                        "season_aqi": season_aqi
                    }

            except Exception as e:
                error_files.append(f"{city_file}: {str(e)}")

        if state_data:
            all_data[state_folder] = state_data

    return all_data


def save_json_data(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n✅ JSON saved successfully")
    print(f"📍 States: {len(data)}")
    print(f"🏙 Cities: {sum(len(c) for c in data.values())}")


if __name__ == "__main__":
    print("🚀 Starting AQI preprocessing...")
    city_data = calculate_city_aqi_averages()
    save_json_data(city_data, OUTPUT_FILE)
    print("🎉 Done!")
