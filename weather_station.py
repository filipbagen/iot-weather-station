import json
import time
from machine import Pin, ADC
import dht
from firebase_client import FirebaseClient

# Hardware setup - LED indicators for weather quality
RED = Pin(0, Pin.OUT)                # Red LED for bad weather
YELLOW = Pin(1, Pin.OUT)             # Yellow LED for okay weather
GREEN = Pin(2, Pin.OUT)              # Green LED for nice weather
dht_sensor = dht.DHT11(Pin(14))      # DHT11 on GPIO 14
light_sensor = ADC(Pin(26))          # Photoresistor on GPIO 26 (ADC0)

# Firebase setup
firebase = FirebaseClient()


def get_light_level(raw_value):
    """Convert raw ADC reading to descriptive light level"""
    if raw_value > 50000:
        return "Very Bright"
    elif raw_value > 30000:
        return "Bright"
    elif raw_value > 15000:
        return "Dim"
    elif raw_value > 5000:
        return "Dark"
    else:
        return "Very Dark"


def get_weather_description(temp, humidity):
    """Determine weather conditions based on temperature and humidity"""
    if temp < 5:
        return "Very Cold"
    elif temp < 15:
        return "Cold"
    elif temp < 25:
        return "Mild"
    elif temp < 30:
        return "Warm"
    else:
        return "Hot"


def get_weather_quality(temp, humidity):
    """Determine if weather is nice, okay, or bad"""
    if temp < 5 or temp > 35:  # Too cold or too hot
        return "bad"
    elif humidity > 80:  # Too humid
        return "bad"
    elif temp < 10 or temp > 30:  # Somewhat uncomfortable
        return "okay"
    elif humidity > 70:  # Somewhat humid
        return "okay"
    else:  # Comfortable temperature and humidity
        return "nice"


def set_weather_leds(weather_quality):
    """Control LEDs based on weather quality"""
    # Turn off all LEDs first
    RED.off()
    YELLOW.off()
    GREEN.off()

    # Turn on appropriate LED
    if weather_quality == "bad":
        RED.on()
    elif weather_quality == "okay":
        YELLOW.on()
    else:  # nice weather
        GREEN.on()


def collect_sensor_data():
    """Collect data from all sensors and format for Firebase"""
    try:
        # Read DHT11 sensor
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        # Read light sensor
        light_raw = light_sensor.read_u16()
        light_level = get_light_level(light_raw)

        # Get weather quality for LED control (not stored in data)
        weather_quality = get_weather_quality(temperature, humidity)

        # Set LED indicators based on weather quality
        set_weather_leds(weather_quality)

        # Create clean data structure for Firebase (only essential sensor data)
        data = {
            "timestamp": int(time.time()),
            "temperature": temperature,
            "humidity": humidity,
            "light_raw": light_raw,
            "light_level": light_level
        }

        return data

    except OSError as e:
        print(f"Sensor error: {e}")
        return None
    except Exception as e:
        print(f"Data collection error: {e}")
        return None


def get_led_status():
    """Get current LED status for display"""
    if RED.value():
        return "RED (Bad Weather)"
    elif YELLOW.value():
        return "YELLOW (Okay Weather)"
    elif GREEN.value():
        return "GREEN (Nice Weather)"
    else:
        return "OFF"


def display_data(data):
    """Display formatted sensor data"""
    if data is None:
        print("Failed to read sensors")
        return

    print("\n" + "="*50)
    print("WEATHER STATION DATA")
    print("="*50)
    print(f"Temperature: {data['temperature']}C")
    print(f"Humidity: {data['humidity']}%")
    print(f"Light Level: {data['light_level']} ({data['light_raw']})")
    print(f"LED Status: {get_led_status()}")
    print(f"Timestamp: {data['timestamp']}")
    print("="*50)


def upload_to_firebase(data):
    """Upload sensor data to Firebase Realtime Database"""
    if data is None:
        print("No data to upload")
        return False

    try:
        print("Uploading to Firebase...")
        success, message = firebase.push("weather_readings", data)

        if success:
            print("Data uploaded successfully!")
            return True
        else:
            print(f"Upload failed: {message}")
            return False

    except Exception as e:
        print(f"Firebase upload error: {e}")
        return False


def upload_latest_reading(data):
    """Upload the latest reading to Firebase for real-time access"""
    if data is None:
        return False

    try:
        success, message = firebase.set("latest_reading", data)
        if success:
            print("Latest reading updated")
            return True
        else:
            print(f"Latest reading update failed: {message}")
            return False
    except Exception as e:
        print(f"Latest reading error: {e}")
        return False


def main():
    """Main loop - collect and upload weather data every 30 seconds"""
    print("Weather Station Starting...")
    print("Hardware data collection mode")
    print("Firebase integration enabled")
    print("LED Weather Indicators: GREEN Nice | YELLOW Okay | RED Bad")
    print("Collecting and uploading data every 30 seconds...")

    reading_count = 0

    while True:
        try:
            reading_count += 1
            print(f"\n--- Reading #{reading_count} ---")

            # Collect sensor data
            sensor_data = collect_sensor_data()

            # Display data locally
            display_data(sensor_data)

            if sensor_data:
                # Upload to Firebase (historical data)
                upload_success = upload_to_firebase(sensor_data)

                # Update latest reading for real-time access
                upload_latest_reading(sensor_data)

                if upload_success:
                    print("Data successfully uploaded to Firebase!")
                else:
                    print("Upload failed - data displayed locally only")

            # Wait 30 seconds before next reading
            print("Waiting 30 seconds until next reading...")
            time.sleep(30)

        except KeyboardInterrupt:
            print("\nWeather Station Stopped")
            # Turn off all LEDs
            RED.off()
            YELLOW.off()
            GREEN.off()
            print(f"Total readings taken: {reading_count}")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)


# Run the weather station
if __name__ == "__main__":
    main()
