import sqlite3
import time
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json
import serial
import re

app = FastAPI()

# Configure the serial connection (adjust COM port and baud rate as needed)
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)
time.sleep(2)  # Wait for the connection to initialize

# SQLite Database Setup
DATABASE = 'environment_data.db'

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

# Create table for storing data (if not already created)
def create_table():
    conn = get_db_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS data (
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperature REAL,
                humidity REAL,
                airQuality REAL
            )''')
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
        finally:
            conn.close()

create_table()

# Insert data into the database
def insert_data(temperature, humidity, air_quality):
    conn = get_db_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute("INSERT INTO data (temperature, humidity, airQuality) VALUES (?, ?, ?)",
                      (temperature, humidity, air_quality))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

# Extract the value from the raw data string
def extract_value(raw_data, sensor_type):
    try:
        match = re.search(rf"{sensor_type}:\s*(\d+\.?\d*)", raw_data)
        if match:
            value = match.group(1)
            # Ensure the value is a valid float before returning
            try:
                return float(value)
            except ValueError:
                print(f"Invalid {sensor_type} value: {value}")
                return None
        else:
            print(f"{sensor_type} value not found in raw data: {raw_data}")
            return None
    except Exception as e:
        print(f"Error extracting {sensor_type} value: {e}")
        return None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            # Read data from the Arduino
            raw_data = arduino.readline().decode('utf-8').strip()
            if raw_data:
                print(f"Received raw data: {raw_data}")

                temperature = extract_value(raw_data, "Temp")
                humidity = extract_value(raw_data, "Humidity")
                air_quality = extract_value(raw_data, "Air Quality")

                if temperature is not None and humidity is not None and air_quality is not None:
                    # Insert the data into the database
                    insert_data(temperature, humidity, air_quality)

                    # Send live data to the front-end
                    data = {
                        "temperature": temperature,
                        "humidity": humidity,
                        "airQuality": air_quality
                    }
                    await websocket.send_text(json.dumps(data))

        except Exception as e:
            print(f"Error in WebSocket: {e}")
            break

@app.get("/", response_class=HTMLResponse)
async def get_page():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Environment Monitoring</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
    body {
        font-family: 'Poppins', sans-serif;
        margin: 0;
        padding: 0;
        background: linear-gradient(135deg, #4e73df, #2a5298);
        color: #fff;
        display: flex;
        justify-content: center;
        align-items: flex-start;
        height: 100vh;
        overflow-y: auto;
        box-sizing: border-box;
    }
    h1 {
        font-size: 3.5rem;
        text-align: center;
        margin-bottom: 40px;
        letter-spacing: 2px;
        text-shadow: 2px 2px 15px rgba(0, 0, 0, 0.5);
        color: #fff;
    }
    .container {
        width: 100%;
        max-width: 1200px;
        text-align: center;
        margin-top: 20px;
        padding-bottom: 40px;
    }
    .data-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); /* Keep small live data boxes */
        gap: 30px;
        margin-top: 40px;
    }
    .data-box {
        background: rgba(255, 255, 255, 0.15);
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.3);
    }
    .data-box h2 {
        font-size: 2.5rem;
        margin: 0;
        font-weight: 600;
    }
    .data-box .value {
        font-size: 2.5rem;
        margin-top: 10px;
        font-weight: 600;
    }
    /* Make the chart containers bigger and place them under the live data boxes */
    .chart-container {
        width: 85%; /* Ensure full width */
        margin-top: 30px;
        text-align: center;
    }
    canvas {
        width: 85% !important; /* Ensure full width */
        height: 400px !important; /* Adjust height for better visibility */
    }
</style>


</head>
<div class="container">
    <h1>Environment Monitoring Dashboard</h1>
    <div class="data-container">
        <div class="data-box">
            <h2>Temperature</h2>
            <p>Current Temperature</p>
            <div class="value" id="temperature">Loading...</div>
        </div>
        <div class="data-box">
            <h2>Humidity</h2>
            <p>Current Humidity</p>
            <div class="value" id="humidity">Loading...</div>
        </div>
        <div class="data-box">
            <h2>Air Quality</h2>
            <p>Current Air Quality</p>
            <div class="value" id="airQuality">Loading...</div>
            <p>Calculated in percentage instead of AQI 1% ≈ AQI 5-10</p>
        </div>
    </div>

    <h2>Live Data Charts</h2>
    <div class="chart-container">
        <canvas id="temperatureChart"></canvas>
    </div>
    <div class="chart-container">
        <canvas id="humidityChart"></canvas>
    </div>
    <div class="chart-container">
        <canvas id="airQualityChart"></canvas>
    </div>
</div>


    <script>
        const ws = new WebSocket("ws://localhost:8000/ws");

        // Set up charts
        const temperatureData = {
            labels: [],
            datasets: [{
                label: 'Temperature (°C)',
                data: [],
                borderColor: 'rgba(75, 192, 192, 1)',
                fill: false,
                tension: 0.1
            }]
        };
        const humidityData = {
            labels: [],
            datasets: [{
                label: 'Humidity (%)',
                data: [],
                borderColor: 'rgba(54, 162, 235, 1)',
                fill: false,
                tension: 0.1
            }]
        };
        const airQualityData = {
            labels: [],
            datasets: [{
                label: 'Air Quality (%)',
                data: [],
                borderColor: 'rgba(153, 102, 255, 1)',
                fill: false,
                tension: 0.1
            }]
        };

        const temperatureChart = new Chart(document.getElementById('temperatureChart'), {
            type: 'line',
            data: temperatureData,
            options: {
                responsive: true,
                scales: {
                    x: { type: 'linear', position: 'bottom' }
                }
            }
        });

        const humidityChart = new Chart(document.getElementById('humidityChart'), {
            type: 'line',
            data: humidityData,
            options: {
                responsive: true,
                scales: {
                    x: { type: 'linear', position: 'bottom' }
                }
            }
        });

        const airQualityChart = new Chart(document.getElementById('airQualityChart'), {
            type: 'line',
            data: airQualityData,
            options: {
                responsive: true,
                scales: {
                    x: { type: 'linear', position: 'bottom' }
                }
            }
        });

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);

            // Update live data
            document.getElementById("temperature").innerText = data.temperature + " °C";
            document.getElementById("humidity").innerText = data.humidity + " %";
            document.getElementById("airQuality").innerText = data.airQuality + " %";

            // Add new data to charts
            const currentTime = Date.now();
            temperatureData.labels.push(currentTime);
            temperatureData.datasets[0].data.push(data.temperature);

            humidityData.labels.push(currentTime);
            humidityData.datasets[0].data.push(data.humidity);

            airQualityData.labels.push(currentTime);
            airQualityData.datasets[0].data.push(data.airQuality);

            // Update charts
            temperatureChart.update();
            humidityChart.update();
            airQualityChart.update();
        };
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/historical_data")
async def get_historical_data():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT timestamp, temperature, humidity, airQuality FROM data ORDER BY timestamp ASC")
    rows = c.fetchall()
    conn.close()

    # Prepare data for the chart
    data = [{"timestamp": row[0], "temperature": row[1], "humidity": row[2], "airQuality": row[3]} for row in rows]
    return {"data": data}
