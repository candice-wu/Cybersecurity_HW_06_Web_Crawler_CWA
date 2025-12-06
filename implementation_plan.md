# CWA Weather App Implementation Plan

This project aims to build a weather dashboard using data from the Central Weather Administration (CWA) Open Data API.
The system will consist of a data crawler, a SQLite database for storage, and a Streamlit web application for visualization.

## Goal Description
- **Objective**: Fetch 36-hour weather forecast data (Dataset ID: `F-A0010-001`), store it in a local database, and visualize it.
- **Data Source**: CWA Open Data API (https://opendata.cwa.gov.tw/dataset/forecast/F-A0010-001).
- **Tech Stack**: Python, SQLite, Streamlit.

## User Review Required
> [!IMPORTANT]
> **API Key Security**: The API Key `CWA-1FFDDAEC-161F-46A3-BE71-93C32C52829F` will be used in the code. In a production environment, this should be stored in an environment variable (`.env`) rather than hardcoded. For this homework/demo, we will proceed with `.env` file management to teach best practices.

## Proposed Changes

### Phase 1: Data Acquisition (Current Focus)
#### [NEW] [fetch_data.py](file:///Users/candicewu/Desktop/20241204%20%E7%A2%A9%E7%8F%AD/114%20%E5%AD%B8%E5%B9%B4%E5%BA%A6%E7%A2%A9%E5%B0%88%E7%8F%AD%E7%94%B3%E8%AE%80/10_%E4%BD%9C%E6%A5%AD%E5%A0%B1%E5%91%8A/7972%20%E4%BA%BA%E5%B7%A5%E6%99%BA%E6%85%A7%E8%88%87%E8%B3%87%E8%A8%8A%E5%AE%89%E5%85%A8_%E9%99%B3%E7%85%A5/Security/HW6/fetch_data.py)
- Script to request data from CWA API.
- Functions:
    - `get_weather_data(api_key)`: Returns JSON response.
    - `save_raw_data(data, filename)`: Saves raw JSON for inspection.

#### [NEW] [.env](file:///Users/candicewu/Desktop/20241204%20%E7%A2%A9%E7%8F%AD/114%20%E5%AD%B8%E5%B9%B4%E5%BA%A6%E7%A2%A9%E5%B0%88%E7%8F%AD%E7%94%B3%E8%AE%80/10_%E4%BD%9C%E6%A5%AD%E5%A0%B1%E5%91%8A/7972%20%E4%BA%BA%E5%B7%A5%E6%99%BA%E6%85%A7%E8%88%87%E8%B3%87%E8%A8%8A%E5%AE%89%E5%85%A8_%E9%99%B3%E7%85%A5/Security/HW6/.env)
- Store `CWA_API_KEY`.

### Phase 2: Database Storage
#### [NEW] [database.py](file:///Users/candicewu/Desktop/20241204%20%E7%A2%A9%E7%8F%AD/114%20%E5%AD%B8%E5%B9%B4%E5%BA%A6%E7%A2%A9%E5%B0%88%E7%8F%AD%E7%94%B3%E8%AE%80/10_%E4%BD%9C%E6%A5%AD%E5%A0%B1%E5%91%8A/7972%20%E4%BA%BA%E5%B7%A5%E6%99%BA%E6%85%A7%E8%88%87%E8%B3%87%E8%A8%8A%E5%AE%89%E5%85%A8_%E9%99%B3%E7%85%A5/Security/HW6/database.py)
- Defines SQLite schema.
- Functions to insert/update weather records.
- Schema: `forecasts` table (location, time, temp, pop, etc.).

### Phase 3: Streamlit Application
#### [NEW] [app.py](file:///Users/candicewu/Desktop/20241204%20%E7%A2%A9%E7%8F%AD/114%20%E5%AD%B8%E5%B9%B4%E5%BA%A6%E7%A2%A9%E5%B0%88%E7%8F%AD%E7%94%B3%E8%AE%80/10_%E4%BD%9C%E6%A5%AD%E5%A0%B1%E5%91%8A/7972%20%E4%BA%BA%E5%B7%A5%E6%99%BA%E6%85%A7%E8%88%87%E8%B3%87%E8%A8%8A%E5%AE%89%E5%85%A8_%E9%99%B3%E7%85%A5/Security/HW6/app.py)
- Main dashboard.
- Displays data from SQLite.
- Visualization: Tables and Charts.

## Verification Plan
### Automated Tests
- Run `python fetch_data.py` and verify `weather_raw.json` is created and contains valid JSON.
- Run `streamlit run app.py` to verify UI loads.

### Manual Verification
- Check if SQLite DB is populated.
- Verify UI shows correct data matching the JSON.
