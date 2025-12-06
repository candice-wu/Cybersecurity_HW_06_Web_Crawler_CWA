import requests
import json
import os
from dotenv import load_dotenv
import database
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

def get_weather_data(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Fetches weather data from CWA API.
    Dataset ID: F-A0010-001 (36-Hour Weather Forecast)
    """
    # Using fileapi as per previous success
    url = f"https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization={api_key}&format=JSON"
    
    try:
        # verify=False is used here to bypass SSL errors (development only)
        response = requests.get(url, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def save_raw_data(data: Dict[str, Any], filename: str = "weather_raw.json") -> None:
    """
    Saves raw JSON data to a file for debugging/inspection.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Raw data successfully saved to {filename}")
    except IOError as e:
        print(f"Error saving raw data: {e}")

def parse_weather_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parses the CWA JSON structure to extract relevant forecast info.
    """
    forecast_list = []
    try:
        root = data.get("cwaopendata", {})
        resources = root.get("resources", {})
        resource = resources.get("resource", {})
        data_payload = resource.get("data", {})
        agr_forecasts = data_payload.get("agrWeatherForecasts", {})
        weather_forecasts = agr_forecasts.get("weatherForecasts", {})
        locations = weather_forecasts.get("location", [])

        if not locations:
            print("Warning: 'location' list is empty or not found in the expected path.")
            return []

        print(f"Found data for {len(locations)} locations.")

        for loc in locations:
            region = loc.get("locationName")
            weather_elements = loc.get("weatherElements", {})
            
            # Extract daily forecast lists
            wx_list = weather_elements.get("Wx", {}).get("daily", [])
            max_t_list = weather_elements.get("MaxT", {}).get("daily", [])
            min_t_list = weather_elements.get("MinT", {}).get("daily", [])
            
            # Iterate through available forecasts (usually 7 days)
            for i, wx in enumerate(wx_list):
                date = wx.get("dataDate")
                weather_desc = wx.get("weather")
                
                # Check bounds for other lists
                max_temp = max_t_list[i].get("temperature") if i < len(max_t_list) else None
                min_temp = min_t_list[i].get("temperature") if i < len(min_t_list) else None
                
                # We need all essential fields
                if date and region:
                    forecast_list.append({
                        "region": region,
                        "date": date,
                        "weather": weather_desc,
                        "max_temp": int(max_temp) if max_temp is not None else None,
                        "min_temp": int(min_temp) if min_temp is not None else None
                    })
                    
    except Exception as e:
        print(f"Error parsing weather data: {e}")
        return []

    return forecast_list

def main():
    api_key = os.getenv("CWA_API_KEY")
    if not api_key:
        print("Error: CWA_API_KEY not found in environment variables.")
        return

    print("Fetching weather data from CWA API...")
    data = get_weather_data(api_key)

    if data:
        save_raw_data(data)
        
        # Initialize Database
        database.init_db()
        
        # Parse Data
        print("Parsing weather data...")
        forecasts = parse_weather_data(data)
        
        if forecasts:
            print(f"Parsing complete. Saving {len(forecasts)} records to database...")
            database.save_forecasts(forecasts)
            print("Data storage complete.")
        else:
            print("No forecast data parsed.")
    else:
        print("Failed to retrieve data.")

if __name__ == "__main__":
    main()
