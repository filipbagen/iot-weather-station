from machine import Pin
from time import sleep
import dht

# LED Blinking
RED = Pin(0, Pin.OUT)
YELLOW = Pin(1, Pin.OUT)
GREEN = Pin(2, Pin.OUT)

while True:
    RED.on()
    sleep(0.5)
    RED.off()
    YELLOW.on()
    sleep(0.5)
    YELLOW.off()
    GREEN.on()
    sleep(0.5)
    GREEN.off()

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

import os
print(os.listdir())

import firebase_client
print("Import successful!")