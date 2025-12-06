import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
import pydeck as pdk
import os
import fetch_data
import datetime

DB_NAME = "data.db"

# Mapping mapping Taiwan cities to their broader regions and coordinates
# This allows us to display specific city points even though data is regional
CITY_MAPPING = {
    "Taipei City": {"region": "北部地區", "lat": 25.0320, "lon": 121.5654},
    "New Taipei City": {"region": "北部地區", "lat": 25.0120, "lon": 121.4654},
    "Keelung City": {"region": "北部地區", "lat": 25.1276, "lon": 121.7392},
    "Taoyuan City": {"region": "北部地區", "lat": 24.9936, "lon": 121.3010},
    "Hsinchu City": {"region": "北部地區", "lat": 24.8138, "lon": 120.9675},
    "Miaoli County": {"region": "北部地區", "lat": 24.5602, "lon": 120.8214},
    
    "Taichung City": {"region": "中部地區", "lat": 24.1477, "lon": 120.6736},
    "Changhua County": {"region": "中部地區", "lat": 24.0518, "lon": 120.5161},
    "Nantou County": {"region": "中部地區", "lat": 23.9610, "lon": 120.9719},
    "Yunlin County": {"region": "中部地區", "lat": 23.7092, "lon": 120.4313},
    "Chiayi City": {"region": "中部地區", "lat": 23.4801, "lon": 120.4491},
    
    "Tainan City": {"region": "南部地區", "lat": 22.9997, "lon": 120.2270},
    "Kaohsiung City": {"region": "南部地區", "lat": 22.6273, "lon": 120.3014},
    "Pingtung County": {"region": "南部地區", "lat": 22.5519, "lon": 120.5487},
    
    "Yilan County": {"region": "東北部地區", "lat": 24.7021, "lon": 121.7377},
    
    "Hualien County": {"region": "東部地區", "lat": 23.9872, "lon": 121.6016},
    
    "Taitung County": {"region": "東南部地區", "lat": 22.7613, "lon": 121.1438},
}

def get_db_connection():
    return sqlite3.connect(DB_NAME)

def get_locations():
    try:
        with get_db_connection() as conn:
            df = pd.read_sql("SELECT DISTINCT location FROM weather", conn)
            return df['location'].tolist()
    except Exception:
        return []

def get_forecast_by_location(location):
    try:
        with get_db_connection() as conn:
            query = """
                SELECT id, forecast_date, description, max_temp, min_temp
                FROM weather
                WHERE location = ?
                ORDER BY forecast_date ASC
            """
            df = pd.read_sql(query, conn, params=(location,))
            return df
    except Exception:
        return pd.DataFrame()

def get_all_forecasts_by_date(target_date):
    """Fetches weather for all regions for a specific date."""
    try:
        with get_db_connection() as conn:
            # Join not needed as we map in python, just get all regional data
            query = "SELECT location, max_temp, min_temp, description FROM weather WHERE forecast_date = ?"
            df = pd.read_sql(query, conn, params=(target_date,))
            return df
    except Exception:
        return pd.DataFrame()

