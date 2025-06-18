from machine import ADC, Pin
import firebase_client
import os
import json
import time
from machine import Pin, ADC
import dht
from firebase_client import FirebaseClient

# Test script for IoT Weather Station
# This script tests all components individually and then together

print("="*60)
print("IoT WEATHER STATION COMPREHENSIVE TEST")
print("="*60)


def test_leds():
    """Test all three LEDs individually"""
    print("\n1. TESTING LEDs...")

    RED = Pin(0, Pin.OUT)
    YELLOW = Pin(1, Pin.OUT)
    GREEN = Pin(2, Pin.OUT)

    # Test each LED
    leds = [("RED", RED), ("YELLOW", YELLOW), ("GREEN", GREEN)]

    for name, led in leds:
        print(f"Testing {name} LED...")
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(0.5)

    # Test all together
    print("Testing all LEDs together...")
    for name, led in leds:
        led.on()
    time.sleep(2)
    for name, led in leds:
        led.off()

    print("LED test completed!")
    return RED, YELLOW, GREEN


def test_dht_sensor():
    """Test DHT11 temperature and humidity sensor"""
    print("\n2. TESTING DHT11 SENSOR...")

    dht_sensor = dht.DHT11(Pin(14))

    for i in range(3):  # Take 3 readings
        try:
            print(f"Reading {i+1}:")
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            humidity = dht_sensor.humidity()

            print(f"  Temperature: {temp}°C")
            print(f"  Humidity: {humidity}%")

            # Basic sanity checks
            if temp < -40 or temp > 80:
                print(f"  WARNING: Temperature {temp}°C seems unrealistic")
            if humidity < 0 or humidity > 100:
                print(f"  WARNING: Humidity {humidity}% is out of range")

            time.sleep(2)

        except Exception as e:
            print(f"  ERROR reading DHT11: {e}")

    print("DHT11 test completed!")
    return dht_sensor


def test_light_sensor():
    """Test photoresistor light sensor (LDR) using ADC readings"""
    print("\n3. TESTING LIGHT SENSOR...")

    light_sensor = ADC(Pin(26))  # ADC0 = GP26

    for i in range(5):  # Take 5 readings
        try:
            raw_value = light_sensor.read_u16()
            voltage = raw_value * 3.3 / 65535  # Optional: voltage conversion

            # Convert raw ADC value to descriptive level
            if raw_value > 50000:
                level = "Very Bright"
            elif raw_value > 30000:
                level = "Bright"
            elif raw_value > 15000:
                level = "Dim"
            elif raw_value > 5000:
                level = "Dark"
            else:
                level = "Very Dark"

            print(f"Reading {i+1}: {raw_value} (raw ADC value)")
            print(f"  Voltage: {voltage:.2f} V")
            print(f"  Light Level: {level}")
            time.sleep(1)

        except Exception as e:
            print(f"  ERROR reading light sensor: {e}")

    print("Light sensor test completed!")
    return light_sensor


def test_firebase_connection():
    """Test Firebase connectivity with small data"""
    print("\n4. TESTING FIREBASE CONNECTION...")

    firebase = FirebaseClient()

    # Test 1: Simple push
    test_data = {
        "test": True,
        "timestamp": time.time(),
        "message": "Test from weather station"
    }

    print("Testing Firebase push...")
    success, message = firebase.push("test_readings", test_data)
    if success:
        print("  Firebase push: SUCCESS")
    else:
        print(f"  Firebase push: FAILED - {message}")

    # Test 2: Set operation
    print("Testing Firebase set...")
    success, message = firebase.set(
        "test_latest", {"status": "testing", "time": time.time()})
    if success:
        print("  Firebase set: SUCCESS")
    else:
        print(f"  Firebase set: FAILED - {message}")

    print("Firebase test completed!")
    return firebase


def test_weather_logic():
    """Test weather quality logic with different scenarios"""
    print("\n5. TESTING WEATHER LOGIC...")

    def get_weather_quality(temp, humidity):
        if temp < 5 or temp > 35:
            return "bad"
        elif humidity > 80:
            return "bad"
        elif temp < 10 or temp > 30:
            return "okay"
        elif humidity > 70:
            return "okay"
        else:
            return "nice"

    # Test scenarios
    scenarios = [
        (0, 50, "bad"),      # Too cold
        (40, 50, "bad"),     # Too hot
        (20, 90, "bad"),     # Too humid
        (8, 60, "okay"),     # Cool
        (32, 60, "okay"),    # Hot
        (25, 75, "okay"),    # Humid
        (22, 55, "nice"),    # Perfect
    ]

    for temp, humidity, expected in scenarios:
        result = get_weather_quality(temp, humidity)
        status = "✓" if result == expected else "✗"
        print(f"  {temp}°C, {humidity}% -> {result} {status}")

    print("Weather logic test completed!")


