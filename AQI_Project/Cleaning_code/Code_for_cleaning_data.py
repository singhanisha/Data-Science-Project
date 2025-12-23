import pandas as pd
import numpy as np
import os
import glob
import re
from city_coordinates import city_coordinates   # ✅ Import saved coordinates

# ---------- PATH SETTINGS ----------
input_path = "D:/MCA MINI PROJECT/citydata"          # folder containing raw city data
output_path = "D:/MCA MINI PROJECT/cleaned_data/"  # folder to save cleaned files
os.makedirs(output_path, exist_ok=True)

# ---------- POLLUTANT PATTERNS ----------
pollutant_patterns = {
    'PM2.5': r'PM2.?5',
    'PM10': r'PM.?10',
    'NO2': r'\bNO2\b',
    'NH3': r'NH3',
    'SO2': r'SO2',
    'CO': r'\bCO\b(?!2)',
    'O3': r'OZONE|O3'
}

# ---------- AQI BREAKPOINTS (CPCB, India) ----------
aqi_breakpoints = {
    'PM2.5': [(0,30,0,50),(31,60,51,100),(61,90,101,200),(91,120,201,300),(121,250,301,400),(250,800,401,500)],
    'PM10': [(0,50,0,50),(51,100,51,100),(101,250,101,200),(251,350,201,300),(351,430,301,400),(430,600,401,500)],
    'NO2':  [(0,40,0,50),(41,80,51,100),(81,180,101,200),(181,280,201,300),(281,400,301,400),(400,1000,401,500)],
    'SO2':  [(0,40,0,50),(41,80,51,100),(81,380,101,200),(381,800,201,300),(801,1600,301,400),(1600,3000,401,500)],
    'CO':   [(0,1,0,50),(1.1,2,51,100),(2.1,10,101,200),(10.1,17,201,300),(17.1,34,301,400),(34,50,401,500)],
    'O3':   [(0,50,0,50),(51,100,51,100),(101,168,101,200),(169,208,201,300),(209,748,301,400),(748,1000,401,500)]
}

# ---------- SEASON FUNCTION ----------
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Summer'
    elif month in [6, 7, 8, 9]:
        return 'Monsoon'
    else:
        return 'Post-Monsoon'

# ---------- FESTIVAL SEASON FUNCTION ----------
def get_festival_season(date):
    if pd.isna(date):
        return "Non-Festival Period"

    month = date.month

    # More descriptive festival periods
    if month in [10, 11]:
        return "Diwali Festival Season"           # Major pollution period
    elif month == 3:
        return "Holi Festival Season"             # Spring festival
    elif month in [8, 9]:
        return "Ganesh Chaturthi & Navratri"      # Major festivals
    elif month in [12, 1]:
        return "Christmas & New Year"             # Year-end celebrations
    elif month in [11, 12, 1, 2]:
        return "Winter Wedding"            # Peak wedding months
    elif month in [4, 5]:
        return "Summer Wedding"                 # Regional festivals
    else:
        return "Non-Festival Period"

# ---------- COLUMN CLEANING ----------
def clean_column_name(col):
    col = re.sub(r'\(.*?\)', '', col)          # remove text inside parentheses
    col = re.sub(r'[^A-Za-z0-9\. ]', '', col)  # remove non-English characters
    return col.strip().upper()

# ---------- AQI CALCULATION ----------
def calculate_subindex(pollutant, value):
    if pollutant not in aqi_breakpoints or pd.isna(value):
        return np.nan
    for (low, high, index_low, index_high) in aqi_breakpoints[pollutant]:
        if low <= value <= high:
            return ((index_high - index_low) / (high - low)) * (value - low) + index_low
    return np.nan

def calculate_aqi(row):
    subindices = []
    for pollutant in aqi_breakpoints.keys():
        if pollutant in row:
            sub = calculate_subindex(pollutant, row[pollutant])
            subindices.append(sub)
    return np.nanmax(subindices) if len(subindices) > 0 else np.nan

def classify_aqi(aqi):
    if pd.isna(aqi): return 'Unknown'
    elif aqi <= 50: return 'Good'
    elif aqi <= 100: return 'Satisfactory'
    elif aqi <= 200: return 'Moderate'
    elif aqi <= 300: return 'Poor'
    elif aqi <= 400: return 'Very Poor'
    else: return 'Severe'

