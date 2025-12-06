# CWA Weather App Project (CRISP-DM)

This project implements a weather dashboard system using the CRISP-DM (Cross-Industry Standard Process for Data Mining) methodology.

## 1. Business Understanding
**Objective**: Build an automated system to fetch, store, and visualize 36-hour agricultural weather forecasts for Taiwan's major regions.
**Background**: Users need a centralized dashboard to view weekly weather trends to support agricultural decision-making.

## 2. Data Understanding
**Data Source**: Central Weather Administration (CWA) Open Data API.
**Dataset ID**: `F-A0010-001` (One-week Agricultural Weather Forecast).
**Data Format**: JSON.
**Key Attributes**:
- `locationName`: Region name (e.g., Northern, Central, Southern).
- `weatherElements`: Contains daily forecasts (`Wx`, `MaxT`, `MinT`).

## 3. Data Preparation
**Process**: Data Extraction and Transformation (ETL).
**Script**: `fetch_data.py`
- Fetches JSON data from CWA API.
- Parses nested JSON structure.
- **Automation**: `scheduler.py` runs this script every hour.

## 4. Modeling (System Architecture)
**Database**: SQLite (`data.db`)
**Schema Design** (`database.py`):
- **Table**: `weather`
    - `id`: Primary Key (Integer, Autoincrement)
    - `location`: Region name (Text)
    - `min_temp`: Minimum Temperature (Real)
    - `max_temp`: Maximum Temperature (Real)
    - `description`: Weather Description (Text)
    - `forecast_date`: Date (Text)

## 5. Evaluation
**Verification Steps**:
1.  **API Connectivity**: Validated successful connection to CWA API.
2.  **Data Integrity**: Data serves as the single source of truth in `data.db`.
3.  **Visualization**: Streamlit app correctly renders charts with custom colors.

## 6. Deployment
**Application**: Streamlit Web App (`app.py`).
**Features**:
- **Interactive Sidebar**: Region selection.
- **Temperature Trend Chart**: Line chart with custom colors (Max Temp: #DD6D6A, Min Temp: #4682B4).
- **Detailed Data Table**: Columns `ID`, `Date`, `Max Temp (°C)`, `Min Temp (°C)`, `Description`.

### How to Run
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure API Key**:
    Create a `.env` file:
    ```
    CWA_API_KEY=your_api_key_here
    ```
3.  **Manual Data Fetch**:
    ```bash
    python fetch_data.py
    ```
4.  **Automated Scheduler**:
    ```bash
    python scheduler.py
    ```
5.  **Launch App**:
    ```bash
    streamlit run app.py
    ```