def test_integrated_system():
    """Test the complete system with all components"""
    print("\n6. TESTING INTEGRATED SYSTEM...")

    # Initialize all components
    RED = Pin(0, Pin.OUT)
    YELLOW = Pin(1, Pin.OUT)
    GREEN = Pin(2, Pin.OUT)
    dht_sensor = dht.DHT11(Pin(14))
    light_sensor = ADC(Pin(26))
    firebase = FirebaseClient()

    def set_weather_leds(weather_quality):
        RED.off()
        YELLOW.off()
        GREEN.off()

        if weather_quality == "bad":
            RED.on()
        elif weather_quality == "okay":
            YELLOW.on()
        else:
            GREEN.on()

    def get_weather_quality(temp, humidity):
        if temp < 5 or temp > 35:
            return "bad"
        elif humidity > 80:
            return "bad"
        elif temp < 10 or temp > 30:
            return "okay"
        elif humidity > 70:
            return "okay"
        else:
            return "nice"

    try:
        # Collect real sensor data
        print("Reading sensors...")
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        light_raw = light_sensor.read_u16()

        # Determine weather quality
        weather_quality = get_weather_quality(temperature, humidity)

        # Set appropriate LED
        set_weather_leds(weather_quality)

        print("Sensor readings:")
        print(f"  Temperature: {temperature}°C")
        print(f"  Humidity: {humidity}%")
        print(f"  Light: {light_raw}")
        print(f"  Weather Quality: {weather_quality}")

        # Create minimal test data for Firebase
        minimal_data = {
            "temp": temperature,
            "humid": humidity,
            "light": light_raw,
            "quality": weather_quality,
            "time": time.time()
        }

        print("Testing Firebase upload with minimal data...")
        success, message = firebase.push("integrated_test", minimal_data)
        if success:
            print("  Integrated Firebase test: SUCCESS")
        else:
            print(f"  Integrated Firebase test: FAILED - {message}")

        # Keep LED on for 3 seconds to see result
        time.sleep(3)

        # Turn off all LEDs
        RED.off()
        YELLOW.off()
        GREEN.off()

    except Exception as e:
        print(f"  ERROR in integrated test: {e}")

    print("Integrated system test completed!")


def main():
    """Run all tests"""
    try:
        test_leds()
        test_dht_sensor()
        test_light_sensor()
        test_firebase_connection()
        test_weather_logic()
        test_integrated_system()

        print("\n" + "="*60)
        print("ALL TESTS COMPLETED!")
        print("Check the output above for any errors or warnings.")
        print("="*60)

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")


if __name__ == "__main__":
    main()

# # DHT Sensor
# sensor = dht.DHT11(Pin(14))

# while True:
#     sensor.measure()
#     humidity = sensor.humidity()
#     temperature = sensor.temperature()
#     print("Humidity: {}%".format(humidity))
#     print("Temperature: {}C".format(temperature))

#     if temperature > 26:
#         led.on()
#     else:
#         led.off()
#     print("LED is {}".format("ON" if led.value() else "OFF"))

#     sleep(2)


# from machine import ADC, Pin
# import time

# # Initialize ADC (Analog to Digital Converter)
# adc = ADC(Pin(26))  # GP26 is ADC0 on the Raspberry Pi Pico

# while True:
#     # Read the input on analog pin ADC0 (value between 0 and 65535)
#     value = adc.read_u16()  # Read the 16-bit ADC value directly

#     description = ""
#     # We'll have a few thresholds, qualitatively determined
#     if value < 655:
#         description = "Dark"
#     elif value < 13107:
#         description = "Dim"
#     elif value < 32768:
#         description = "Light"
#     elif value < 52429:
#         description = "Bright"
#     else:
#         description = "Very bright"

#     print(f"Analog reading: {value} - {description}")

#     time.sleep(0.5)  # delay for 500 milliseconds


# from machine import ADC, Pin
# import time

# # Connects to GP26 = ADC0
# ldr = ADC(Pin(26))

# while True:
#     light = ldr.read_u16()  # Returns a value from 0 (dark) to 65535 (bright)
#     print("Light level:", light)
#     time.sleep(1)

print(os.listdir())

print("Import successful!")