# ---------- REMOVE EMPTY COLUMNS FUNCTION ----------
def remove_empty_columns(df):
    """Remove completely empty columns (all NaN values) from DataFrame"""
    # Find columns that are completely empty (all NaN)
    empty_cols = df.columns[df.isna().all()].tolist()
    
    if empty_cols:
        print(f"🗑️  Removing empty columns: {empty_cols}")
        df = df.drop(columns=empty_cols)
    
    return df

# ---------- MAIN CLEANING PROCESS ----------
all_files = glob.glob(input_path + "/**/*.csv", recursive=True)

for file in all_files:
    try:
        # read file
        try:
            df = pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file, encoding='latin1')

        # Step 1: Remove empty columns FIRST
        df = remove_empty_columns(df)

        # Step 2: Clean columns
        df.columns = [clean_column_name(c) for c in df.columns]

        # Step 3: Detect pollutant columns
        matched_cols = {}
        for std_name, pattern in pollutant_patterns.items():
            for col in df.columns:
                if re.search(pattern, col, re.IGNORECASE):
                    matched_cols[col] = std_name
                    break
        df.rename(columns=matched_cols, inplace=True)

        # Step 4: Keep main columns
        keep_cols = [c for c in ['TIMESTAMP', 'DATE', 'LOCATION'] if c in df.columns]
        keep_cols += list(pollutant_patterns.keys())
        df = df[[c for c in keep_cols if c in df.columns]]

        # Step 5: Fill missing values (but only for columns that exist and have some data)
        for col in pollutant_patterns.keys():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                if df[col].notna().any():
                    # Column has some valid data, fill with median
                    df[col] = df[col].fillna(df[col].median())
                else:
                    # Column exists but has no valid data - remove it instead of filling with 0
                    print(f"🗑️  Removing '{col}' column from {file} - no valid data")
                    df = df.drop(columns=[col])

        # Step 6: Add date-related features
        date_col = 'TIMESTAMP' if 'TIMESTAMP' in df.columns else 'DATE'
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df['MONTH'] = df[date_col].dt.month_name()
        df['SEASON'] = df[date_col].dt.month.apply(get_season)
        df['FESTIVAL_SEASON'] = df[date_col].apply(get_festival_season)

        # Step 7: Calculate AQI (only if we have pollutant columns left)
        pollutant_cols_present = [col for col in pollutant_patterns.keys() if col in df.columns]
        if pollutant_cols_present:
            df['AQI'] = df.apply(calculate_aqi, axis=1)
            df['AQI_CATEGORY'] = df['AQI'].apply(classify_aqi)
        else:
            df['AQI'] = np.nan
            df['AQI_CATEGORY'] = 'Unknown'
            print(f"⚠️ No pollutant columns available for AQI calculation in {file}")

        # Step 8: Add latitude & longitude
        city_name = os.path.splitext(os.path.basename(file))[0]  # extract city name
        city_info = city_coordinates.get(city_name)

        if city_info:
            df['CITY'] = city_name
            df['STATE'] = city_info['state']
            df['LATITUDE'] = city_info['latitude']
            df['LONGITUDE'] = city_info['longitude']
        else:
            df['CITY'] = city_name
            df['STATE'] = os.path.basename(os.path.dirname(file))
            df['LATITUDE'] = np.nan
            df['LONGITUDE'] = np.nan
            print(f"⚠️ Coordinates not found for {city_name}")

        # Step 9: Final check for empty columns (in case any were created during processing)
        df = remove_empty_columns(df)

        # Save file
        relative_path = os.path.relpath(file, input_path)
        output_file = os.path.join(output_path, relative_path)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        cleaned_file = output_file.replace(".csv", "_cleaned.csv")
        df.to_csv(cleaned_file, index=False)

        print(f"✅ Cleaned + AQI + Festival + Coordinates added: {cleaned_file}")

    except Exception as e:
        print(f"⚠️ Skipped {file} due to: {e}")

print("\n🎯 All cities processed successfully — Empty columns removed + AQI + Festival & Coordinates added!")
