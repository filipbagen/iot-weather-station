import json
import time
import random
from firebase_client import FirebaseClient

# Simulate hardware with mock classes


class MockPin:
    def __init__(self, pin, mode):
        self.pin = pin
        self.mode = mode
        self._value = 0

    def on(self):
        self._value = 1
        print(f"💡 LED {self.pin} ON")

    def off(self):
        self._value = 0
        print(f"💡 LED {self.pin} OFF")

    def value(self):
        return self._value


class MockDHT:
    def __init__(self, pin):
        self.pin = pin

    def measure(self):
        pass  # Simulate measurement

    def temperature(self):
        return random.randint(15, 30)  # Random temp between 15-30°C

    def humidity(self):
        return random.randint(40, 80)  # Random humidity 40-80%


class MockADC:
    def __init__(self, pin):
        self.pin = pin

    def read_u16(self):
        return random.randint(200, 800)  # Random light sensor value


# Mock hardware setup
RED = MockPin(0, "OUT")                # Red LED for bad weather
YELLOW = MockPin(1, "OUT")             # Yellow LED for okay weather
GREEN = MockPin(2, "OUT")              # Green LED for nice weather
dht_sensor = MockDHT(14)               # Mock DHT11
light_sensor = MockADC(26)             # Mock photoresistor

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


def get_weather_quality(temp, humidity):
    """Determine if weather is nice, okay, or bad"""
    # Bad weather conditions
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
    """Collect data from all sensors"""
    try:
        # Read DHT11 sensor (simulated)
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        # Read light sensor (simulated)
        light_raw = light_sensor.read_u16()
        light_level = get_light_level(light_raw)

        # Get weather description and quality
        weather = get_weather_description(temperature, humidity)
        weather_quality = get_weather_quality(temperature, humidity)

        # Get outfit recommendation
        outfit = get_outfit_recommendation(temperature, humidity, light_level)

        # Set LED indicators based on weather quality
        set_weather_leds(weather_quality)

        # Create data structure (ready for Firebase)
        data = {
            "timestamp": time.time(),
            "temperature": temperature,
            "humidity": humidity,
            "light_raw": light_raw,
            "light_level": light_level,
            "weather_condition": weather,
            "weather_quality": weather_quality,
            "outfit_recommendation": outfit
        }

        return data

    except Exception as e:
        print(f"Sensor error: {e}")
        return None


def get_led_status():
    """Get current LED status for display"""
    if RED.value():
        return "🔴 RED (Bad Weather)"
    elif YELLOW.value():
        return "🟡 YELLOW (Okay Weather)"
    elif GREEN.value():
        return "🟢 GREEN (Nice Weather)"
    else:
        return "⚫ OFF"


def display_data(data):
    """Display formatted sensor data"""
    if data is None:
        print("❌ Failed to read sensors")
        return

    print("\n" + "="*50)
    print("🌡️  WEATHER STATION DATA (SIMULATION)")
    print("="*50)
    print(f"🌡️  Temperature: {data['temperature']}°C")
    print(f"💧 Humidity: {data['humidity']}%")
    print(f"☀️  Light Level: {data['light_level']} ({data['light_raw']})")
    print(f"⛅ Weather: {data['weather_condition']}")
    print(f"📊 Weather Quality: {data['weather_quality'].upper()}")
    print(f"👕 Outfit: {data['outfit_recommendation']}")
    print(f"💡 LED Status: {get_led_status()}")
    print(f"⏰ Timestamp: {data['timestamp']}")
    print("="*50)


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
    print("💡 LED Weather Indicators: 🟢 Nice | 🟡 Okay | 🔴 Bad")
    print("📊 Collecting and uploading simulated data every 10 seconds...")
    print("Press Ctrl+C to stop\n")

    reading_count = 0

    while True:
        try:
            reading_count += 1
            print(f"\n📊 Reading #{reading_count}")

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
            time.sleep(10)

        except KeyboardInterrupt:
            print("\n🛑 Weather Station Simulator Stopped")
            # Turn off all LEDs
            RED.off()
            YELLOW.off()
            GREEN.off()
            print(f"📊 Total readings taken: {reading_count}")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)


# Run the weather station simulator
if __name__ == "__main__":
    main()
