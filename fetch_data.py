import requests
import json
import os
from dotenv import load_dotenv
import database

# Load environment variables
load_dotenv()

def get_weather_data(api_key):
    """
    Fetches weather data from CWA API.
    Dataset ID: F-A0010-001 (36-Hour Weather Forecast)
    """
    # Tried datastore API, got 404. Switching to fileapi.
    # url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-A0010-001?Authorization={api_key}&format=JSON"
    url = f"https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization={api_key}&format=JSON"
    
    try:
        # verify=False is used here to bypass SSL errors commonly found in some environments
        # In production, you should fix the certificate issue instead.
        response = requests.get(url, verify=False)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def save_raw_data(data, filename="weather_raw.json"):
    """
    Saves raw JSON data to a file for inspection.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {filename}")
    except IOError as e:
        print(f"Error saving data: {e}")

def main():
    api_key = os.getenv("CWA_API_KEY")
    if not api_key:
        print("Error: CWA_API_KEY not found in environment variables.")
        return

    print("Fetching weather data from CWA API...")
    data = get_weather_data(api_key)

    if data:
        save_raw_data(data)
        
        # Verification for F-A0010-001 structure
        try:
            root = data.get("cwaopendata", {})
            resources = root.get("resources", {})
            resource = resources.get("resource", {})
            data_payload = resource.get("data", {})
            agr_forecasts = data_payload.get("agrWeatherForecasts", {})
            weather_forecasts = agr_forecasts.get("weatherForecasts", {})
            locations = weather_forecasts.get("location", [])

            if locations:
                print(f"Successfully retrieved data for {len(locations)} locations.")
                
                # Initialize Database
                database.init_db()
                
                forecast_list = []
                for loc in locations:
                    region = loc.get("locationName")
                    weather_elements = loc.get("weatherElements", {})
                    
                    # We need to zip Wx, MaxT, MinT
                    # Assuming checking 'Wx' daily list length is safe
                    wx_list = weather_elements.get("Wx", {}).get("daily", [])
                    max_t_list = weather_elements.get("MaxT", {}).get("daily", [])
                    min_t_list = weather_elements.get("MinT", {}).get("daily", [])
                    
                    for i, wx in enumerate(wx_list):
                        date = wx.get("dataDate")
                        weather_desc = wx.get("weather")
                        
                        # Safe get for others matching index
                        max_temp = max_t_list[i].get("temperature") if i < len(max_t_list) else None
                        min_temp = min_t_list[i].get("temperature") if i < len(min_t_list) else None
                        
                        forecast_list.append({
                            "region": region,
                            "date": date,
                            "weather": weather_desc,
                            "max_temp": int(max_temp) if max_temp else None,
                            "min_temp": int(min_temp) if min_temp else None
                        })
                
                if forecast_list:
                    print(f"Parsing complete. Saving {len(forecast_list)} records to database...")
                    database.save_forecasts(forecast_list)
                    print("Data storage complete.")
                else:
                    print("No forecast data parsed.")

            else:
                print("Warning: 'location' list is empty or not found in the expected path.")
        except Exception as e:
            print(f"Error verifying/saving data: {e}")

if __name__ == "__main__":
    main()
