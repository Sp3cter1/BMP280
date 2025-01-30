import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import time
import threading
import subprocess

def get_sensor_data():
    connection = sqlite3.connect('sensor_data.db')
    query = "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 10"  # Get the latest 10 readings
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# Function to start bmp280_pack.py script
def run_bmp280_pack():
    subprocess.run(['python3', 'bmp280_pack.py'])


st.set_page_config(page_title="Sensor Data Viewer", layout="wide")

st.title("Sensor Data - Temperature, Pressure, and Altitude")

# Placeholder for displaying data
data_placeholder = st.empty()

# Plot placeholder
plot_placeholder = st.empty()

# Start the BMP280 data collection script in a separate thread
thread = threading.Thread(target=run_bmp280_pack)
thread.daemon = True
thread.start()

# Loop to refresh data and update display
while True:
    # Get the latest sensor data
    df = get_sensor_data()

    # Display latest data in a table
    with data_placeholder.container():
        if df.empty:
            st.write("No data available.")
        else:
            st.subheader("Latest Sensor Readings")
            st.dataframe(df)  # Display data as a table

    # Plot temperature over time
    with plot_placeholder.container():
        if not df.empty:
            st.subheader("Temperature Over Time")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df['timestamp'], df['temperature'], marker='o', linestyle='-', color='tab:red')
            ax.set_xlabel("Time")
            ax.set_ylabel("Temperature (°C)")
            ax.set_title("Temperature Trend")
            st.pyplot(fig)

    # Sleep for 10 seconds before updating again
    time.sleep(10)