def apply_custom_css():
    st.markdown("""
        <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
        .stMetric {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid #f0f0f0;
        }
        div[data-testid="stExpander"] div[role="button"] p {
            font-size: 1.1rem;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Taiwan Agriculture Weather", page_icon="🌾", layout="wide")
    apply_custom_css()

    st.title("🌾 Agricultural Weather Map")
    
    # 1. Sidebar Configuration
    st.sidebar.header("⚙️ Settings")
    
    # 1. Sidebar Configuration
    st.sidebar.header("⚙️ Settings")
    
    # Auto-update Logic
    def should_update_data():
        """Checks if data needs to be fetched (missing, empty, or stale)."""
        if not os.path.exists(DB_NAME):
            return True
            
        # Check if empty
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM weather")
            count = cursor.fetchone()[0]
            if count == 0:
                return True
        except:
            return True
        finally:
            conn.close()

        # Check freshness (e.g., update if older than 4 hours)
        last_mod_time = os.path.getmtime(DB_NAME)
        if (datetime.datetime.now().timestamp() - last_mod_time) > 14400:  # 4 hours
            return True
            
        return False

    def update_data():
        """Fetches new data using API key from Secrets or Env."""
        with st.spinner("🔄 Updating weather data from CWA..."):
            try:
                # Ensure API Key is set in environment for fetch_data script
                if "CWA_API_KEY" not in os.environ:
                    # Try to get from st.secrets safely
                    try:
                        os.environ["CWA_API_KEY"] = st.secrets["CWA_API_KEY"]
                    except (FileNotFoundError, KeyError):
                        # If running locally without secrets.toml and not in env, this might fail
                        pass
                
                # Check again if key exists
                if not os.getenv("CWA_API_KEY"):
                    st.error("❌ API Key missing! Please set CWA_API_KEY in secrets or environment.")
                    st.stop()

                # Run fetch (ensure DB is init inside fetch_data or here)
                # fetch_data.main() calls init_db itself
                fetch_data.main()
                st.success("✅ Weather data updated successfully!")
                
                # Rerun logic to ensure clean state
                # st.rerun() # Optional: might cause loop if file time handling is tricky
                
            except Exception as e:
                st.error(f"Failed to update data: {e}")

    # Check and Run Update
    if should_update_data():
        if st.sidebar.button("Force Update Now"): # Manual override option
             update_data()
        else:
             update_data() # Auto run

    # Also allow manual refresh anytime
    if st.sidebar.button("🔄 Refresh Data"):
        update_data()

    # Get locations AFTER potential update
    available_regions = get_locations()
    if not available_regions:
        st.error("No weather data available. Please check your API Key and Network Connection.")
        st.stop()

    # Get available dates for the slider/radio
    # We'll just grab dates from one region to populate options
    dates = []
    if available_regions:
        details = get_forecast_by_location(available_regions[0])
        if not details.empty:
            dates = details['forecast_date'].tolist()

    if not dates:
        st.warning("No forecast dates available.")
        st.stop()

    # Time Period Selection (simulate "Today, Yesterday" but with Forecast dates)
    st.sidebar.subheader("📅 Select Forecast Date")
    selected_date = st.sidebar.radio(
        "Choose a date:",
        dates,
        format_func=lambda x: f"{x} (Forecast)"
    )

    # 2. Main Layout
    
    # ROW 1: Map (Left) + Single Day Details (Right)
    row1_left, row1_right = st.columns([1.5, 1])

    with row1_left:
        st.subheader(f"🗺️ Temperature Map: {selected_date}")
        
        # Prepare Map Data
        regional_weather = get_all_forecasts_by_date(selected_date)
        
        map_data = []
        for city, info in CITY_MAPPING.items():
            region = info['region']
            # Find weather for this region
            idx = regional_weather.index[regional_weather['location'] == region].tolist()
            if idx:
                row = regional_weather.iloc[idx[0]]
                max_t = row['max_temp']
                
                # Color calculation
                normalized_t = max(0, min(1, (max_t - 10) / 25))
                r = int(255 * normalized_t)
                b = int(255 * (1 - normalized_t))
                color = [r, 50, b, 200]
                
                map_data.append({
                    "city": city,
                    "lat": info['lat'],
                    "lon": info['lon'],
                    "temp": f"{int(row['min_temp'])}-{int(row['max_temp'])}°C",
                    "max_temp": int(row['max_temp']),
                    "desc": row['description'],
                    "color": color,
                    "radius": 15000
                })
        
        df_map = pd.DataFrame(map_data)

        if not df_map.empty:
            layer = pdk.Layer(
                "ScatterplotLayer",
                df_map,
                get_position="[lon, lat]",
                get_color="color",
                pickable=True,
                opacity=0.8,
                stroked=True,
                filled=True,
                radius_scale=1,
                radius_min_pixels=5,
                radius_max_pixels=25,
            )
            
            tooltip = {
                "html": "<b>{city}</b><br/>Temp: {temp}<br/>Weather: {desc}",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }

            view_state = pdk.ViewState(
                latitude=23.7,
                longitude=121.0,
                zoom=6.8,
                pitch=0,
            )

            r = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip,
                map_style="mapbox://styles/mapbox/light-v9",
                height=400
            )
            st.pydeck_chart(r)
        else:
            st.info("No map data available for this date.")

    with row1_right:
        st.subheader("📍 Daily Status")
        
        # Region Selector (Controls Details & Trend)
        selected_region_detail = st.selectbox("Select Region:", available_regions, index=0)
        
        if selected_region_detail:
            st.markdown(f"#### {selected_region_detail} on {selected_date}")
            
            match_date = pd.to_datetime(selected_date)
            df_trend = get_forecast_by_location(selected_region_detail)
            df_trend['forecast_date'] = pd.to_datetime(df_trend['forecast_date'])
            
            day_data = df_trend[df_trend['forecast_date'] == match_date]
            
            if not day_data.empty:
                d = day_data.iloc[0]
                formatted_date = d['forecast_date'].strftime('%Y-%m-%d')
                
                st.metric("Date", formatted_date)
                st.metric("Weather", d['description'])
                st.metric("Temp Range", f"{int(d['min_temp'])}-{int(d['max_temp'])}°C")
            else:
                st.warning("No data for selected date.")
    
    st.divider()

    # ROW 2: Trend Chart (Left) + Data Table (Right)
    row2_left, row2_right = st.columns([2, 1])

    with row2_left:
        st.subheader("📈 Temperature Trend (7 Days)")
        if selected_region_detail:
             # Altair Chart
            base = alt.Chart(df_trend).encode(
                x=alt.X('forecast_date', axis=alt.Axis(format='%m-%d'), title='Date'),
                tooltip=['forecast_date', 'max_temp', 'min_temp', 'description']
            )
            line_max = base.mark_line(color='#ff7f50').encode(y='max_temp')
            line_min = base.mark_line(color='#4682b4').encode(y='min_temp')
            
            st.altair_chart((line_max + line_min).interactive(), use_container_width=True)

    with row2_right:
        st.subheader("📋 Forecast Data")
        if selected_region_detail:
            display_df = df_trend.copy()
            display_df['forecast_date'] = display_df['forecast_date'].dt.strftime('%Y-%m-%d')
            display_df = display_df[['forecast_date', 'max_temp', 'min_temp', 'description']]
            display_df.columns = ['Date', 'Max', 'Min', 'Weather']
            
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=300)

    # Sidebar Footer - Dataset Limitation
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**⚠️ Dataset Limitations**\n\n"
        "This data is based on CWA Dataset `F-A0010-001` (36-Hour Agricultural Weather Forecast).\n"
        "It provides **forecasts only** (future 36 hours) and does **not** contain historical observation data (Yesterday/Past)."
    )
    
if __name__ == "__main__":
    main()
