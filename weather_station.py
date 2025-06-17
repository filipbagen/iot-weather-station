import json
import time
from machine import Pin, ADC
import dht

# Hardware setup
led = Pin(0, Pin.OUT)                # LED for status indication
dht_sensor = dht.DHT11(Pin(14))      # DHT11 on GPIO 14
light_sensor = ADC(Pin(26))          # Photoresistor on GPIO 26 (ADC0)


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
    """Collect data from all sensors"""
    try:
        # Read DHT11 sensor
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        # Read light sensor
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
            "outfit_recommendation": outfit
        }

        # LED indicator based on temperature
        if temperature > 26:
            led.on()
        else:
            led.off()

        return data

    except OSError as e:
        print(f"Sensor error: {e}")
        return None


def display_data(data):
    """Display formatted sensor data"""
    if data is None:
        print("❌ Failed to read sensors")
        return

    print("\n" + "="*50)
    print("🌡️  WEATHER STATION DATA")
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


def main():
    """Main loop - collect and display data every 5 seconds"""
    print("🚀 Weather Station Starting...")
    print("📊 Collecting data every 5 seconds...")

    while True:
        try:
            # Collect sensor data
            sensor_data = collect_sensor_data()

            # Display data
            display_data(sensor_data)

            # Wait 5 seconds before next reading
            time.sleep(5)

        except KeyboardInterrupt:
            print("\n🛑 Weather Station Stopped")
            led.off()
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)


# Run the weather station
if __name__ == "__main__":
    main()
