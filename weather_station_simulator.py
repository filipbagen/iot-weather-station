"""
Weather Station Simulator for testing Firebase integration on Mac/PC
This simulates the MicroPython hardware modules and generates fake sensor data
"""

import json
import time
import random
from firebase_client import FirebaseClient

# Simulate MicroPython modules


class MockPin:
    OUT = 1

    def __init__(self, pin, mode):
        self.pin = pin
        self.mode = mode
        self._value = 0

    def on(self):
        self._value = 1
        print(f"🔴 LED {self.pin} turned ON")

    def off(self):
        self._value = 0
        print(f"⚫ LED {self.pin} turned OFF")

    def value(self):
        return self._value


class MockADC:
    def __init__(self, pin):
        self.pin = pin

    def read_u16(self):
        # Simulate light sensor readings (0-65535)
        return random.randint(200, 800)


class MockDHT:
    def __init__(self, pin):
        self.pin = pin
        self._temp = 20
        self._humidity = 50

    def measure(self):
        # Simulate temperature fluctuation
        self._temp = random.uniform(15, 30)
        self._humidity = random.uniform(30, 80)

    def temperature(self):
        return round(self._temp, 1)

    def humidity(self):
        return round(self._humidity, 1)


# Hardware setup (simulated)
led = MockPin(0, MockPin.OUT)
dht_sensor = MockDHT(14)
light_sensor = MockADC(26)

# Firebase setup
firebase = FirebaseClient()


def get_light_level(raw_value):
    """Convert raw ADC reading to descriptive light level"""
    if raw_value < 300:
        return "Very Dark"
    elif raw_value < 400:
        return "Dark"
    elif raw_value < 500:
        return "Dim"
    elif raw_value < 600:
        return "Light"
    elif raw_value < 700:
        return "Bright"
    else:
        return "Very Bright"


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


def get_outfit_recommendation(temp, humidity, light_level):
    """Recommend outfit based on weather conditions"""
    outfit = []

    # Base clothing
    if temp < 5:
        outfit.append("Heavy coat, warm layers")
    elif temp < 15:
        outfit.append("Jacket or sweater")
    elif temp < 25:
        outfit.append("Light jacket or long sleeves")
    else:
        outfit.append("T-shirt or light clothing")

    # Humidity considerations
    if humidity > 70:
        outfit.append("breathable fabric")

    # Light considerations
    if light_level in ["Bright", "Very Bright"]:
        outfit.append("sunglasses")

    return ", ".join(outfit)


def collect_sensor_data():
    """Collect data from all sensors (simulated)"""
    try:
        # Read DHT11 sensor (simulated)
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        # Read light sensor (simulated)
        light_raw = light_sensor.read_u16()
        light_level = get_light_level(light_raw)

        # Get weather description
        weather = get_weather_description(temperature, humidity)

        # Get outfit recommendation
        outfit = get_outfit_recommendation(temperature, humidity, light_level)

        # Create data structure (ready for Firebase)
        data = {
            "timestamp": time.time(),
            "temperature": temperature,
            "humidity": humidity,
            "light_raw": light_raw,
            "light_level": light_level,
            "weather_condition": weather,
            "outfit_recommendation": outfit,
            "device": "simulator"  # Mark as simulated data
        }

        # LED indicator based on temperature
        if temperature > 26:
            led.on()
        else:
            led.off()

        return data

    except Exception as e:
        print(f"Sensor error: {e}")
        return None


def display_data(data):
    """Display formatted sensor data"""
    if data is None:
        print("❌ Failed to read sensors")
        return

    print("\n" + "="*50)
    print("🌡️  WEATHER STATION SIMULATOR")
    print("="*50)
    print(f"🌡️  Temperature: {data['temperature']}°C")
    print(f"💧 Humidity: {data['humidity']}%")
    print(f"☀️  Light Level: {data['light_level']} ({data['light_raw']})")
    print(f"⛅ Weather: {data['weather_condition']}")
    print(f"👕 Outfit: {data['outfit_recommendation']}")
    print(f"🔴 LED Status: {'ON' if led.value() else 'OFF'}")
    print(f"⏰ Timestamp: {data['timestamp']}")
    print("="*50)

    # Also print JSON format (ready for Firebase)
    print("\n📡 JSON Data (Firebase format):")
    print(json.dumps(data))


def upload_to_firebase(data):
    """Upload sensor data to Firebase Realtime Database"""
    if data is None:
        print("❌ No data to upload")
        return False

    try:
        print("🔥 Uploading to Firebase...")
        success, message = firebase.push("weather_readings", data)

        if success:
            print("✅ Data uploaded successfully!")
            return True
        else:
            print(f"❌ Upload failed: {message}")
            return False

    except Exception as e:
        print(f"❌ Firebase upload error: {e}")
        return False


def upload_latest_reading(data):
    """Upload the latest reading to a specific 'latest' path for easy access"""
    if data is None:
        return False

    try:
        success, message = firebase.set("latest_reading", data)
        if success:
            print("📍 Latest reading updated")
            return True
        else:
            print(f"❌ Latest reading update failed: {message}")
            return False
    except Exception as e:
        print(f"❌ Latest reading error: {e}")
        return False


def main():
    """Main loop - collect and upload data every 10 seconds (faster for testing)"""
    print("🚀 Weather Station Simulator Starting...")
    print("🔥 Firebase integration enabled")
    print("📊 Collecting and uploading simulated data every 10 seconds...")
    print("💡 This is a SIMULATOR - data is randomly generated for testing")

    reading_count = 0

    while True:
        try:
            reading_count += 1
            print(f"\n🔢 Reading #{reading_count}")

            # Collect sensor data
            sensor_data = collect_sensor_data()

            # Display data locally
            display_data(sensor_data)

            if sensor_data:
                # Upload to Firebase (all readings)
                upload_success = upload_to_firebase(sensor_data)

                # Also update the latest reading
                upload_latest_reading(sensor_data)

                if upload_success:
                    print("🎉 Data successfully uploaded to Firebase!")
                else:
                    print("⚠️ Upload failed - data displayed locally only")

            # Wait 10 seconds before next reading (faster for testing)
            print("⏱️ Waiting 10 seconds until next reading...")
            print("Press Ctrl+C to stop")
            time.sleep(10)

        except KeyboardInterrupt:
            print("\n🛑 Weather Station Simulator Stopped")
            led.off()
            print(f"📊 Total readings taken: {reading_count}")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)


# Run the weather station simulator
if __name__ == "__main__":
    main()
