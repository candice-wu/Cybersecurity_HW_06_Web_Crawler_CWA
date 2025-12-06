import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

DB_NAME = "data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def get_locations():
    conn = get_db_connection()
    try:
        df = pd.read_sql("SELECT DISTINCT location FROM weather", conn)
        conn.close()
        return df['location'].tolist()
    except Exception as e:
        conn.close()
        return []

def get_forecast_by_location(location):
    conn = get_db_connection()
    # Query matching the new schema
    query = """
        SELECT id, forecast_date, description, max_temp, min_temp
        FROM weather
        WHERE location = ?
        ORDER BY forecast_date ASC
    """
    df = pd.read_sql(query, conn, params=(location,))
    conn.close()
    return df

st.set_page_config(page_title="Taiwan Agriculture Weather Forecast", layout="wide")

st.title("🌾 Taiwan Agricultural Weather Forecast")
st.markdown("Data Source: CWA Open Data API (F-A0010-001)")

# Sidebar for selection
st.sidebar.header("Settings")
locations = get_locations()

if not locations:
    st.error("No data found in database (data.db). Please run fetch_data.py first.")
else:
    selected_location = st.sidebar.selectbox("Select Region", locations)

    if selected_location:
        st.header(f"Forecast for {selected_location}")
        
        df = get_forecast_by_location(selected_location)
        
        if not df.empty:
            # 1. Visualization (Line Chart for Temp)
            st.subheader("Temperature Trend (Next 7 Days)")
            
            # Melt dataframe for better chart plotting (Max/Min temp together)
            df_melt = df.melt('forecast_date', value_vars=['max_temp', 'min_temp'], var_name='Type', value_name='Temperature')
            
            # Custom colors: Max Temp -> #DD6D6A, Min Temp -> SteelBlue (default-ish)
            chart = alt.Chart(df_melt).mark_line(point=True).encode(
                x='forecast_date',
                y=alt.Y('Temperature', scale=alt.Scale(domain=[10, 40])),
                color=alt.Color('Type', scale=alt.Scale(domain=['max_temp', 'min_temp'], range=['#DD6D6A', '#4682B4'])),
                tooltip=['forecast_date', 'Type', 'Temperature']
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)

            # 2. Detailed Data Table
            st.subheader("Detailed Forecast")
            # Rename columns for display if needed
            display_df = df.rename(columns={
                'id': 'ID',
                'forecast_date': '日期 Date',
                'description': '天氣描述 Description',
                'max_temp': '最高溫 Max Temp (°C)',
                'min_temp': '最低溫 Min Temp (°C)'
            })
            # Reorder columns: ID, Date, Max, Min, Description
            display_df = display_df[['ID', '日期 Date', '最高溫 Max Temp (°C)', '最低溫 Min Temp (°C)', '天氣描述 Description']]
            # Hide index by not displaying it (Streamlit dataframe handles this, usually index is separate)
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No forecast data available for this region.")
