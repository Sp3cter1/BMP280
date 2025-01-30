from time import sleep
from smbus import SMBus
from bmp280 import BMP280
from datetime import datetime
import sqlite3

# Database setup
def create_table():
    connection = sqlite3.connect('sensor_data.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sensor_readings (
                        timestamp TEXT,
                        temperature REAL,
                        pressure REAL,
                        altitude REAL)''')
    connection.commit()
    connection.close()

def insert_data(timestamp, temperature, pressure, altitude):
    connection = sqlite3.connect('sensor_data.db')
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO sensor_readings (timestamp, temperature, pressure, altitude)
                      VALUES (?, ?, ?, ?)''', (timestamp, temperature, pressure, altitude))
    connection.commit()
    connection.close()

# Initialize the BMP280
bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus, i2c_addr=0x77)

# Create the database table if it doesn't exist
create_table()

while True:
    # Get temperature and pressure
    temperature = bmp280.get_temperature()
    pressure = bmp280.get_pressure()
    
    # Calculate altitude
    P0 = 101325  # Sea level pressure in Pa (adjust based on location)
    altitude = 44330 * (1 - (pressure / P0) ** (1 / 5.255))

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print the output with timestamp
    print(f"{timestamp} - Temperature: {temperature:.2f} °C")
    print(f"{timestamp} - Pressure: {pressure:.2f} Pa")
    print(f"{timestamp} - Altitude: {altitude:.2f} meters")
    
    # Insert the data into the database
    insert_data(timestamp, temperature, pressure, altitude)

    # Sleep for 1 second
    sleep(1)
